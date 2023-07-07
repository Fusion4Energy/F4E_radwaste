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
    CoordinateType,
)
from f4e_radwaste.data_formats.data_absolute_activity import DataAbsoluteActivity
from f4e_radwaste.data_formats.data_isotope_criteria import DataIsotopeCriteria
from f4e_radwaste.data_formats.data_mass import DataMass
from f4e_radwaste.data_formats.data_mesh_activity import DataMeshActivity
from f4e_radwaste.data_formats.data_mesh_info import DataMeshInfo
from f4e_radwaste.post_processing.input_data import InputData


class InputDataTests(unittest.TestCase):
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
        data_absolute_activity = DataAbsoluteActivity(df)

        # DataMass
        data = {
            KEY_VOXEL: [1, 1, 2],
            KEY_MATERIAL: [10, 20, 30],
            KEY_CELL: [1, 2, 3],
            KEY_MASS_GRAMS: [2, 3, 10],
        }
        df = pd.DataFrame(data)
        df.set_index([KEY_VOXEL, KEY_MATERIAL, KEY_CELL], inplace=True)
        data_mass = DataMass(df)
        data_mesh_info = DataMeshInfo(
            coordinates=CoordinateType.CARTESIAN,
            data_mass=data_mass,
            vector_i=np.array([1, 0, 0]),
            vector_j=np.array([1, 0, 0]),
            vector_k=np.array([1, 0, 0]),
        )

        # DataIsotopeCriteria
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
        data_isotope_criteria = DataIsotopeCriteria(df)

        self.input_data = InputData(
            data_absolute_activity=data_absolute_activity,
            data_mesh_info=data_mesh_info,
            isotope_criteria=data_isotope_criteria,
        )

    def test_get_mesh_activity_by_time_and_materials_simple(self):
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
        data_mesh_activity = self.input_data.get_mesh_activity_by_time_and_materials(
            decay_time, materials
        )

        pd.testing.assert_frame_equal(
            data_mesh_activity._dataframe, expected_mesh_activity._dataframe
        )

    def test_get_mesh_activity_by_time_and_materials_complex(self):
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
        data_mesh_activity = self.input_data.get_mesh_activity_by_time_and_materials(
            decay_time, materials
        )

        pd.testing.assert_frame_equal(
            data_mesh_activity._dataframe,
            expected_mesh_activity._dataframe,
        )

    def test_get_mesh_activity_by_time_and_materials_empty(self):
        data_mesh_activity = self.input_data.get_mesh_activity_by_time_and_materials(
            15, [999]
        )
        self.assertIsNone(data_mesh_activity)

    def test_get_mesh_activity_by_time_and_materials_all_materials(self):
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

        # The argument 'materials' is not filled
        data_mesh_activity = self.input_data.get_mesh_activity_by_time_and_materials(
            decay_time=1
        )

        pd.testing.assert_frame_equal(
            data_mesh_activity._dataframe, expected_mesh_activity._dataframe
        )

    def test_apply_filter_include_cells(self):
        input_data = deepcopy(self.input_data)
        cells_to_include = [1]

        input_data.apply_filter_include_cells(cells_to_include)

        self.assertIsInstance(
            self.input_data.data_absolute_activity, DataAbsoluteActivity
        )
        self.assertIsInstance(input_data.data_mesh_info, DataMeshInfo)
        self.assertIsInstance(input_data.isotope_criteria, DataIsotopeCriteria)

        cells_in_activity = (
            input_data.data_absolute_activity._dataframe.index.get_level_values(2)
            .unique()
            .tolist()
        )
        self.assertListEqual([1], cells_in_activity)

        cells_in_data_mass = (
            input_data.data_mesh_info.data_mass._dataframe.index.get_level_values(
                2
            )
            .unique()
            .tolist()
        )
        self.assertListEqual([1], cells_in_data_mass)
