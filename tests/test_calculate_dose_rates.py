import unittest

import pandas as pd

from f4e_radwaste.constants import KEY_VOXEL, KEY_MASS_GRAMS, KEY_DOSE_1_METER
from f4e_radwaste.data_formats.data_mesh_activity import DataMeshActivity
from f4e_radwaste.post_processing.calculate_dose_rates import calculate_dose_at_1_meter


class CalculateDoseRatesTests(unittest.TestCase):
    def setUp(self):
        # DataMeshActivity
        data = {
            KEY_VOXEL: [1, 2, 3, 4],
            KEY_MASS_GRAMS: [5, 5, 5, 3],
            "H3": [4, 4, 4, 4],
            "Be11": [5, 5, 8e12, 5e99],
            "K42": [6, 6, 3, 6],
            "B14": [3, 3, 3, 3],
        }
        df = pd.DataFrame(data)
        df.set_index([KEY_VOXEL], inplace=True)
        self.data_mesh_activity = DataMeshActivity(df)

        self.dose_1_m_factors = pd.Series(
            index=["He8", "Be7", "Be11", "B12", "B13", "B14"],
            data=[1.40e-08, 8.49e-10, 1.59e-08, 5.87e-10, 3.11e-09, 5.55e-08],
        )

    def test_calculate_dose_at_1_meter(self):
        activity_with_dose_1_m = calculate_dose_at_1_meter(
            self.data_mesh_activity, self.dose_1_m_factors
        ).get_filtered_dataframe()

        expected_voxel_1 = 5 * 1.59e-08 + 3 * 5.55e-08
        expected_voxel_4 = 5e99 * 1.59e-08 + 3 * 5.55e-08

        self.assertAlmostEqual(
            activity_with_dose_1_m[KEY_DOSE_1_METER][1], expected_voxel_1
        )
        self.assertAlmostEqual(
            activity_with_dose_1_m[KEY_DOSE_1_METER][4], expected_voxel_4
        )

    # def test_calculate_contact_dose_rate(self):
    #     self.assertEqual(True, False)  # add assertion here
