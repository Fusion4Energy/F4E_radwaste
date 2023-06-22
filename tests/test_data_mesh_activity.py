import unittest
from copy import deepcopy

import pandas as pd

from f4e_radwaste.constants import KEY_VOXEL, KEY_MASS_GRAMS
from f4e_radwaste.data_formats.data_mesh_activity import DataMeshActivity


class DataMeshActivityTests(unittest.TestCase):
    def setUp(self):
        data = {
            KEY_VOXEL: [1, 2, 3, 4],
            KEY_MASS_GRAMS: [5, 5, 5, 2],
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
            KEY_VOXEL: [1, 2, 3, 4],
            "H3": [0.1235, 0.51255, 1.32e3, 0.432],
            "Fe55": [0.3333, 0.555, 5.32e3, 0.444],
        }
        df = pd.DataFrame(data)
        df.set_index([KEY_VOXEL], inplace=True)

        with self.assertRaises(ValueError):
            self.data_mesh_activity = DataMeshActivity(df)

    def test_get_filtered_dataframe_by_voxels(self):
        data = {
            KEY_VOXEL: [2, 3],
            KEY_MASS_GRAMS: [5, 5],
            "H3": [0.51255, 1.32e3],
            "Fe55": [0.555, 5.32e3],
        }
        expected_df = pd.DataFrame(data)
        expected_df.set_index([KEY_VOXEL], inplace=True)

        filtered_df = self.data_mesh_activity.get_filtered_dataframe(voxels=[2, 3])
        self.assertTrue(filtered_df.equals(expected_df))

    def test_update_dataframe_format_valid(self):
        data = {
            KEY_VOXEL: [1, 2, 3, 4],
            KEY_MASS_GRAMS: [5, 5, 5, 2],
            "H3": [0.1235, 0.51255, 1.32e3, 0.432],
            "Fe55": [0.3333, 0.555, 5.32e3, 0.444],
            "NewIsotope99": [0.3333, 0.555, 5.32e3, 0.444],
        }
        df = pd.DataFrame(data)
        df.set_index([KEY_VOXEL], inplace=True)

        data_mesh_activity = deepcopy(self.data_mesh_activity)
        data_mesh_activity.update_dataframe(df)
        pd.testing.assert_frame_equal(df, data_mesh_activity._dataframe)

    def test_update_dataframe_format_invalid(self):
        data = {
            KEY_VOXEL: [1, 2, 3, 4],
            "H3": [0.1235, 0.51255, 1.32e3, 0.432],
            "Fe55": [0.3333, 0.555, 5.32e3, 0.444],
        }
        df = pd.DataFrame(data)
        df.set_index([KEY_VOXEL], inplace=True)

        data_mesh_activity = deepcopy(self.data_mesh_activity)
        with self.assertRaises(ValueError):
            data_mesh_activity.update_dataframe(df)
