import unittest

import numpy as np
import pandas as pd

from f4e_radwaste.post_processing.classify_waste import classify_waste
from f4e_radwaste.constants import (
    KEY_ISOTOPE,
    KEY_HALF_LIFE,
    KEY_CSA_DECLARATION,
    KEY_LMA,
    KEY_TFA_CLASS,
    KEY_TFA_DECLARATION,
    KEY_LDF_DECLARATION,
    KEY_VOXEL,
    KEY_MASS_GRAMS,
    KEY_TOTAL_SPECIFIC_ACTIVITY,
    KEY_RELEVANT_SPECIFIC_ACTIVITY,
    KEY_IRAS,
    KEY_RADWASTE_CLASS,
    TYPE_TFA,
    TYPE_A,
    TYPE_B,
)
from f4e_radwaste.data_formats.data_isotope_criteria import DataIsotopeCriteria
from f4e_radwaste.data_formats.data_mesh_activity import DataMeshActivity


class ClassifyWasteTests(unittest.TestCase):
    def setUp(self) -> None:
        # DataIsotopeCriteria
        data = {
            KEY_ISOTOPE: ["H3", "Be10", "C14", "Na22", "K42"],
            KEY_HALF_LIFE: [3.89e08, 5.05e13, 1.81e11, 8.21e07, 2.27e13],
            KEY_CSA_DECLARATION: [10, 0.0001, 10, 1, 1],
            KEY_LMA: [2e5, 5.10e99, 9.2e4, 1.3e8, 4],
            KEY_TFA_CLASS: [3, 2, 3, 1, np.nan],
            KEY_TFA_DECLARATION: [1, 0.01, 0.1, 0.1, 0.1],
            KEY_LDF_DECLARATION: [10, 1, 1, np.nan, np.nan],
        }
        df = pd.DataFrame(data)
        df.set_index([KEY_ISOTOPE], inplace=True)
        self.data_isotope_criteria = DataIsotopeCriteria(df)

        # DataMeshActivity
        data = {
            KEY_VOXEL: [1, 2, 3, 4],
            KEY_MASS_GRAMS: [5, 5, 5, 3],
            "H3": [4, 4, 4, 4],
            "Be10": [5, 5, 8e12, 5e99],
            "K42": [6, 6, 3, 6],  # non-relevant (TFA) isotope
            "Wrong isotope": [3, 3, 3, 3],
        }
        df = pd.DataFrame(data)
        df.set_index([KEY_VOXEL], inplace=True)
        self.data_mesh_activity = DataMeshActivity(df)

    def test_classify_waste(self):
        data_mesh_activity = classify_waste(
            self.data_mesh_activity, self.data_isotope_criteria
        )

        voxel_1_data = data_mesh_activity.get_filtered_dataframe(voxels=[1])
        total_activity_voxel_1 = voxel_1_data[KEY_TOTAL_SPECIFIC_ACTIVITY].values[0]
        relevant_activity_voxel_1 = voxel_1_data[KEY_RELEVANT_SPECIFIC_ACTIVITY].values[
            0
        ]
        iras_voxel_1 = voxel_1_data[KEY_IRAS].values[0]
        lma_voxel_1 = voxel_1_data[KEY_LMA].values[0]
        radwaste_class_voxel_1 = voxel_1_data[KEY_RADWASTE_CLASS].values[0]
        self.assertEqual(total_activity_voxel_1, 4 + 5 + 6)
        self.assertEqual(relevant_activity_voxel_1, 4 + 5)
        self.assertEqual(iras_voxel_1, 4 / 1000 + 5 / 100)
        self.assertEqual(lma_voxel_1, 1)
        self.assertEqual(radwaste_class_voxel_1, TYPE_TFA)

        voxel_3_data = data_mesh_activity.get_filtered_dataframe(voxels=[3])
        radwaste_class_voxel_3 = voxel_3_data[KEY_RADWASTE_CLASS].values[0]
        self.assertEqual(radwaste_class_voxel_3, TYPE_A)

        voxel_4_data = data_mesh_activity.get_filtered_dataframe(voxels=[4])
        radwaste_class_voxel_4 = voxel_4_data[KEY_RADWASTE_CLASS].values[0]
        self.assertEqual(radwaste_class_voxel_4, TYPE_B)
