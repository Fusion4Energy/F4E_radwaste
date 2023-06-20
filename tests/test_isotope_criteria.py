import unittest
from io import StringIO
from unittest.mock import patch

import numpy as np

from f4e_radwaste.constants import KEY_HALF_LIFE, KEY_LDF_DECLARATION
from f4e_radwaste.data_formats.data_isotope_criteria import DataIsotopeCriteria
from f4e_radwaste.readers.isotope_criteria import read_file

EXAMPLE_ISOTOPE_CRITERIA = """{
  "H3": [
    "3.89E+08",
    "10",
    "2.00E+05",
    "3",
    "1",
    "10"
  ],
  "Be10": [
    "5.05E+13",
    "0.0001",
    "5.10E+03",
    "3",
    "0.01",
    "1"
  ],
  "C14": [
    "1.81E+11",
    "10",
    "9.20E+04",
    "3",
    "0.1",
    "1"
  ],
  "Na22": [
    "8.21E+07",
    "1",
    "1.30E+08",
    "1",
    "0.1",
    ""
  ],
  "Al26": [
    "2.27E+13",
    "1",
    "",
    "1",
    "0.1",
    ""
  ]
}
"""


class IsotopeCriteriaTests(unittest.TestCase):
    def test_read_file(self):
        with patch("builtins.open", return_value=StringIO(EXAMPLE_ISOTOPE_CRITERIA)):
            result = read_file("test.dat")

        self.assertIsInstance(result, DataIsotopeCriteria)

        half_life = result.get_filtered_dataframe()[KEY_HALF_LIFE]["H3"]
        self.assertEqual(half_life, 3.89e08)
        ldf_declaration = result.get_filtered_dataframe()[KEY_LDF_DECLARATION]["Al26"]
        self.assertTrue(np.isnan(ldf_declaration))
