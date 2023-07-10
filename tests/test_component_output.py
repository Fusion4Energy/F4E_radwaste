import shutil
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from f4e_radwaste.constants import KEY_VOXEL, KEY_MASS_GRAMS
from f4e_radwaste.data_formats.data_mesh_activity import DataMeshActivity
from f4e_radwaste.post_processing.component_output import ComponentOutput
from f4e_radwaste.post_processing.folder_paths import FolderPaths


class ComponentOutputTests(unittest.TestCase):
    def setUp(self):
        self.test_dir_csv = tempfile.mkdtemp()

        self.folder_paths = FolderPaths(
            input_files=Path(""),
            data_tables=Path(""),
            csv_results=Path(self.test_dir_csv),
            vtk_results=Path(""),
        )

        # DataMeshActivity
        data = {
            KEY_VOXEL: [1, 2, 3, 4],
            KEY_MASS_GRAMS: [5, 5, 5, 2],
            "H3": [0.1235, 0.51255, 1.32e3, 0.432],
            "Fe55": [0.3333, 0.555, 5.32e3, 0.444],
        }
        df = pd.DataFrame(data)
        df.set_index([KEY_VOXEL], inplace=True)

        # Initialize the validator with the DataFrame
        data_mesh_activity = DataMeshActivity(df)

        self.component_output = ComponentOutput(
            name="name",
            data_mesh_activity=data_mesh_activity,
        )

    def tearDown(self):
        shutil.rmtree(self.test_dir_csv)

    def test_save(self):
        self.component_output.save(self.folder_paths)

        self.assertTrue(self.folder_paths.csv_results / "name.csv")
