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
KEY_LMA = "LMA"
KEY_TFA_CLASS = "tfa_class"
KEY_TFA_DECLARATION = "tfa_declaration"
KEY_LDF_DECLARATION = "ldf_declaration"

KEY_SPECIFIC_ACTIVITY = "Activity [Bq/g]"

KEY_TOTAL_SPECIFIC_ACTIVITY = "Total Activity [Bq/g]"
KEY_RELEVANT_SPECIFIC_ACTIVITY = "Relevant Activity [Bq/g]"
KEY_IRAS = "IRAS"
KEY_RADWASTE_CLASS = "Radwaste class"
KEY_CDR = "Contact dose rate [Sv/h]"
KEY_DOSE_1_METER = "Dose 1 meter [Sv/h]"
TYPE_TFA = 0
TYPE_A = 1
TYPE_B = 2


class CoordinateType(Enum):
    CARTESIAN = "cartesian"
    CYLINDRICAL = "cylindrical"
