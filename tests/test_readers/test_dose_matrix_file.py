import unittest
from io import StringIO
from unittest.mock import patch

import pandas as pd

from f4e_radwaste.readers.dose_matrix_file import (
    read_dose_1_m_factors,
    read_contact_dose_rate_factors,
    GEOMETRIC_FACTOR_1_M,
)

EXAMPLE_FILE = """Absorbed doses from kerma-in-air...,,,,
Nuclide,Dose factor Gy.cm2.s/hr,Contact gamma dose rate...,,
,,H,He,Li
He8,1.40E-08,1.09E-07,2.17E-07,2.51E-07
Be7,8.49E-10,4.80E-09,9.53E-09,1.10E-08
Be11,1.59E-08,2.59E-07,5.07E-07,5.80E-07
B12,5.87E-10,1.08E-08,2.11E-08,2.42E-08
B13,3.11E-09,5.07E-08,9.98E-08,1.15E-07
B14,5.55E-08,1.24E-06,2.41E-06,2.74E-06"""


class MeshInfoFileTests(unittest.TestCase):
    def test_read_dose_1_m_factors(self):
        with patch("builtins.open", return_value=StringIO(EXAMPLE_FILE)):
            dose_1_m_factors = read_dose_1_m_factors("test.dat")

        self.assertIsInstance(dose_1_m_factors, pd.Series)
        self.assertAlmostEqual(dose_1_m_factors["He8"], 1.40e-08 * GEOMETRIC_FACTOR_1_M)
        self.assertAlmostEqual(dose_1_m_factors["B14"], 5.55e-08 * GEOMETRIC_FACTOR_1_M)

    def test_read_dose_1_m_factors_path(self):
        dose_1_m_factors = read_dose_1_m_factors()
        self.assertIn("He8", dose_1_m_factors)

    def test_read_contact_dose_rate_factors(self):
        with patch("builtins.open", return_value=StringIO(EXAMPLE_FILE)):
            cdr_factors = read_contact_dose_rate_factors("test.dat")

            self.assertIsInstance(cdr_factors, pd.DataFrame)
            self.assertAlmostEqual(cdr_factors["Li"]["He8"], 2.51e-07)
            self.assertAlmostEqual(cdr_factors["He"]["B14"], 2.41e-06)

    def test_read_contact_dose_rate_factors_path(self):
        cdr_factors = read_contact_dose_rate_factors()
        self.assertIn("Li", cdr_factors)
