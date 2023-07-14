import unittest

import numpy as np
import pandas as pd

from f4e_radwaste.constants import (
    KEY_ISOTOPE,
    KEY_HALF_LIFE,
    KEY_CSA_DECLARATION,
    KEY_LMA,
    KEY_TFA_CLASS,
    KEY_TFA_DECLARATION,
    KEY_LDF_DECLARATION,
)
from f4e_radwaste.data_formats.data_isotope_criteria import DataIsotopeCriteria


class DataIsotopeCriteriaTests(unittest.TestCase):
    def setUp(self):
        # Create a valid DataFrame for testing
        data = {
            KEY_ISOTOPE: ["H3", "Be10"],
            KEY_HALF_LIFE: [3.89e08, 5.05e13],
            KEY_CSA_DECLARATION: [10, 0.0001],
            KEY_LMA: [2.00e05, 5.10e03],
            KEY_TFA_CLASS: [3, 3],
            KEY_TFA_DECLARATION: [1, 0.01],
            KEY_LDF_DECLARATION: [10, 1],
        }
        df = pd.DataFrame(data)
        df.set_index([KEY_ISOTOPE], inplace=True)

        # Initialize the validator with the DataFrame
        self.data_isotope_criteria = DataIsotopeCriteria(df)

    def test_validate_dataframe_format_valid(self):
        self.assertIsInstance(self.data_isotope_criteria, DataIsotopeCriteria)

    def test_validate_dataframe_format_invalid(self):
        # Create a valid DataFrame for testing
        data = {
            KEY_ISOTOPE: ["H3", "Be10"],
            KEY_HALF_LIFE: [3.89e08, 5.05e13],
            KEY_CSA_DECLARATION: [10, 0.0001],
            KEY_LMA: [2.00e05, 5.10e03],
            KEY_TFA_CLASS: [3, 3],
            KEY_TFA_DECLARATION: [1, 0.01],
            # KEY_LDF_DECLARATION: [10, 1],  Missing this column
        }
        df = pd.DataFrame(data)
        df.set_index([KEY_ISOTOPE], inplace=True)

        # Verify that initializing the validator raises a ValueError
        with self.assertRaises(ValueError):
            DataIsotopeCriteria(df)

    def test_get_filtered_dataframe_by_isotopes(self):
        # Create a valid DataFrame for testing
        data = {
            KEY_ISOTOPE: ["Be10"],
            KEY_HALF_LIFE: [5.05e13],
            KEY_CSA_DECLARATION: [0.0001],
            KEY_LMA: [5.10e03],
            KEY_TFA_CLASS: [3],
            KEY_TFA_DECLARATION: [0.01],
            KEY_LDF_DECLARATION: [1],
        }
        expected_df = pd.DataFrame(data)
        expected_df.set_index([KEY_ISOTOPE], inplace=True)

        filtered_df = self.data_isotope_criteria.get_filtered_dataframe(
            isotopes=["Be10"]
        )
        self.assertTrue(filtered_df.equals(expected_df))

    def test_isotope_names_attributes(self):
        # Create a valid DataFrame for testing
        data = {
            KEY_ISOTOPE: ["H3", "Be10", "K99"],
            KEY_HALF_LIFE: [3.89e08, 5.05e13, 1e23],
            KEY_CSA_DECLARATION: [10, 0.0001, np.nan],
            KEY_LMA: [2.00e05, 5.10e03, np.nan],
            KEY_TFA_CLASS: [3, 3, np.nan],
            KEY_TFA_DECLARATION: [1, 0.01, np.nan],
            KEY_LDF_DECLARATION: [10, 1, np.nan],
        }
        df = pd.DataFrame(data)
        df.set_index([KEY_ISOTOPE], inplace=True)
        data_isotope_criteria = DataIsotopeCriteria(df)

        self.assertListEqual(
            ["Be10", "H3", "K99"], data_isotope_criteria.all_isotopes_names
        )
        self.assertListEqual(
            ["Be10", "H3"], data_isotope_criteria.relevant_isotopes_names
        )

    def test_tfa_class(self):
        data = {KEY_ISOTOPE: ["Be10", "H3"], KEY_TFA_CLASS: [3, 3]}
        expected_series = pd.Series(
            data=data[KEY_TFA_CLASS], index=data[KEY_ISOTOPE], name=KEY_TFA_CLASS
        )
        expected_series.index.name = KEY_ISOTOPE

        pd.testing.assert_series_equal(
            expected_series, self.data_isotope_criteria.tfa_class
        )

    def test_lma(self):
        data = {KEY_ISOTOPE: ["Be10", "H3"], KEY_LMA: [5.10e03, 2.00e05]}
        expected_series = pd.Series(
            data=data[KEY_LMA], index=data[KEY_ISOTOPE], name=KEY_LMA
        )
        expected_series.index.name = KEY_ISOTOPE

        pd.testing.assert_series_equal(expected_series, self.data_isotope_criteria.lma)
