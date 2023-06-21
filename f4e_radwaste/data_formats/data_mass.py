from typing import Optional, List

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

    def get_cells_from_materials(self, materials: list) -> List[int]:
        filtered_dataframe = self.get_filtered_dataframe(materials=materials)
        cells = filtered_dataframe.index.unique(level=KEY_CELL).values
        return list(cells)
