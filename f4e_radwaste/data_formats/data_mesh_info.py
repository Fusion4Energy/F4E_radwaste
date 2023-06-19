from dataclasses import dataclass
from typing import Optional

import numpy as np

from f4e_radwaste.constants import CoordinateType
from f4e_radwaste.data_formats.data_mass import DataMass


@dataclass
class DataMeshInfo:
    coordinates: CoordinateType
    vector_i: np.array
    vector_j: np.array
    vector_k: np.array
    data_mass: Optional[DataMass] = None
    origin: Optional[np.array] = None
    axis: Optional[np.array] = None
    vec: Optional[np.array] = None

    def __post_init__(self):
        if self.coordinates == CoordinateType.CYLINDRICAL:
            if any(param is None for param in [self.origin, self.axis, self.vec]):
                raise TypeError("Cylindrical mesh should have origin, axis, and vec!")
        else:
            if any(param is not None for param in [self.origin, self.axis, self.vec]):
                raise TypeError("Cartesian mesh should NOT have origin, axis, and vec!")
