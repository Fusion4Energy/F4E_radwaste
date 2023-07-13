import os
import unittest
from pathlib import Path

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
        pd.testing.assert_frame_equal(filtered_df, expected_df)

    def test_get_filtered_dataframe_by_columns(self):
        data = {
            KEY_VOXEL: [1, 2, 3, 4],
            "Fe55": [0.3333, 0.555, 5.32e3, 0.444],
        }
        expected_df = pd.DataFrame(data)
        expected_df.set_index([KEY_VOXEL], inplace=True)

        filtered_df = self.data_mesh_activity.get_filtered_dataframe(columns=["Fe55"])
        pd.testing.assert_frame_equal(filtered_df, expected_df)

    def test_add_columns_format_valid(self):
        data = {
            KEY_VOXEL: [1, 2, 3, 4],
            "Nb94": [0.3, 0.5, 5.32e3, 0.4],
            "Other name": ["str", "str", "str", "str"],
            KEY_MASS_GRAMS: [5, 5, 5, 2],
            "H3": [0.1235, 0.51255, 1.32e3, 0.432],
            "Fe55": [0.3333, 0.555, 5.32e3, 0.444],
        }
        expected_df = pd.DataFrame(data)
        expected_df.set_index([KEY_VOXEL], inplace=True)

        column_1 = pd.Series([0.3, 0.5, 5.32e3, 0.4])
        column_2 = pd.Series(["str", "str", "str", "str"])
        column_1.index = [1, 2, 3, 4]
        column_2.index = [1, 2, 3, 4]
        result_dataframe = self.data_mesh_activity.get_dataframe_with_added_columns(
            {
                "Nb94": column_1,
                "Other name": column_2,
            }
        )

        pd.testing.assert_frame_equal(result_dataframe, expected_df)

    def test_to_csv(self):
        self.data_mesh_activity.to_csv(Path(""), "test")
        os.remove("test.csv")
