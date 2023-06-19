import unittest
from io import StringIO
from unittest.mock import patch

import numpy as np

from f4e_radwaste.constants import (
    CoordinateType,
    KEY_MASS_GRAMS,
)
from f4e_radwaste.data_formats.data_mesh_info import DataMeshInfo
from f4e_radwaste.readers.mesh_info_file import read_file

EXAMPLE_MESHINFO_CART = """d1sune version 3.1.4 ld=05152019  probid =  08/19/22 20:11:57 
 C                                                                               

 Mesh tally number:      9014
 Average cell number per voxel:  2.00000

 Tally bin boundaries:
    X direction:   -100.00   0.00   100.00
    Y direction:   -110.00   0.00   110.00
    Z direction:   -120.00   0.00   120.00
      1   3.38693E+03    2
     309104    5.5868   110507  0.80000
     309485    1.3966      253  0.20000
      2   3.38693E+03    2
     139510    5.5868   110507  0.80000
     140711    1.3966      253  0.20000
      3   3.38693E+03    2
     139512    5.5868   110507  0.80000
     139737    1.3966      253  0.20000
      4   3.38693E+03    2
     139737    5.5868   110507  0.80000
     140656    1.3966      253  0.20000
      5   3.38693E+03    2
     140693    5.5868   110507  0.80000
     326669    1.3966      253  0.20000
      6   3.38693E+03    2
     405729    5.5868   110507  0.80000
     309485    1.3966      253  0.20000
      7   3.38693E+03    2
     309104    5.5868   110507  0.80000
     405729    1.3966      253  0.20000
      8   2.38693E+03    2
     140692    5.5868   110507  0.80000
     309485    1.3966      253  0.20000     
"""

EXAMPLE_MESHINFO_CYL = """d1sune version 3.1.4 ld=05152019  probid =  08/08/22 17:27:18 
 Aplication del R2S a un cilindro                                                

 Mesh tally number:         4
 Average cell number per voxel:  1.00000

 Tally bin boundaries:
               origin at   0.00E+00  0.00E+00  0.00E+00 axis in   0.00E+00  0.00E+00  1.00E+00 direction, VEC direction   1.00E+00  0.00E+00  0.00E+00
    R direction:      0.00      5.00     10.00
    Z direction:      0.00      3.00      6.00
    Theta direction (revolutions):0.000000006.28318531
      1   3.38693E+03    2
     309104    5.5868   110507  0.80000
     309485    1.3966      253  0.20000
      2   3.38693E+03    2
     139510    5.5868   110507  0.80000
     140711    1.3966      253  0.20000
      3   3.38693E+03    2
     139512    5.5868   110507  0.80000
     139737    1.3966      253  0.20000
      4   3.38693E+03    2
     139737    5.5868   110507  0.80000
     140656    1.3966      253  0.20000     
"""


class MeshInfoFileTests(unittest.TestCase):
    def test_read_file_cartesian(self):
        with patch("builtins.open", return_value=StringIO(EXAMPLE_MESHINFO_CART)):
            result = read_file("test.dat")

        self.assertIsInstance(result, DataMeshInfo)
        self.assertTrue(result.coordinates == CoordinateType.CARTESIAN)
        np.testing.assert_array_equal(result.vector_i, np.array([-100, 0, 100]))
        np.testing.assert_array_equal(result.vector_j, np.array([-110, 0, 110]))
        np.testing.assert_array_equal(result.vector_k, np.array([-120, 0, 120]))

        # Check two values of the DataMass instance
        result_mass_first_value = result.data_mass.get_filtered_dataframe(
            voxels=[1], cells=[309104], materials=[110507]
        )[KEY_MASS_GRAMS].values[0]
        expected_mass_first_value = 3.38693e03 * 0.80000 * 5.5868
        self.assertAlmostEqual(result_mass_first_value, expected_mass_first_value)
        result_mass_last_value = result.data_mass.get_filtered_dataframe(
            voxels=[8], cells=[309485], materials=[253]
        )[KEY_MASS_GRAMS].values[0]
        expected_mass_last_value = 2.38693e03 * 0.20000 * 1.3966
        self.assertAlmostEqual(result_mass_last_value, expected_mass_last_value)

    def test_read_file_cylindrical(self):
        with patch("builtins.open", return_value=StringIO(EXAMPLE_MESHINFO_CYL)):
            result = read_file("test.dat")

        self.assertIsInstance(result, DataMeshInfo)
        self.assertTrue(result.coordinates == CoordinateType.CYLINDRICAL)
        np.testing.assert_array_equal(result.vector_i, np.array([0, 5, 10]))
        np.testing.assert_array_equal(result.vector_j, np.array([0, 3, 6]))
        np.testing.assert_array_almost_equal(result.vector_k, np.array([0, 1]))
        np.testing.assert_array_equal(result.origin, np.array([0, 0, 0]))
        np.testing.assert_array_equal(result.axis, np.array([0, 0, 1]))
        np.testing.assert_array_equal(result.vec, np.array([1, 0, 0]))

        # Check two values of the DataMass instance
        result_mass_first_value = result.data_mass.get_filtered_dataframe(
            voxels=[1], cells=[309104], materials=[110507]
        )[KEY_MASS_GRAMS].values[0]
        expected_mass_first_value = 3.38693e03 * 0.80000 * 5.5868 / (2 * np.pi)
        self.assertAlmostEqual(result_mass_first_value, expected_mass_first_value)
        result_mass_last_value = result.data_mass.get_filtered_dataframe(
            voxels=[4], cells=[140656], materials=[253]
        )[KEY_MASS_GRAMS].values[0]
        expected_mass_last_value = 3.38693E+03 * 0.20000 * 1.3966 / (2 * np.pi)
        self.assertAlmostEqual(result_mass_last_value, expected_mass_last_value)

    def test_read_file_no_mesh_found(self):
        with self.assertRaises(ValueError):
            with patch("builtins.open", return_value=StringIO("")):
                read_file("test.dat")
