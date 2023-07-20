from dataclasses import dataclass
from typing import Dict

import pandas as pd

from f4e_radwaste.constants import KEY_DOSE_1_METER, KEY_CDR
from f4e_radwaste.data_formats.data_mesh_activity import DataMeshActivity


@dataclass
class DoseCalculator:
    dose_1_m_factors: pd.Series
    cdr_factors: pd.DataFrame
    material_mixes_by_id: Dict[int, pd.Series]

    def calculate_doses(
        self,
        data_mesh_activity: DataMeshActivity,
        material_proportion: Dict[int, float],
    ) -> DataMeshActivity:
        activity_df = data_mesh_activity.get_filtered_dataframe()

        dose_1m_column = (activity_df * self.dose_1_m_factors).sum(axis=1)

        cdr_column = self._calculate_cdr_column(activity_df, material_proportion)

        updated_df = data_mesh_activity.get_dataframe_with_added_columns(
            {KEY_DOSE_1_METER: dose_1m_column, KEY_CDR: cdr_column}
        )
        return DataMeshActivity(updated_df)

    def _calculate_cdr_column(self, activity_df, material_proportion) -> pd.Series:
        element_mix = self._calculate_element_mix_from_material_id_proportion(
            material_proportion
        )
        cdr_factors_mix = self._calculate_cdr_factors_for_element_mix(element_mix)

        return (activity_df * cdr_factors_mix).sum(axis=1)

    def _calculate_element_mix_from_material_id_proportion(
        self, materials_proportion: Dict[int, float]
    ) -> pd.Series:
        proportioned_mixes = []

        material_ids = materials_proportion.keys()
        for material_id in material_ids:
            material_mix = self.material_mixes_by_id[material_id]
            proportion = materials_proportion[material_id]

            proportioned_mixes.append(material_mix * proportion)

        element_mix = pd.concat(proportioned_mixes, axis=1)
        element_mix = element_mix.sum(axis=1)
        return element_mix

    def _calculate_cdr_factors_for_element_mix(
        self, element_mix: pd.Series
    ) -> pd.Series:
        return (self.cdr_factors * element_mix).sum(axis=1)
