import unittest

import pandas as pd

from f4e_radwaste.constants import KEY_VOXEL
from f4e_radwaste.data_formats.data_mesh_activity import DataMeshActivity


class DataMeshActivityTests(unittest.TestCase):
    def setUp(self):
        data = {
            KEY_VOXEL: [1, 2, 3, 4],
            "H3": [0.1235, 0.51255, 1.32e3, 0.432],
            "Fe55": [0.3333, 0.555, 5.32e3, 0.444],
        }
        df = pd.DataFrame(data)
        df.set_index([KEY_VOXEL], inplace=True)

        # Initialize the validator with the DataFrame
        self.data_mesh_activity = DataMeshActivity(df)

    def test_validate_dataframe_format_valid(self):
        self.assertIsInstance(self.data_mesh_activity, DataMeshActivity)

    def test_validate_dataframe_format_invalid(self):
        data = {
            "Wrong name": [1, 2, 3, 4],
            "H3": [0.1235, 0.51255, 1.32e3, 0.432],
            "Fe55": [0.3333, 0.555, 5.32e3, 0.444],
        }
        df = pd.DataFrame(data)
        df.set_index(["Wrong name"], inplace=True)

        with self.assertRaises(ValueError):
            self.data_mesh_activity = DataMeshActivity(df)

    def test_get_filtered_dataframe_by_voxels(self):
        data = {
            KEY_VOXEL: [2, 3],
            "H3": [0.51255, 1.32e3],
            "Fe55": [0.555, 5.32e3],
        }
        expected_df = pd.DataFrame(data)
        expected_df.set_index([KEY_VOXEL], inplace=True)

        filtered_df = self.data_mesh_activity.get_filtered_dataframe(voxels=[2, 3])
        self.assertTrue(filtered_df.equals(expected_df))
