from typing import List

from f4e_radwaste.constants import (
    KEY_RADWASTE_CLASS,
    get_radwaste_class_str_from_int,
    KEY_MASS_GRAMS,
    KEY_IRAS, KEY_RELEVANT_SPECIFIC_ACTIVITY, KEY_TOTAL_SPECIFIC_ACTIVITY,
)
from f4e_radwaste.data_formats.data_isotope_criteria import DataIsotopeCriteria
from f4e_radwaste.data_formats.data_mesh_activity import DataMeshActivity


class CollapsedData:
    def __init__(self, package_activity: DataMeshActivity):
        self.dataframe = package_activity.get_filtered_dataframe()

    def get_radwaste_class_str(self) -> str:
        return get_radwaste_class_str_from_int(
            self.dataframe[KEY_RADWASTE_CLASS].values[0]
        )

    def get_mass(self) -> float:
        return self.dataframe[KEY_MASS_GRAMS].values[0]

    def get_iras(self) -> float:
        return self.dataframe[KEY_IRAS].values[0]

    def get_isotopes_exceeding_lma(
        self, isotope_criteria: DataIsotopeCriteria
    ) -> List[str]:
        lma_exceeded_mask = self.dataframe.ge(isotope_criteria.lma).transpose()
        column_name = lma_exceeded_mask.columns[0]
        return lma_exceeded_mask[lma_exceeded_mask[column_name]].index.values.tolist()

    def get_relevant_activity(self) -> float:
        return self.dataframe[KEY_RELEVANT_SPECIFIC_ACTIVITY].values[0]

    def get_total_activity(self) -> float:
        return self.dataframe[KEY_TOTAL_SPECIFIC_ACTIVITY].values[0]
