from typing import Optional, List

import pandas as pd

from f4e_radwaste.constants import KEY_VOXEL
from f4e_radwaste.data_formats.dataframe_validator import DataFrameValidator


class DataMeshActivity(DataFrameValidator):
    EXPECTED_INDEX_NAMES = [KEY_VOXEL]
    EXPECTED_COLUMNS = []

    def get_filtered_dataframe(
        self, voxels: Optional[List[int]] = None
    ) -> pd.DataFrame:
        filters = {KEY_VOXEL: voxels}

        return super().get_filtered_dataframe(**filters)
