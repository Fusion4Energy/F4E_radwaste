import os
import shutil
import tempfile
import unittest
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
)
from f4e_radwaste.data_formats.data_absolute_activity import DataAbsoluteActivity
from f4e_radwaste.data_formats.data_isotope_criteria import DataIsotopeCriteria
from f4e_radwaste.data_formats.data_mass import DataMass
from f4e_radwaste.data_formats.data_mesh_info import DataMeshInfo
from f4e_radwaste.post_processing.folder_paths import FolderPaths
from f4e_radwaste.post_processing.input_data import (
    InputData,
)
from f4e_radwaste.post_processing.post_processing import (
    process_input_data_by_material,
    process_input_data_by_components,
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

        dose_1_m_factors = pd.Series(
            index=["He8", "Fe55", "Be11", "B12", "B13", "B14"],
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

        self.input_data = InputData(
            data_absolute_activity=data_absolute_activity,
            data_mesh_info=data_mesh_info,
            isotope_criteria=data_isotope_criteria,
            dose_1_m_factors=dose_1_m_factors,
            cdr_factors=cdr_factors,
        )

        # Temporary folder
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

    def tearDown(self):
        shutil.rmtree(self.dir_tables)
        shutil.rmtree(self.dir_csv)
        shutil.rmtree(self.dir_vtk)
        shutil.rmtree(self.dir_inputs)

    def test_process_input_data_by_material(self):
        process_input_data_by_material(self.input_data, self.folder_paths)

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
        process_input_data_by_components(
            self.input_data, self.folder_paths, component_ids
        )

        csv_files = os.listdir(self.folder_paths.csv_results)
        self.assertTrue("1.00s_by_component.csv" in csv_files)
        self.assertTrue("2.00s_by_component.csv" in csv_files)
