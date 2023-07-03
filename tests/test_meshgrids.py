import unittest

import numpy as np
import pandas as pd

from f4e_radwaste.constants import (
    KEY_VOXEL,
    KEY_MASS_GRAMS,
    CoordinateType,
    KEY_MATERIAL,
    KEY_CELL,
)
from f4e_radwaste.data_formats.data_mass import DataMass
from f4e_radwaste.data_formats.data_mesh_activity import DataMeshActivity
from f4e_radwaste.data_formats.data_mesh_info import DataMeshInfo
from f4e_radwaste.meshgrids import (
    create_cartesian_grid,
    create_cylindrical_grid_z_axis,
    create_cylindrical_grid,
    create_grid,
    correct_theta_vector,
    extend_theta_intervals,
)


class MeshgridsTests(unittest.TestCase):
    def setUp(self) -> None:
        # DataMeshActivity
        data = {
            KEY_VOXEL: [1, 2, 3, 4],
            KEY_MASS_GRAMS: [10, 20, 30, 40],
            "H3": [110, 120, 130, 140],
            "Fe55": [910, 920, 930, 940],
        }
        df = pd.DataFrame(data)
        df.set_index([KEY_VOXEL], inplace=True)
        self.data_mesh_activity = DataMeshActivity(df)

        # DataMeshInfo
        data = {
            KEY_VOXEL: [1, 1, 2, 3, 4],
            KEY_MATERIAL: [10, 20, 10, 40, 10],
            KEY_CELL: [11, 12, 11, 14, 90],
            KEY_MASS_GRAMS: [2.34, 3.13, 1.09, 10.2, 77],
        }
        df = pd.DataFrame(data)
        df.set_index([KEY_VOXEL, KEY_MATERIAL, KEY_CELL], inplace=True)
        data_mass = DataMass(df)
        self.data_mesh_info_cart = DataMeshInfo(
            coordinates=CoordinateType.CARTESIAN,
            data_mass=data_mass,
            vector_i=np.array([0, 1, 2]),
            vector_j=np.array([10, 20, 30]),
            vector_k=np.array([5, 6, 7]),
        )
        self.data_mesh_info_cyl = DataMeshInfo(
            coordinates=CoordinateType.CYLINDRICAL,
            data_mass=data_mass,
            vector_i=np.array([0, 1, 2]),
            vector_j=np.array([5, 6, 7]),
            # vector_k=np.array([0, 0.5, 1]),
            vector_k=np.array([0, 0.5, 1]),
            origin=np.array([0, 0, 0]),
            axis=np.array([0, 0, 1]),
            vec=np.array([1, 0, 0]),
        )

    def test_create_cartesian_grid(self):
        grid = create_cartesian_grid(
            vector_i=[0, 1, 2], vector_j=[10, 20, 30], vector_k=[5, 6, 7]
        )

        self.assertEqual(8, grid.n_cells)
        # Center of cell 0
        self.assertListEqual([0.5, 15, 5.5], grid.extract_cells(0).center)
        # Center of cell 1
        self.assertListEqual([1.5, 15, 5.5], grid.extract_cells(1).center)
        # Center of cell 7
        self.assertListEqual([1.5, 25, 6.5], grid.extract_cells(7).center)

    def test_create_cylindrical_grid_z_axis(self):
        grid = create_cylindrical_grid_z_axis(
            vector_i=[0, 1, 2],
            vector_j=[10, 20, 30],
            vector_k_revolutions=[0, 0.25, 0.5],
        )

        self.assertEqual(8, grid.n_cells)
        # Center of cell 0
        np.testing.assert_array_almost_equal(
            [0.5, 0.5, 15], grid.extract_cells(0).center
        )
        # Center of cell 1
        np.testing.assert_array_almost_equal([1, 1, 15], grid.extract_cells(1).center)
        # Center of cell 2
        np.testing.assert_array_almost_equal(
            [-0.5, 0.5, 15], grid.extract_cells(2).center
        )
        # Center of cell 7
        np.testing.assert_array_almost_equal([-1, 1, 25], grid.extract_cells(7).center)

    @staticmethod
    def test_extend_theta_intervals_1_initial_int():
        extended_vector = extend_theta_intervals([0, 1], 4)
        np.testing.assert_array_almost_equal([0, 0.25, 0.5, 0.75, 1], extended_vector)

    @staticmethod
    def test_extend_theta_intervals_2_initial_ints():
        extended_vector = extend_theta_intervals([0, 0.5, 1], 4)
        np.testing.assert_array_almost_equal([0, 0.25, 0.5, 0.75, 1], extended_vector)

    def test_extend_theta_intervals_3_initial_ints(self):
        with self.assertRaises(ValueError):
            extend_theta_intervals([0, 0.2, 0.4, 0.6])

    @staticmethod
    def test_correct_theta_vector():
        wrong_vector = [-0.0000000001, 0.5, 0.9999999999995]
        corrected_vector = correct_theta_vector(wrong_vector)
        np.testing.assert_array_equal([0, 0.5, 1], corrected_vector)

    def test_create_cylindrical_grid_rotated(self):
        vector_i = [0, 10]
        vector_j = [0, 20]
        vector_k = [1e-25, 1 + 1e-25]
        origin = [100, 100, 100]
        axis = [1, 0, 0]

        grid = create_cylindrical_grid(
            vector_i, vector_j, vector_k, origin=origin, axis=axis
        )

        np.testing.assert_array_almost_equal([110.0, 100.0, 100.0], grid.center)
        self.assertEqual(20, grid.n_cells)

    def test_create_grid_for_cartesian(self):
        grid = create_grid(self.data_mesh_info_cart, self.data_mesh_activity)

        # R2S indexing starts at 1 and goes Z-Y-X
        # Value at cell 1 (R2S indexing)
        cell_index = grid.find_closest_cell([0.5, 15, 5.5])
        self.assertAlmostEqual(10, grid[KEY_MASS_GRAMS][cell_index])
        # Value at cell 2 (R2S indexing)
        cell_index = grid.find_closest_cell([0.5, 15, 6.5])
        self.assertAlmostEqual(20, grid[KEY_MASS_GRAMS][cell_index])
        # Value at cell 3 (R2S indexing)
        cell_index = grid.find_closest_cell([0.5, 25, 5.5])
        self.assertAlmostEqual(30, grid[KEY_MASS_GRAMS][cell_index])
        # Value at cell 4 (R2S indexing)
        cell_index = grid.find_closest_cell([0.5, 25, 6.5])
        self.assertAlmostEqual(40, grid[KEY_MASS_GRAMS][cell_index])

    def test_create_grid_for_cylindrical_extended_thetas(self):
        grid = create_grid(self.data_mesh_info_cyl, self.data_mesh_activity)

        # R2S indexing starts at 1 and goes Z-THETA-R supposedly, to make this work
        #  I am really using a THETA-Z-R in the R2S voxels
        # Value at cell 1 (R2S indexing)
        cell_index = grid.find_closest_cell([0, 0.5, 5.5])
        self.assertAlmostEqual(10, grid[KEY_MASS_GRAMS][cell_index])
        # Value at cell 2 (R2S indexing)
        cell_index = grid.find_closest_cell([0, 0 - 0.5, 5.5])
        self.assertAlmostEqual(20, grid[KEY_MASS_GRAMS][cell_index])
        # Value at cell 3 (R2S indexing)
        cell_index = grid.find_closest_cell([0, 0.5, 6.5])
        self.assertAlmostEqual(30, grid[KEY_MASS_GRAMS][cell_index])
        # Value at cell 4 (R2S indexing)
        cell_index = grid.find_closest_cell([0, -0.5, 6.5])
        self.assertAlmostEqual(40, grid[KEY_MASS_GRAMS][cell_index])

    def test_create_grid_for_cylindrical_simple(self):
        # DataMeshActivity
        data = {
            KEY_VOXEL: [1, 2, 3, 4, 5, 6, 7, 8],
            KEY_MASS_GRAMS: [10, 20, 30, 40, 50, 60, 70, 80],
        }
        df = pd.DataFrame(data)
        df.set_index([KEY_VOXEL], inplace=True)
        data_mesh_activity = DataMeshActivity(df)

        # DataMeshInfo
        data = {
            KEY_VOXEL: [1, 1, 2, 3, 4],
            KEY_MATERIAL: [10, 20, 10, 40, 10],
            KEY_CELL: [11, 12, 11, 14, 90],
            KEY_MASS_GRAMS: [2.34, 3.13, 1.09, 10.2, 77],
        }
        df = pd.DataFrame(data)
        df.set_index([KEY_VOXEL, KEY_MATERIAL, KEY_CELL], inplace=True)
        data_mass = DataMass(df)
        data_mesh_info_cyl = DataMeshInfo(
            coordinates=CoordinateType.CYLINDRICAL,
            data_mass=data_mass,
            vector_i=np.array([0, 1, 2]),
            vector_j=np.array([5, 6, 7]),
            # vector_k=np.array([0, 0.5, 1]),
            vector_k=np.array([0, 0.2, 0.4, 0.6]),
            origin=np.array([0, 0, 0]),
            axis=np.array([0, 0, 1]),
            vec=np.array([1, 0, 0]),
        )

        grid = create_grid(data_mesh_info_cyl, data_mesh_activity)

        # R2S indexing starts at 1 and goes Z-THETA-R supposedly, to make this work
        #  I am really using a THETA-Z-R in the R2S voxels
        cell_index = grid.find_closest_cell([0, 1.5, 5.5])
        self.assertAlmostEqual(80, grid[KEY_MASS_GRAMS][cell_index])
