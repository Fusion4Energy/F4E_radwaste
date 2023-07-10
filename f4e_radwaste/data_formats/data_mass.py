from typing import Optional, List, Tuple

import numpy as np
import pandas as pd

from f4e_radwaste.constants import KEY_MASS_GRAMS, KEY_CELL, KEY_MATERIAL, KEY_VOXEL
from f4e_radwaste.data_formats.dataframe_validator import DataFrameValidator


class DataMass(DataFrameValidator):
    EXPECTED_INDEX_NAMES = [
        KEY_VOXEL,
        KEY_MATERIAL,
        KEY_CELL,
    ]
    EXPECTED_COLUMNS = [KEY_MASS_GRAMS]

    def get_filtered_dataframe(
        self,
        voxels: Optional[List[int]] = None,
        materials: Optional[List[int]] = None,
        cells: Optional[List[int]] = None,
    ) -> pd.DataFrame:
        filters = {
            KEY_VOXEL: voxels,
            KEY_MATERIAL: materials,
            KEY_CELL: cells,
        }

        return super().get_filtered_dataframe(**filters)

    def get_cells_and_masses_from_materials(
        self, materials: List
    ) -> Tuple[List[int], pd.DataFrame]:
        filtered_dataframe = self.get_filtered_dataframe(materials=materials)
        cells = filtered_dataframe.index.unique(level=KEY_CELL).values
        voxel_masses = filtered_dataframe[KEY_MASS_GRAMS].groupby(KEY_VOXEL).sum()
        return list(cells), voxel_masses

    def get_mass_from_cells(self, cell_ids: List[int]) -> float:
        filtered_dataframe = self.get_filtered_dataframe(cells=cell_ids)
        return filtered_dataframe[KEY_MASS_GRAMS].sum()

    @property
    def materials(self) -> np.ndarray:
        return self._dataframe.index.unique(level=KEY_MATERIAL).values
