import unittest
from io import StringIO
from unittest.mock import patch

import numpy as np
import pandas as pd

from f4e_radwaste.constants import (
    KEY_HALF_LIFE,
    KEY_LDF_DECLARATION,
    KEY_ISOTOPE,
    KEY_CSA_DECLARATION,
    KEY_LMA,
    KEY_TFA_CLASS,
    KEY_TFA_DECLARATION,
)
from f4e_radwaste.data_formats.data_isotope_criteria import DataIsotopeCriteria
from f4e_radwaste.readers.isotope_criteria_file import read_file

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
    "",
    "",
    "",
    "",
    ""
  ]
}
"""


class IsotopeCriteriaTests(unittest.TestCase):
    def setUp(self) -> None:
        data = {
            KEY_ISOTOPE: ["H3", "Be10", "C14", "Na22", "Al26"],
            KEY_HALF_LIFE: [3.89e08, 5.05e13, 1.81e11, 8.21e07, 2.27e13],
            KEY_CSA_DECLARATION: [10, 0.0001, 10, 1, np.nan],
            KEY_LMA: [2e5, 5.10e03, 9.2e4, 1.3e8, np.nan],
            KEY_TFA_CLASS: [3, 3, 3, 1, np.nan],
            KEY_TFA_DECLARATION: [1, 0.01, 0.1, 0.1, np.nan],
            KEY_LDF_DECLARATION: [10, 1, 1, np.nan, np.nan],
        }
        df = pd.DataFrame(data)
        df.set_index([KEY_ISOTOPE], inplace=True)

        # Initialize the validator with the DataFrame
        self.data_isotope_criteria = DataIsotopeCriteria(df)

    def test_read_file(self):
        with patch("builtins.open", return_value=StringIO(EXAMPLE_ISOTOPE_CRITERIA)):
            result = read_file("test.dat")

        self.assertIsInstance(result, DataIsotopeCriteria)

        pd.testing.assert_frame_equal(
            result._dataframe, self.data_isotope_criteria._dataframe
        )

    def test_read_file_path(self):
        result = read_file()

        self.assertIsInstance(result, DataIsotopeCriteria)
