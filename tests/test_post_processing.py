import unittest
from copy import deepcopy

import numpy as np
import pandas as pd

from f4e_radwaste.constants import (
    KEY_TIME,
    KEY_VOXEL,
    KEY_CELL,
    KEY_ISOTOPE,
    KEY_ABSOLUTE_ACTIVITY,
    KEY_MASS_GRAMS,
    KEY_MATERIAL,
    KEY_LDF_DECLARATION,
    KEY_TFA_DECLARATION,
    KEY_TFA_CLASS,
    KEY_LMA,
    KEY_CSA_DECLARATION,
    KEY_HALF_LIFE,
    KEY_TOTAL_SPECIFIC_ACTIVITY,
    KEY_RELEVANT_SPECIFIC_ACTIVITY,
    KEY_IRAS,
    KEY_RADWASTE_CLASS,
    TYPE_TFA,
    TYPE_A,
    TYPE_B,
)
from f4e_radwaste.data_formats.data_absolute_activity import DataAbsoluteActivity
from f4e_radwaste.data_formats.data_isotope_criteria import DataIsotopeCriteria
from f4e_radwaste.data_formats.data_mass import DataMass
from f4e_radwaste.data_formats.data_mesh_activity import DataMeshActivity
from f4e_radwaste.post_processing import (
    group_data_by_time_and_materials,
    classify_waste,
)


class GroupDataByTimeAndMaterialsTests(unittest.TestCase):
    def setUp(self) -> None:
        # DataAbsoluteActivity
        data = {
            KEY_TIME: [1, 1, 1, 1, 2, 2],
            KEY_VOXEL: [1, 1, 1, 2, 1, 1],
            KEY_CELL: [1, 1, 2, 3, 1, 2],
            KEY_ISOTOPE: ["H3", "Fe55", "H3", "H3", "H3", "Fe55"],
            KEY_ABSOLUTE_ACTIVITY: [0.5, 1.0, 1.5, 2.0, 0.1, 0.2],
        }
        df = pd.DataFrame(data)
        df.set_index([KEY_TIME, KEY_VOXEL, KEY_CELL, KEY_ISOTOPE], inplace=True)
        self.data_absolute_activity = DataAbsoluteActivity(df)

        # DataMass
        data = {
            KEY_VOXEL: [1, 1, 2],
            KEY_MATERIAL: [10, 20, 30],
            KEY_CELL: [1, 2, 3],
            KEY_MASS_GRAMS: [2, 3, 10],
        }
        df = pd.DataFrame(data)
        df.set_index([KEY_VOXEL, KEY_MATERIAL, KEY_CELL], inplace=True)
        self.data_mass = DataMass(df)

    def test_group_data_by_time_and_materials_simple(self):
        # Second decay time, material 10 only
        data = {
            KEY_VOXEL: [1],
            KEY_MASS_GRAMS: [2],
            "H3": [0.1 / 2],
        }
        df = pd.DataFrame(data)
        df.set_index([KEY_VOXEL], inplace=True)
        expected_mesh_activity = DataMeshActivity(df)

        decay_time = 2
        materials = [10]
        data_mesh_activity = group_data_by_time_and_materials(
            self.data_absolute_activity, self.data_mass, decay_time, materials
        )
        pd.testing.assert_frame_equal(
            data_mesh_activity._dataframe, expected_mesh_activity._dataframe
        )

    def test_group_data_by_time_and_materials_complex(self):
        # First decay time, all materials
        data = {
            KEY_VOXEL: [1, 2],
            KEY_MASS_GRAMS: [5, 10],
            "Fe55": [1 / (2 + 3), 0],
            "H3": [(0.5 + 1.5) / (2 + 3), 2 / 10],
        }
        df = pd.DataFrame(data)
        df.set_index([KEY_VOXEL], inplace=True)
        expected_mesh_activity = DataMeshActivity(df)

        decay_time = 1
        materials = [10, 20, 30]
        data_mesh_activity = group_data_by_time_and_materials(
            self.data_absolute_activity, self.data_mass, decay_time, materials
        )
        pd.testing.assert_frame_equal(
            data_mesh_activity._dataframe,
            expected_mesh_activity._dataframe,
        )

    def test_group_data_by_time_and_materials_empty(self):
        data_mesh_activity = group_data_by_time_and_materials(
            self.data_absolute_activity, self.data_mass, 15, [999]
        )
        self.assertIsNone(data_mesh_activity)


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
        data_mesh_activity = deepcopy(self.data_mesh_activity)

        classify_waste(data_mesh_activity, self.data_isotope_criteria)

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
