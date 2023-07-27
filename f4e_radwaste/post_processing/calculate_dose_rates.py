from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import pandas as pd

from f4e_radwaste.constants import (
    KEY_DOSE_1_METER,
    KEY_CDR,
)
from f4e_radwaste.data_formats.data_mesh_activity import DataMeshActivity


@dataclass
class DoseCalculator:
    dose_1_m_factors: pd.Series
    cdr_factors: pd.DataFrame
    element_mix_by_material_id: Dict[int, pd.Series]

    def __post_init__(self):
        df = pd.read_csv(
            Path(__file__).parents[1] / r"resources/concrete_M200_cdr_factors.csv",
            index_col=0,
        )
        self.concrete_cdr_factors: pd.Series = df["0"]

    def calculate_doses(
        self, comp_activity: DataMeshActivity, cdr_factor_columns: List[pd.Series]
    ) -> DataMeshActivity:
        activity_df = comp_activity.get_filtered_dataframe()

        dose_1m_column = (activity_df * self.dose_1_m_factors).sum(axis=1)

        cdr_column = self._calculate_cdr_values(activity_df, cdr_factor_columns)

        updated_df = comp_activity.get_dataframe_with_added_columns(
            {KEY_DOSE_1_METER: dose_1m_column, KEY_CDR: cdr_column}
        )
        return DataMeshActivity(updated_df)

    @staticmethod
    def _calculate_cdr_values(
        activity_df: pd.DataFrame, cdr_factor_columns: List[pd.Series]
    ) -> pd.Series:
        cdr_values = []

        for (_, row), cdr_factors in zip(activity_df.iterrows(), cdr_factor_columns):
            cdr_values.append((row * cdr_factors).sum())

        return pd.Series(index=activity_df.index, data=cdr_values)

    def calculate_doses_in_concrete(
        self, comp_activity: DataMeshActivity
    ) -> DataMeshActivity:
        cdr_factor_columns = [self.concrete_cdr_factors] * comp_activity.n_rows

        return self.calculate_doses(comp_activity, cdr_factor_columns)

    def calculate_cdr_factors_list(
        self, material_id_proportions: List[pd.Series]
    ) -> List[pd.Series]:
        element_mixes = self._calculate_element_mixes(material_id_proportions)

        cdr_factors = []
        for element_mix in element_mixes:
            cdr_factors.append((self.cdr_factors * element_mix).sum(axis=1))

        return cdr_factors

    def _calculate_element_mixes(self, material_id_proportions: List[pd.Series]):
        element_mixes = []

        for mat_id_proportion in material_id_proportions:
            proportioned_mixes = []

            for mat_id, proportion in mat_id_proportion.items():
                if mat_id not in self.element_mix_by_material_id:
                    continue

                # noinspection PyTypeChecker
                proportioned_mixes.append(
                    self.element_mix_by_material_id[mat_id] * proportion
                )

            if len(proportioned_mixes) == 0:
                element_mixes.append(pd.Series())
                continue

            element_mix = pd.concat(proportioned_mixes, axis=1)
            element_mix = element_mix.sum(axis=1)
            element_mixes.append(element_mix)

        return element_mixes
