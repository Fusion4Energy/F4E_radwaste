from enum import Enum

KEY_TIME = "Time"
KEY_VOXEL = "Voxel"
KEY_CELL = "Cell"
KEY_ISOTOPE = "Isotope"
KEY_ABSOLUTE_ACTIVITY = "Activity [Bq]"
KEY_MATERIAL = "Material"
KEY_MASS_GRAMS = "Mass [g]"

KEY_HALF_LIFE = "half_life"
KEY_CSA_DECLARATION = "csa_declaration"
KEY_LMA = "lma"
KEY_TFA_CLASS = "tfa_class"
KEY_TFA_DECLARATION = "tfa_declaration"
KEY_LDF_DECLARATION = "ldf_declaration"

KEY_SPECIFIC_ACTIVITY = "Activity [Bq/g]"


class CoordinateType(Enum):
    CARTESIAN = "cartesian"
    CYLINDRICAL = "cylindrical"
