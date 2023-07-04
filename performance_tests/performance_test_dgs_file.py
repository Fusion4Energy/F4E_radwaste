import unittest
from pathlib import Path

from f4e_radwaste.readers.dgs_file import read_file


class DgsFilePerformanceTests(unittest.TestCase):
    def setUp(self) -> None:
        current_file = Path(__file__)
        self.tests_folder_path = current_file.parent

    def test_read_file_performance(self):
        path_to_dgs_file = self.tests_folder_path / "old_data/DGSdata_example_ivvs.dat"
        data_absolute_activity = read_file(path_to_dgs_file)
        result_value = data_absolute_activity.get_filtered_dataframe(
            decay_times=[1e5],
            voxels=[1],
            cells=[324896],
            isotopes=["Fe55"],
        ).values[0]
        # partial volume * specific_activity in Bq/cm3
        expected_value = 1.053335e03 * 5.5910819e02
        self.assertAlmostEqual(expected_value, result_value)
        # repeat the test with other old_data point
        result_value = data_absolute_activity.get_filtered_dataframe(
            decay_times=[1e6],
            voxels=[19567],
            cells=[534515],
            isotopes=["Cr50"],
        ).values[0]
        # partial volume * specific_activity in Bq/cm3
        expected_value = 1.693465e01 * 9.0091646e-05
        self.assertAlmostEqual(expected_value, result_value)
