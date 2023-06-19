import unittest

import numpy as np

from f4e_radwaste.constants import CoordinateType, KEY_MASS_GRAMS
from f4e_radwaste.readers.mesh_info_file import read_file


class MeshInfoFilePerformanceTests(unittest.TestCase):
    def test_read_file_cart(self):
        path_to_meshinfo_file = "data/meshinfo_cart"
        meshinfo = read_file(path_to_meshinfo_file)
        self.assertEqual(CoordinateType.CARTESIAN, meshinfo.coordinates)
        self.assertAlmostEqual(734.00, meshinfo.vector_j[0])
        self.assertEqual(18, len(meshinfo.vector_k))
        filtered_dataframe = meshinfo.data_mass.get_filtered_dataframe(
            voxels=[1],
            materials=[110],
            cells=[324896],
        )
        result_mass = filtered_dataframe[KEY_MASS_GRAMS].values[0]
        # voxel_volume * cell_proportion_of_volume * density
        expected_mass = 3.38693e03 * 0.31100 * 8.0300
        self.assertAlmostEqual(expected_mass, result_mass)
        # check that the specific cell 940030 is made of material 940001
        cells = meshinfo.data_mass.get_filtered_dataframe(materials=[940001])
        self.assertTrue(940030 in cells.reset_index()["Cell"].values)

    def test_read_file_cyl(self):
        path_to_meshinfo_file = "data/meshinfo_cyl"
        meshinfo = read_file(path_to_meshinfo_file)
        self.assertEqual(CoordinateType.CYLINDRICAL, meshinfo.coordinates)
        self.assertAlmostEqual(0.0, meshinfo.origin.sum())
        self.assertEqual(22, len(meshinfo.vector_i))
        self.assertAlmostEqual(100, meshinfo.vector_i[-1])
        self.assertAlmostEqual(550, meshinfo.vector_j[-1])
        self.assertAlmostEqual(1, meshinfo.vector_k[-1])
        filtered_dataframe = meshinfo.data_mass.get_filtered_dataframe(
            voxels=[108],
            materials=[1],
            cells=[2],
        )
        result_mass = filtered_dataframe[KEY_MASS_GRAMS].values[0]
        # from the file: voxel_volume * cell_proportion_of_volume * density
        expected_mass = 1.38791e03 * 1.00000 * 7.9300
        # WARNING: voxel_volume given by the file is wrong, it considered the theta
        # units as degrees instead of revolutions, we manually correct the mass
        expected_mass /= np.pi * 2
        self.assertAlmostEqual(expected_mass, result_mass)
        # Check that our manual correction was also right by calculating the volume
        # from zero by hand
        manual_volume = np.pi * (3.75 ** 2) * 5 * 7.9300
        # I reduce the precision, surely a harmless decimals thing
        self.assertAlmostEqual(manual_volume, expected_mass, places=2)
