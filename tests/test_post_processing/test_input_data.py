import shutil
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

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
    KEY_RADWASTE_CLASS,
    KEY_IRAS,
    KEY_TOTAL_SPECIFIC_ACTIVITY,
    KEY_RELEVANT_SPECIFIC_ACTIVITY,
    KEY_DOSE_1_METER,
    KEY_CDR,
)
from f4e_radwaste.data_formats.data_absolute_activity import DataAbsoluteActivity
from f4e_radwaste.data_formats.data_isotope_criteria import DataIsotopeCriteria
from f4e_radwaste.data_formats.data_mass import DataMass
from f4e_radwaste.data_formats.data_mesh_activity import DataMeshActivity
from f4e_radwaste.data_formats.data_mesh_info import DataMeshInfo
from f4e_radwaste.post_processing.calculate_dose_rates import DoseCalculator
from f4e_radwaste.post_processing.component_output import ComponentOutput
from f4e_radwaste.post_processing.components_info import ComponentsInfo
from f4e_radwaste.post_processing.folder_paths import FolderPaths
from f4e_radwaste.post_processing.input_data import (
    InputData,
    create_name_by_time_and_materials,
)
from f4e_radwaste.post_processing.mesh_ouput import MeshOutput


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

        # DataMeshInfo
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
            KEY_ISOTOPE: ["H3", "Be10", "C14", "Na22", "Fe55"],
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

        # DoseCalculator
        dose_1_m_factors = pd.Series(
            index=["He8", "Be7", "Be11", "B12", "B13", "B14"],
            data=[1.40e-08, 8.49e-10, 1.59e-08, 5.87e-10, 3.11e-09, 5.55e-08],
        )
        cdr_factors = pd.DataFrame(
            index=["He8", "Fe55", "Be11", "B12", "B13", "B14"],
            data={
                "H": [1.09e-07, 4.80e-09, 2.59e-07, 1.08e-08, 5.07e-08, 1.24e-06],
                "He": [2.17e-07, 9.53e-09, 5.07e-07, 2.11e-08, 9.98e-08, 2.41e-06],
                "Li": [2.51e-07, 1.10e-08, 5.80e-07, 2.42e-08, 1.15e-07, 2.74e-06],
            },
        )
        material_mix_10 = pd.Series(
            index=["He", "H"],
            data=[0.6, 0.4],
        )
        material_mix_20 = pd.Series(
            index=["Be", "B"],
            data=[0.5, 0.5],
        )
        material_mixes_by_id = {
            10: material_mix_10,
            20: material_mix_20,
            30: material_mix_20,
        }
        self.dose_calculator = DoseCalculator(
            dose_1_m_factors=dose_1_m_factors,
            cdr_factors=cdr_factors,
            element_mix_by_material_id=material_mixes_by_id,
        )

        # ComponentsInfo
        component_ids = [
            ["Component_1", [1, 2]],
            ["Component_2", [3]],
            ["Empty component", [99999]],
        ]
        self.components_info = ComponentsInfo(
            component_ids=component_ids,
            data_mass=data_mass,
            dose_calculator=self.dose_calculator,
        )

        # Temporary folder
        self.test_dir = tempfile.mkdtemp()
        self.folder_paths = FolderPaths(
            input_files=Path(""),
            data_tables=Path(self.test_dir),
            csv_results=Path(""),
            vtk_results=Path(""),
        )

    def tearDown(self):
        shutil.rmtree(self.test_dir)

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
        with self.assertRaises(ValueError):
            self.input_data.get_mesh_activity_by_time_and_materials(15, [999])

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

    def test_get_component_output_by_time_and_ids(self):
        component_output = self.input_data.get_component_output_by_time_and_ids(
            decay_time=1,
            components_info=self.components_info,
            dose_calculator=self.dose_calculator,
        )

        self.assertIsInstance(component_output, ComponentOutput)

        # Expected dataframe
        data = {
            KEY_VOXEL: ["Component_1", "Component_2", "Empty component"],
            KEY_DOSE_1_METER: [0.0, 0.0, 0.0],
            KEY_CDR: [6.110400e-10, 0.0, 0.0],
            KEY_RADWASTE_CLASS: [0, 0, 0],
            KEY_IRAS: [0.0004, 0.0002, 0.0000],
            KEY_LMA: [0, 0, 0],
            KEY_TOTAL_SPECIFIC_ACTIVITY: [0.6, 0.2, 0.0],
            KEY_RELEVANT_SPECIFIC_ACTIVITY: [0.4, 0.2, 0.0],
            "Fe55": [1 / 5, 0.0, 0.0],
            "H3": [2 / 5, 2 / 10, 0.0],
            KEY_MASS_GRAMS: [5, 10, 0.0],
        }
        df = pd.DataFrame(data)
        df.set_index([KEY_VOXEL], inplace=True)

        pd.testing.assert_frame_equal(
            df, component_output.data_mesh_activity._dataframe
        )
        self.assertEqual("1.00s_by_component", component_output.name)
        self.assertIn(
            KEY_RADWASTE_CLASS, component_output.data_mesh_activity._dataframe.columns
        )

    def test_get_component_mesh_activity_by_time_and_ids(self):
        comp_mesh_act = self.input_data.get_component_mesh_activity_by_time_and_ids(
            decay_time=1, components_info=self.components_info
        )

        self.assertIsInstance(comp_mesh_act, DataMeshActivity)

        # Expected dataframe
        data = {
            KEY_VOXEL: ["Component_1", "Component_2", "Empty component"],
            "Fe55": [1 / 5, 0.0, 0.0],
            "H3": [2 / 5, 2 / 10, 0.0],
            KEY_MASS_GRAMS: [5, 10, 0.0],
        }
        df = pd.DataFrame(data)
        df.set_index([KEY_VOXEL], inplace=True)

        pd.testing.assert_frame_equal(df, comp_mesh_act._dataframe)

    def test_get_mesh_output_by_time_and_materials(self):
        result = self.input_data.get_mesh_output_by_time_and_materials(1, [10])

        self.assertIsInstance(result, MeshOutput)
        self.assertIn(KEY_RADWASTE_CLASS, result.data_mesh_activity._dataframe.columns)

    def test_try_get_mesh_output_by_time_and_materials_no_exception(self):
        result_try = self.input_data.try_get_mesh_output_by_time_and_materials(1, [10])
        direct_result = self.input_data.get_mesh_output_by_time_and_materials(1, [10])

        pd.testing.assert_frame_equal(
            result_try.data_mesh_activity._dataframe,
            direct_result.data_mesh_activity._dataframe,
        )

    def test_try_get_mesh_output_by_time_and_materials_with_exception(self):
        result = self.input_data.try_get_mesh_output_by_time_and_materials(1, [99999])

        self.assertIsNone(result)

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
            input_data.data_mesh_info.data_mass._dataframe.index.get_level_values(2)
            .unique()
            .tolist()
        )
        self.assertListEqual([1], cells_in_data_mass)

    def test_save_data_tables(self):
        self.input_data.save_data_tables(self.folder_paths)

        absolute_activity_file = (
            f"{self.input_data.data_absolute_activity.__class__.__name__}.hdf5"
        )
        self.assertTrue(self.folder_paths.data_tables / absolute_activity_file)

        mesh_info_file = f"{self.input_data.data_mesh_info.__class__.__name__}.hdf5"
        self.assertTrue(self.folder_paths.data_tables / mesh_info_file)

    def test_create_name_by_time_and_materials(self):
        result = create_name_by_time_and_materials(5, [123])
        self.assertEqual(result, "Time 5.00s with materials [123]")

        result = create_name_by_time_and_materials(5)
        self.assertEqual(result, "Time 5.00s with materials all_materials")
