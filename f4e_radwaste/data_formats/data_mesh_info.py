import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np

from f4e_radwaste.constants import CoordinateType
from f4e_radwaste.data_formats.data_mass import DataMass


@dataclass
class DataMeshInfo:
    coordinates: CoordinateType
    vector_i: np.ndarray
    vector_j: np.ndarray
    vector_k: np.ndarray
    data_mass: Optional[DataMass] = None
    origin: Optional[np.ndarray] = None
    axis: Optional[np.ndarray] = None
    vec: Optional[np.ndarray] = None

    def __post_init__(self):
        # Validate the type of coordinates
        if self.coordinates == CoordinateType.CYLINDRICAL:
            if any(param is None for param in [self.origin, self.axis, self.vec]):
                raise TypeError("Cylindrical mesh should have origin, axis, and vec!")
        else:
            if any(param is not None for param in [self.origin, self.axis, self.vec]):
                raise TypeError("Cartesian mesh should NOT have origin, axis, and vec!")

    def save(self, folder_path: Path):
        json_data = {
            "coordinates": self.coordinates.value,
            "vector_i": self.vector_i.tolist(),
            "vector_j": self.vector_j.tolist(),
            "vector_k": self.vector_k.tolist(),
        }
        if self.coordinates == CoordinateType.CYLINDRICAL:
            json_data["origin"] = self.origin.tolist()
            json_data["axis"] = self.axis.tolist()
            json_data["vec"] = self.vec.tolist()

        with open(folder_path / "DataMeshInfo.json", "w") as infile:
            json.dump(json_data, infile)

        if self.data_mass is not None:
            self.data_mass.save_dataframe_to_hdf5(folder_path)

    @classmethod
    def load(cls, folder_path: Path):
        data_mass = DataMass.load(folder_path)
        with open(folder_path / "DataMeshInfo.json", "r") as infile:
            json_data = json.load(infile)
        coordinates = CoordinateType(json_data["coordinates"])
        if coordinates == CoordinateType.CARTESIAN:
            return DataMeshInfo(
                coordinates=coordinates,
                data_mass=data_mass,
                vector_i=np.array(json_data["vector_i"]),
                vector_j=np.array(json_data["vector_j"]),
                vector_k=np.array(json_data["vector_k"]),
            )
        return DataMeshInfo(
            coordinates=coordinates,
            data_mass=data_mass,
            vector_i=np.array(json_data["vector_i"]),
            vector_j=np.array(json_data["vector_j"]),
            vector_k=np.array(json_data["vector_k"]),
            origin=np.array(json_data["origin"]),
            axis=np.array(json_data["axis"]),
            vec=np.array(json_data["vec"]),
        )
