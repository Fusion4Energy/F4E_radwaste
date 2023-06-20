import os
import unittest
from pathlib import Path

import pandas as pd

from f4e_radwaste.constants import (
    KEY_ABSOLUTE_ACTIVITY,
    KEY_TIME,
    KEY_VOXEL,
    KEY_CELL,
    KEY_ISOTOPE,
)
from f4e_radwaste.data_formats.data_absolute_activity import DataAbsoluteActivity


class DataFrameValidatorTests(unittest.TestCase):
    def setUp(self):
        # Create a valid DataFrame for testing
        data = {
            KEY_TIME: [1, 1, 2, 2],
            KEY_VOXEL: [1, 2, 1, 2],
            KEY_CELL: [1, 1, 2, 2],
            KEY_ISOTOPE: ["A", "B", "A", "B"],
            KEY_ABSOLUTE_ACTIVITY: [0.5, 1.0, 1.5, 2.0],
        }
        df = pd.DataFrame(data)
        df.set_index([KEY_TIME, KEY_VOXEL, KEY_CELL, KEY_ISOTOPE], inplace=True)

        # Initialize the validator with the DataFrame
        self.data_absolute_activity = DataAbsoluteActivity(df)

    def test_validate_dataframe_format_valid(self):
        self.assertIsInstance(self.data_absolute_activity, DataAbsoluteActivity)

    def test_validate_dataframe_format_invalid(self):
        # Create an invalid DataFrame for testing
        data = {
            KEY_TIME: [1, 1, 2, 2],
            KEY_VOXEL: [1, 2, 1, 2],
            KEY_CELL: [1, 1, 2, 2],
            KEY_ISOTOPE: ["A", "B", "A", "B"],
            "Some Column": [0.5, 1.0, 1.5, 2.0],  # Incorrect column name
        }
        df = pd.DataFrame(data)
        df.set_index([KEY_TIME, KEY_VOXEL, KEY_CELL, KEY_ISOTOPE], inplace=True)

        # Verify that initializing the validator raises a ValueError
        with self.assertRaises(ValueError):
            DataAbsoluteActivity(df)

    def test_validate_dataframe_extra_column(self):
        # Create an invalid DataFrame for testing
        data = {
            KEY_TIME: [1, 1, 2, 2],
            KEY_VOXEL: [1, 2, 1, 2],
            KEY_CELL: [1, 1, 2, 2],
            KEY_ISOTOPE: ["A", "B", "A", "B"],
            KEY_ABSOLUTE_ACTIVITY: [0.5, 1.0, 1.5, 2.0],
            "Some Column": [0.5, 1.0, 1.5, 2.0],  # It is valid to have extra columns
        }
        df = pd.DataFrame(data)
        df.set_index([KEY_TIME, KEY_VOXEL, KEY_CELL, KEY_ISOTOPE], inplace=True)
        validator = DataAbsoluteActivity(df)
        self.assertIsInstance(validator, DataAbsoluteActivity)

    # def test_get_value(self):
    #     # Test retrieving a value from the DataFrame using get_value method
    #     value = self.validator.get_value(time=1, voxel=2, cell=1, isotope="B")
    #     expected_value = 1.0
    #     self.assertEqual(value, expected_value)
    #
    # def test_get_value_invalid_index(self):
    #     # Test retrieving a value with an invalid index combination
    #     with self.assertRaises(KeyError):
    #         self.validator.get_value(time=2, voxel=2, cell=1, isotope="A")
    #
    # def test_get_value_missing_index(self):
    #     # Test retrieving a value with a missing index
    #     with self.assertRaises(KeyError):
    #         self.validator.get_value(time="", voxel=1, cell=1, isotope="A")

    def test_get_filtered_dataframe_by_decay_times(self):
        # Expected dataframe
        data = {
            KEY_TIME: [1, 1],
            KEY_VOXEL: [1, 2],
            KEY_CELL: [1, 1],
            KEY_ISOTOPE: ["A", "B"],
            KEY_ABSOLUTE_ACTIVITY: [0.5, 1.0],
        }
        expected_df = pd.DataFrame(data)
        expected_df.set_index(
            [KEY_TIME, KEY_VOXEL, KEY_CELL, KEY_ISOTOPE], inplace=True
        )

        filtered_df = self.data_absolute_activity.get_filtered_dataframe(
            decay_times=[1.0]
        )
        self.assertTrue(filtered_df.equals(expected_df))

    def test_get_filtered_dataframe_by_voxels_and_isotopes(self):
        # Expected dataframe
        data = {
            KEY_TIME: [1, 2],
            KEY_VOXEL: [1, 1],
            KEY_CELL: [1, 2],
            KEY_ISOTOPE: ["A", "A"],
            KEY_ABSOLUTE_ACTIVITY: [0.5, 1.5],
        }
        expected_df = pd.DataFrame(data)
        expected_df.set_index(
            [KEY_TIME, KEY_VOXEL, KEY_CELL, KEY_ISOTOPE], inplace=True
        )

        filtered_df = self.data_absolute_activity.get_filtered_dataframe(
            voxels=[1, 3], isotopes=["A", "C"]
        )
        self.assertTrue(filtered_df.equals(expected_df))

    def test_get_filtered_dataframe_no_filtering(self):
        filtered_df = self.data_absolute_activity.get_filtered_dataframe()
        self.assertTrue(filtered_df.equals(self.data_absolute_activity._dataframe))

    def test_get_filtered_dataframe_empty_filter_criteria(self):
        filtered_df = self.data_absolute_activity.get_filtered_dataframe(
            decay_times=[], voxels=[4, 5]
        )
        self.assertTrue(filtered_df.empty)

    def test_get_filtered_dataframe_single_result(self):
        # Expected dataframe
        data = {
            KEY_TIME: [1],
            KEY_VOXEL: [1],
            KEY_CELL: [1],
            KEY_ISOTOPE: ["A"],
            KEY_ABSOLUTE_ACTIVITY: [0.5],
        }
        expected_df = pd.DataFrame(data)
        expected_df.set_index(
            [KEY_TIME, KEY_VOXEL, KEY_CELL, KEY_ISOTOPE], inplace=True
        )

        filtered_df = self.data_absolute_activity.get_filtered_dataframe(
            decay_times=[1], voxels=[1], cells=[1], isotopes=["A"]
        )
        self.assertTrue(filtered_df.equals(expected_df))

    def test_save_and_load_dataframe_to_hdf5(self):
        # Save the dataframe
        folder_path = Path("")
        self.data_absolute_activity.save_dataframe_to_hdf5(folder_path)

        # Two Dataframes, one read directly and one loaded with the function
        loaded_data = DataAbsoluteActivity.load(folder_path)
        read_df = pd.read_hdf(
            folder_path / "DataAbsoluteActivity.hdf5", key="dataframe"
        )
        read_df = pd.DataFrame(read_df)

        # Assertion
        pd.testing.assert_frame_equal(
            self.data_absolute_activity._dataframe, loaded_data._dataframe
        )
        pd.testing.assert_frame_equal(self.data_absolute_activity._dataframe, read_df)

        # Clean the file
        os.remove(folder_path / "DataAbsoluteActivity.hdf5")
