import os
import shutil
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

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
from f4e_radwaste.data_formats.data_mesh_info import DataMeshInfo
from f4e_radwaste.post_processing.calculate_dose_rates import DoseCalculator
from f4e_radwaste.post_processing.components_info import ComponentsInfo
from f4e_radwaste.post_processing.folder_paths import FolderPaths
from f4e_radwaste.post_processing.input_data import (
    InputData,
)
from f4e_radwaste.post_processing.post_processing import (
    create_folder_paths,
    load_input_data_from_folder,
    StandardProcessor,
    ByComponentProcessor,
    FilteredProcessor,
)


class PostProcessingTests(unittest.TestCase):
    def setUp(self):
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

        # Temporary FolderPaths
        self.dir_inputs = tempfile.mkdtemp()
        self.dir_tables = tempfile.mkdtemp()
        self.dir_csv = tempfile.mkdtemp()
        self.dir_vtk = tempfile.mkdtemp()
        self.folder_paths = FolderPaths(
            input_files=Path(self.dir_inputs),
            data_tables=Path(self.dir_tables),
            csv_results=Path(self.dir_csv),
            vtk_results=Path(self.dir_vtk),
        )

        # Temporary auxiliary folders
        self.test_dir_empty = tempfile.mkdtemp()
        self.test_dir_filled = tempfile.mkdtemp()
        path_data_tables = Path(self.test_dir_filled) / "data_tables"
        os.mkdir(path_data_tables)
        with open(path_data_tables / "test.txt", "w") as infile:
            infile.write("Hello world!")

        # Test folder data
        self.input_folder_path = Path(__file__).parents[1] / "data/test_folder_cart"

    def test_standard_processor_init(self):
        processor = StandardProcessor(self.input_folder_path)

        self.assertIsInstance(processor, StandardProcessor)

    def test_standard_processor_process(self):
        processor = StandardProcessor(self.input_folder_path)
        processor.input_data = self.input_data
        processor.folder_paths = self.folder_paths

        StandardProcessor.process(processor)

        data_tables = os.listdir(self.folder_paths.data_tables)
        self.assertTrue("DataAbsoluteActivity.hdf5" in data_tables)
        self.assertTrue("DataMass.hdf5" in data_tables)
        self.assertTrue("DataMeshInfo.json" in data_tables)

    def test_filtered_processor_init(self):
        processor = FilteredProcessor(self.input_folder_path)
        self.assertIsInstance(processor, FilteredProcessor)

        data_mass = processor.input_data.data_mesh_info.data_mass
        data_mass_index = data_mass.get_filtered_dataframe().index
        data_mass_cells = data_mass_index.get_level_values(KEY_CELL).unique().values
        self.assertListEqual([309485], list(data_mass_cells))

        activity = processor.input_data.data_absolute_activity
        activity_index = activity.get_filtered_dataframe().index
        activity_cells = activity_index.get_level_values(KEY_CELL).unique().values
        self.assertListEqual([1], list(activity_cells))

    def test_by_component_processor_init(self):
        processor = ByComponentProcessor(self.input_folder_path)

        self.assertIsInstance(processor, ByComponentProcessor)

    def test_by_component_processor_process(self):
        processor = ByComponentProcessor(self.input_folder_path)
        processor.input_data = self.input_data
        processor.folder_paths = self.folder_paths

        ByComponentProcessor.process(processor)

        csv_tables = os.listdir(self.folder_paths.csv_results)
        self.assertTrue("1.00s_by_component.csv" in csv_tables)
        self.assertTrue("2.00s_by_component.csv" in csv_tables)

    def test_process_input_data_by_material(self):
        mock_standard_processor = SimpleNamespace()
        mock_standard_processor.input_data = self.input_data
        mock_standard_processor.folder_paths = self.folder_paths

        # noinspection PyTypeChecker
        StandardProcessor.process_input_data_by_material(mock_standard_processor)

        csv_files = os.listdir(self.folder_paths.csv_results)
        self.assertTrue("Time 2.00s with materials all_materials.csv" in csv_files)

        vtk_files = os.listdir(self.folder_paths.vtk_results)
        self.assertTrue("Time 1.00s with materials [30].vts" in vtk_files)

    def test_process_input_data_by_components(self):
        component_ids = [
            ["Component_1", [1, 2]],
            ["Component_2", [3]],
            ["Empty component", [99999]],
        ]
        components_info = ComponentsInfo(
            component_ids=component_ids,
            data_mass=self.input_data.data_mesh_info.data_mass,
            dose_calculator=self.dose_calculator,
        )
        mock_by_component_processor = SimpleNamespace()
        mock_by_component_processor.input_data = self.input_data
        mock_by_component_processor.folder_paths = self.folder_paths
        mock_by_component_processor.components_info = components_info
        mock_by_component_processor.dose_calculator = self.dose_calculator

        # noinspection PyTypeChecker
        ByComponentProcessor.process_input_data_by_components(
            mock_by_component_processor
        )

        csv_files = os.listdir(self.folder_paths.csv_results)
        self.assertTrue("1.00s_by_component.csv" in csv_files)
        self.assertTrue("2.00s_by_component.csv" in csv_files)

    def test_create_folder_paths_empty(self):
        folder_paths = create_folder_paths(Path(self.test_dir_empty))

        self.assertTrue(folder_paths.input_files.is_dir())
        self.assertTrue(folder_paths.data_tables.is_dir())
        self.assertTrue(folder_paths.csv_results.is_dir())
        self.assertTrue(folder_paths.vtk_results.is_dir())

    def test_create_folder_paths_filled(self):
        folder_paths = create_folder_paths(Path(self.test_dir_filled))

        self.assertTrue(folder_paths.input_files.is_dir())
        self.assertTrue(folder_paths.data_tables.is_dir())
        self.assertTrue(folder_paths.csv_results.is_dir())
        self.assertTrue(folder_paths.vtk_results.is_dir())
        self.assertEqual(0, len(os.listdir(folder_paths.data_tables)))

    def test_load_input_data_from_folder(self):
        input_data = load_input_data_from_folder(self.input_folder_path)

        self.assertIsInstance(input_data.data_absolute_activity, DataAbsoluteActivity)
        self.assertIsInstance(input_data.data_mesh_info, DataMeshInfo)
        self.assertIsInstance(input_data.isotope_criteria, DataIsotopeCriteria)

    def tearDown(self):
        shutil.rmtree(self.dir_tables)
        shutil.rmtree(self.dir_csv)
        shutil.rmtree(self.dir_vtk)
        shutil.rmtree(self.dir_inputs)
