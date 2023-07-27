from typing import List, Optional

import pandas as pd

from f4e_radwaste.constants import (
    KEY_ISOTOPE,
    KEY_TFA_DECLARATION,
    KEY_TFA_CLASS,
    KEY_LMA,
    KEY_CSA_DECLARATION,
    KEY_HALF_LIFE,
    KEY_LDF_DECLARATION,
)
from f4e_radwaste.data_formats.dataframe_validator import DataFrameValidator


class DataIsotopeCriteria(DataFrameValidator):
    EXPECTED_INDEX_NAMES = [KEY_ISOTOPE]

    EXPECTED_COLUMNS = [
        KEY_HALF_LIFE,
        KEY_CSA_DECLARATION,
        KEY_LMA,
        KEY_TFA_CLASS,
        KEY_TFA_DECLARATION,
        KEY_LDF_DECLARATION,
    ]

    def __init__(self, dataframe: pd.DataFrame):
        super().__init__(dataframe)
        self._dataframe = self._dataframe.sort_index()
        self.all_isotopes_names = self._get_all_isotopes_names()
        self.relevant_isotopes_names = self._get_relevant_isotopes_names()

    def get_filtered_dataframe(
        self,
        isotopes: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        filters = {KEY_ISOTOPE: isotopes}

        return super().get_filtered_dataframe(**filters)

    def _get_all_isotopes_names(self) -> List[str]:
        return list(self._dataframe.index.values)

    def _get_relevant_isotopes_names(self) -> List[str]:
        mask = self._dataframe[KEY_TFA_CLASS] > 0
        return list(self._dataframe[mask].index.values)

    @property
    def tfa_class(self) -> pd.Series:
        return self._dataframe[KEY_TFA_CLASS]

    @property
    def lma(self) -> pd.Series:
        return self._dataframe[KEY_LMA]
