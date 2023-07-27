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

    def __init__(self, dataframe: pd.DataFrame):
        super().__init__(dataframe)
        self._dataframe = self._dataframe.sort_index()

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

    def get_cells_and_masses_from_selection(
        self, materials: Optional[List[int]] = None, voxels: Optional[List[int]] = None
    ) -> Tuple[List[int], pd.DataFrame]:
        filtered_dataframe = self.get_filtered_dataframe(
            materials=materials, voxels=voxels
        )
        cells = filtered_dataframe.index.unique(level=KEY_CELL).values
        voxel_masses = filtered_dataframe[KEY_MASS_GRAMS].groupby(KEY_VOXEL).sum()
        return list(cells), voxel_masses

    def get_mass_from_cells(self, cell_ids: List[int]) -> float:
        filtered_dataframe = self.get_filtered_dataframe(cells=cell_ids)
        return filtered_dataframe[KEY_MASS_GRAMS].sum()

    def calculate_material_id_proportions(
        self, cell_ids: List[List[int]]
    ) -> List[pd.Series]:
        mat_id_proportions = []

        for comp_cell_ids in cell_ids:
            df = self.get_filtered_dataframe(cells=comp_cell_ids)
            masses_by_material = df.groupby(KEY_MATERIAL).sum()
            mat_id_proportion = masses_by_material / masses_by_material.sum()
            mat_id_proportion = mat_id_proportion[KEY_MASS_GRAMS]
            mat_id_proportions.append(mat_id_proportion)

        return mat_id_proportions

    @property
    def materials(self) -> np.ndarray:
        return self._dataframe.index.unique(level=KEY_MATERIAL).values
