import unittest

import pandas as pd

from f4e_radwaste.constants import (
    KEY_TIME,
    KEY_VOXEL,
    KEY_CELL,
    KEY_ISOTOPE,
    KEY_ABSOLUTE_ACTIVITY,
)
from f4e_radwaste.data_formats.data_absolute_activity import DataAbsoluteActivity
from f4e_radwaste.readers.dgs_file import read_file, fix_isotope_names

from io import StringIO
from unittest.mock import patch

EXAMPLE_DGS_FILE = """ Photon Isotope
Number of decay times:         2
 Case:         5808  Nmat:            2
 Cells:
 1 2
 Volumes:
 0.1 0.2
Time  1.000E+05 S
Number of materials:         3
Nb91M1     Hf178M2     Co60
2.2648085E+07 7.2338034E+06 6.8497718E+06
Number of materials:         3
Nb91M1     Hf178M2     Co60
2.2648085E+02 7.2338034E+02 6.8497718E+02
Time  2.300E+05 S
Number of materials:         3
Nb91M1     Hf178M2     Co60
2.2648085E+07 7.2338034E+06 6.8497718E+06
Number of materials:         3
Nb91M1     Hf178M2     Co60
2.2648085E+02 7.2338034E+02 6.8497718E+02
"""


class DgsFileTests(unittest.TestCase):
    def setUp(self):
        data = {
            KEY_TIME: [
                100000.0,
                100000.0,
                100000.0,
                100000.0,
                100000.0,
                100000.0,
                230000.0,
                230000.0,
                230000.0,
                230000.0,
                230000.0,
                230000.0,
            ],
            KEY_VOXEL: [
                5808,
                5808,
                5808,
                5808,
                5808,
                5808,
                5808,
                5808,
                5808,
                5808,
                5808,
                5808,
            ],
            KEY_CELL: [1, 1, 1, 2, 2, 2, 1, 1, 1, 2, 2, 2],
            KEY_ISOTOPE: [
                "Nb91m",
                "Hf178n",
                "Co60",
                "Nb91m",
                "Hf178n",
                "Co60",
                "Nb91m",
                "Hf178n",
                "Co60",
                "Nb91m",
                "Hf178n",
                "Co60",
            ],
            KEY_ABSOLUTE_ACTIVITY: [
                2264808.5,
                723380.3400000001,
                684977.18,
                45.296170000000004,
                144.67606800000001,
                136.995436,
                2264808.5,
                723380.3400000001,
                684977.18,
                45.296170000000004,
                144.67606800000001,
                136.995436,
            ],
        }
        df = pd.DataFrame(data)
        df.set_index([KEY_TIME, KEY_VOXEL, KEY_CELL, KEY_ISOTOPE], inplace=True)
        self.data_absolute_activity = DataAbsoluteActivity(df)

    def test_fix_isotope_names(self):
        data = {
            KEY_TIME: [
                100000.0,
                100000.0,
                100000.0,
                100000.0,
                100000.0,
                100000.0,
                230000.0,
                230000.0,
                230000.0,
                230000.0,
                230000.0,
                230000.0,
            ],
            KEY_VOXEL: [
                5808,
                5808,
                5808,
                5808,
                5808,
                5808,
                5808,
                5808,
                5808,
                5808,
                5808,
                5808,
            ],
            KEY_CELL: [1, 1, 1, 2, 2, 2, 1, 1, 1, 2, 2, 2],
            KEY_ISOTOPE: [
                "Nb91M1",
                "Hf178M2",
                "Co60",
                "Nb91M1",
                "Hf178M2",
                "Co60",
                "Nb91M1",
                "Hf178M2",
                "Co60",
                "Nb91M1",
                "Hf178M2",
                "Co60",
            ],
            KEY_ABSOLUTE_ACTIVITY: [
                2264808.5,
                723380.3400000001,
                684977.18,
                45.296170000000004,
                144.67606800000001,
                136.995436,
                2264808.5,
                723380.3400000001,
                684977.18,
                45.296170000000004,
                144.67606800000001,
                136.995436,
            ],
        }
        dataframe = pd.DataFrame(data)
        index_columns = [KEY_TIME, KEY_VOXEL, KEY_CELL, KEY_ISOTOPE]
        dataframe.set_index(index_columns, inplace=True)

        fix_isotope_names(dataframe)

        self.assertIn("Nb91m", dataframe.index.get_level_values(3))
        self.assertIn("Hf178n", dataframe.index.get_level_values(3))

    def test_read_file(self):
        with patch("builtins.open", return_value=StringIO(EXAMPLE_DGS_FILE)):
            result = read_file("test.dat")

        self.assertIsInstance(result, DataAbsoluteActivity)
        pd.testing.assert_frame_equal(
            self.data_absolute_activity._dataframe, result._dataframe
        )
