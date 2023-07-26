from typing import Optional, List

import numpy as np
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

    @property
    def decay_times(self) -> np.ndarray:
        return self._dataframe.index.unique(level=KEY_TIME).values

    @decay_times.setter
    def decay_times(self, decay_time_names):
        self._dataframe.index = self._dataframe.index.set_levels(
            decay_time_names, level=KEY_TIME
        )
