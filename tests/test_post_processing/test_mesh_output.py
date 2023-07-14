import shutil
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from f4e_radwaste.constants import (
    CoordinateType,
    KEY_VOXEL,
    KEY_MATERIAL,
    KEY_CELL,
    KEY_MASS_GRAMS,
)
from f4e_radwaste.data_formats.data_mass import DataMass
from f4e_radwaste.data_formats.data_mesh_activity import DataMeshActivity
from f4e_radwaste.data_formats.data_mesh_info import DataMeshInfo
from f4e_radwaste.post_processing.folder_paths import FolderPaths
from f4e_radwaste.post_processing.mesh_ouput import MeshOutput


class MeshOutputTests(unittest.TestCase):
    def setUp(self):
        self.test_dir_csv = tempfile.mkdtemp()
        self.test_dir_vtk = tempfile.mkdtemp()

        self.folder_paths = FolderPaths(
            input_files=Path(""),
            data_tables=Path(""),
            csv_results=Path(self.test_dir_csv),
            vtk_results=Path(self.test_dir_vtk),
        )

        # DataMeshInfo
        data = {
            KEY_VOXEL: [1, 1, 2],
            KEY_MATERIAL: [10, 20, 30],
            KEY_CELL: [1, 2, 3],
            KEY_MASS_GRAMS: [2, 3, 10],
        }
        df = pd.DataFrame(data)
        df.set_index([KEY_VOXEL, KEY_MATERIAL, KEY_CELL], inplace=True)
        data_mass = DataMass(df)
        data_mesh_info = DataMeshInfo(
            coordinates=CoordinateType.CARTESIAN,
            data_mass=data_mass,
            vector_i=np.array([1, 0, 0]),
            vector_j=np.array([1, 0, 0]),
            vector_k=np.array([1, 0, 0]),
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

        self.mesh_output = MeshOutput(
            name="name",
            data_mesh_info=data_mesh_info,
            data_mesh_activity=data_mesh_activity,
        )

    def tearDown(self):
        shutil.rmtree(self.test_dir_csv)
        shutil.rmtree(self.test_dir_vtk)

    def test_save(self):
        self.mesh_output.save(self.folder_paths)

        mesh_activity_csv = (
            f"{self.mesh_output.data_mesh_activity.__class__.__name__}.csv"
        )
        self.assertTrue(self.folder_paths.csv_results / mesh_activity_csv)

        mesh_activity_vtk = (
            f"{self.mesh_output.data_mesh_activity.__class__.__name__}.vts"
        )
        self.assertTrue(self.folder_paths.vtk_results / mesh_activity_vtk)
