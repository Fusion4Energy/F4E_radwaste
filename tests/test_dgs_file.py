import unittest
from f4e_radwaste.data_formats.data_absolute_activity import DataAbsoluteActivity
from f4e_radwaste.readers.dgs_file import read_file

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
Co58     Mn54     Co60
2.2648085E+07 7.2338034E+06 6.8497718E+06
Number of materials:         3
Co58     Mn54     Co60
2.2648085E+02 7.2338034E+02 6.8497718E+02
Time  2.300E+05 S
Number of materials:         3
Co58     Mn54     Co60
2.2648085E+07 7.2338034E+06 6.8497718E+06
Number of materials:         3
Co58     Mn54     Co60
2.2648085E+02 7.2338034E+02 6.8497718E+02
"""


class DgsFileTests(unittest.TestCase):
    def test_read_file(self):
        expected_dataframe_dict = {
            "Activity [Bq]": {
                (100000.0, 5808, 1, "Co58"): 2264808.5,
                (100000.0, 5808, 1, "Mn54"): 723380.3400000001,
                (100000.0, 5808, 1, "Co60"): 684977.18,
                (100000.0, 5808, 2, "Co58"): 45.296170000000004,
                (100000.0, 5808, 2, "Mn54"): 144.67606800000001,
                (100000.0, 5808, 2, "Co60"): 136.995436,
                (230000.0, 5808, 1, "Co58"): 2264808.5,
                (230000.0, 5808, 1, "Mn54"): 723380.3400000001,
                (230000.0, 5808, 1, "Co60"): 684977.18,
                (230000.0, 5808, 2, "Co58"): 45.296170000000004,
                (230000.0, 5808, 2, "Mn54"): 144.67606800000001,
                (230000.0, 5808, 2, "Co60"): 136.995436,
            }
        }

        with patch("builtins.open", return_value=StringIO(EXAMPLE_DGS_FILE)):
            result = read_file("test.dat")

        self.assertIsInstance(result, DataAbsoluteActivity)
        self.assertDictEqual(result._dataframe.to_dict(), expected_dataframe_dict)
