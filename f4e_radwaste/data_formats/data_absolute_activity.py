from typing import Optional, List

import pandas as pd

from f4e_radwaste.constants import (
    KEY_TIME,
    KEY_VOXEL,
    KEY_CELL,
    KEY_ISOTOPE,
    KEY_ABSOLUTE_ACTIVITY,
)
from f4e_radwaste.data_formats.dataframe_validator import DataFrameValidator


class DataAbsoluteActivity(DataFrameValidator):
    EXPECTED_INDEX_NAMES = [
        KEY_TIME,
        KEY_VOXEL,
        KEY_CELL,
        KEY_ISOTOPE,
    ]
    EXPECTED_COLUMNS = [KEY_ABSOLUTE_ACTIVITY]

    def get_filtered_dataframe(
        self,
        decay_times: Optional[List[float]] = None,
        voxels: Optional[List[int]] = None,
        cells: Optional[List[int]] = None,
        isotopes: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        filters = {
            KEY_TIME: decay_times,
            KEY_VOXEL: voxels,
            KEY_CELL: cells,
            KEY_ISOTOPE: isotopes,
        }

        return super().get_filtered_dataframe(**filters)


# def get_value(self, time, voxel, cell, isotope):
#     return self._dataframe.loc[(time, voxel, cell, isotope)][KEY_ABSOLUTE_ACTIVITY]
