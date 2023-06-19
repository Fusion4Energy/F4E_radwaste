from enum import Enum

KEY_TIME = "Time"
KEY_VOXEL = "Voxel"
KEY_CELL = "Cell"
KEY_ISOTOPE = "Isotope"
KEY_ABSOLUTE_ACTIVITY = "Activity [Bq]"
KEY_MATERIAL = "Material"
KEY_MASS_GRAMS = "Mass [g]"


class CoordinateType(Enum):
    CARTESIAN = "cartesian"
    CYLINDRICAL = "cylindrical"
