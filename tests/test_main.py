import os
import shutil
import tempfile
import unittest
from pathlib import Path

from f4e_radwaste.data_formats.data_absolute_activity import DataAbsoluteActivity
from f4e_radwaste.data_formats.data_isotope_criteria import DataIsotopeCriteria
from f4e_radwaste.data_formats.data_mesh_info import DataMeshInfo
from f4e_radwaste.main import get_folder_paths, load_input_data_from_folder


class MainTests(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)


class MainTestsFolders(unittest.TestCase):
    def setUp(self):
        self.test_dir_empty = tempfile.mkdtemp()
        self.test_dir_filled = tempfile.mkdtemp()
        path_data_tables = Path(self.test_dir_filled) / "data_tables"
        os.mkdir(path_data_tables)
        with open(path_data_tables / "test.txt", "w") as infile:
            infile.write("Hello world!")

    def tearDown(self):
        shutil.rmtree(self.test_dir_empty)
        shutil.rmtree(self.test_dir_filled)

    def test_get_folder_paths_empty(self):
        folder_paths = get_folder_paths(Path(self.test_dir_empty))

        self.assertTrue(folder_paths.input_files.is_dir())
        self.assertTrue(folder_paths.data_tables.is_dir())
        self.assertTrue(folder_paths.csv_results.is_dir())
        self.assertTrue(folder_paths.vtk_results.is_dir())

    def test_get_folder_paths_filled(self):
        folder_paths = get_folder_paths(Path(self.test_dir_filled))

        self.assertTrue(folder_paths.input_files.is_dir())
        self.assertTrue(folder_paths.data_tables.is_dir())
        self.assertTrue(folder_paths.csv_results.is_dir())
        self.assertTrue(folder_paths.vtk_results.is_dir())
        self.assertEqual(0, len(os.listdir(folder_paths.data_tables)))

    def test_load_input_data_from_folder(self):
        folder_path = Path(__file__).parent / "data/test_folder_cart"
        input_data = load_input_data_from_folder(folder_path)

        self.assertIsInstance(input_data.data_absolute_activity, DataAbsoluteActivity)
        self.assertIsInstance(input_data.data_mesh_info, DataMeshInfo)
        self.assertIsInstance(input_data.isotope_criteria, DataIsotopeCriteria)
