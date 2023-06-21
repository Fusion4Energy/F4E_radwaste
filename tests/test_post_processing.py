import unittest

import pandas as pd

from f4e_radwaste.constants import (
    KEY_TIME,
    KEY_VOXEL,
    KEY_CELL,
    KEY_ISOTOPE,
    KEY_ABSOLUTE_ACTIVITY,
    KEY_MASS_GRAMS,
    KEY_MATERIAL,
)
from f4e_radwaste.data_formats.data_absolute_activity import DataAbsoluteActivity
from f4e_radwaste.data_formats.data_mass import DataMass
from f4e_radwaste.data_formats.data_mesh_activity import DataMeshActivity
from f4e_radwaste.post_processing import group_data_by_time_and_materials


class PostProcessingTests(unittest.TestCase):
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
