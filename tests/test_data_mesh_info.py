import unittest

import numpy as np
import pandas as pd

from f4e_radwaste.constants import (
    CoordinateType,
    KEY_VOXEL,
    KEY_MATERIAL,
    KEY_CELL,
    KEY_MASS_GRAMS,
)
from f4e_radwaste.data_formats.data_mass import DataMass
from f4e_radwaste.data_formats.data_mesh_info import DataMeshInfo


class DataMeshInfoTests(unittest.TestCase):
    def setUp(self):
        # Crate a DataMass instance to use when instancing DataMeshInfo
        data = {
            KEY_VOXEL: [1, 1, 2, 3],
            KEY_MATERIAL: [10, 20, 10, 40],
            KEY_CELL: [11, 12, 11, 14],
            KEY_MASS_GRAMS: [2.34, 3.13, 1.09, 10.2],
        }
        df = pd.DataFrame(data)
        df.set_index([KEY_VOXEL, KEY_MATERIAL, KEY_CELL], inplace=True)

        # Initialize the validator with the DataFrame
        self.data_mass = DataMass(df)

    def test_initialize_cartesian_coordinates(self):
        data_mesh_info = DataMeshInfo(
            coordinates=CoordinateType.CARTESIAN,
            data_mass=self.data_mass,
            vector_i=np.array([1, 0, 0]),
            vector_j=np.array([1, 0, 0]),
            vector_k=np.array([1, 0, 0]),
        )
        self.assertIsInstance(data_mesh_info, DataMeshInfo)
        self.assertIsInstance(data_mesh_info.data_mass, DataMass)

    def test_initialize_cartesian_coordinates_with_invalid_parameters(self):
        with self.assertRaises(TypeError):
            DataMeshInfo(
                coordinates=CoordinateType.CARTESIAN,
                data_mass=self.data_mass,
                vector_i=np.array([1, 0, 0]),
                vector_j=np.array([1, 0, 0]),
                vector_k=np.array([1, 0, 0]),
                origin=np.array([1, 0, 0]),
                axis=np.array([1, 0, 0]),
                vec=np.array([1, 0, 0]),
            )

    def test_initialize_cylindrical_coordinates(self):
        data_mesh_info = DataMeshInfo(
            coordinates=CoordinateType.CYLINDRICAL,
            data_mass=self.data_mass,
            vector_i=np.array([1, 0, 0]),
            vector_j=np.array([1, 0, 0]),
            vector_k=np.array([1, 0, 0]),
            origin=np.array([1, 0, 0]),
            axis=np.array([1, 0, 0]),
            vec=np.array([1, 0, 0]),
        )
        self.assertIsInstance(data_mesh_info, DataMeshInfo)
        self.assertIsInstance(data_mesh_info.data_mass, DataMass)

    def test_initialize_cylindrical_coordinates_with_invalid_parameters(self):
        with self.assertRaises(TypeError):
            DataMeshInfo(
                coordinates=CoordinateType.CYLINDRICAL,
                data_mass=self.data_mass,
                vector_i=np.array([1, 0, 0]),
                vector_j=np.array([1, 0, 0]),
                vector_k=np.array([1, 0, 0]),
            )
