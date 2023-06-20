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

    def get_filtered_dataframe(
        self,
        isotopes: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        filters = {KEY_ISOTOPE: isotopes}

        return super().get_filtered_dataframe(**filters)
