from pathlib import Path
from typing import Optional, List, Dict

import pandas as pd

from f4e_radwaste.constants import KEY_VOXEL, KEY_MASS_GRAMS
from f4e_radwaste.data_formats.dataframe_validator import DataFrameValidator


class DataMeshActivity(DataFrameValidator):
    EXPECTED_INDEX_NAMES = [KEY_VOXEL]
    EXPECTED_COLUMNS = [KEY_MASS_GRAMS]

    def get_filtered_dataframe(
        self, voxels: Optional[List[int]] = None, isotopes: Optional[List[str]] = None
    ) -> pd.DataFrame:
        filters = {KEY_VOXEL: voxels}
        filtered_dataframe = super().get_filtered_dataframe(**filters)

        # Return only the columns with names that match the isotopes provided
        if isotopes is not None:
            matching_isotopes = filtered_dataframe.columns.intersection(isotopes)
            return filtered_dataframe[matching_isotopes]

        return filtered_dataframe

    def get_dataframe_with_added_columns(self, columns: Dict[str, pd.Series]):
        for column_name, series in columns.items():
            series.name = column_name

        dataframe = pd.concat([*columns.values(), self._dataframe], axis=1)
        dataframe.index.name = KEY_VOXEL

        return dataframe

    def to_csv(self, folder_path: Path, file_name: str):
        self._dataframe.to_csv(folder_path / f"{file_name}.csv")
