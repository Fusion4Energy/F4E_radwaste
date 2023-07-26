from enum import Enum

FOLDER_NAME_DATA_TABLES = "data_tables"
FOLDER_NAME_CSV = "csv_files"
FOLDER_NAME_VTK = "vtk_files"

FILENAME_MESHINFO = "meshinfo"
FILENAME_DGS_DATA = "DGSdata.dat"

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
KEY_DOSE_1_METER = "Dose 1 meter [Sv/h/g]"
TYPE_TFA_INT = 0
TYPE_A_INT = 1
TYPE_B_INT = 2
TYPE_TFA_STR = "TFA"
TYPE_A_STR = "Type A"
TYPE_B_STR = "Type B"


class CoordinateType(Enum):
    CARTESIAN = "cartesian"
    CYLINDRICAL = "cylindrical"


def get_radwaste_class_str_from_int(value: int) -> str:
    if value == TYPE_TFA_INT:
        return TYPE_TFA_STR
    if value == TYPE_A_INT:
        return TYPE_A_STR
    if value == TYPE_B_INT:
        return TYPE_B_STR
    raise ValueError(
        "The only acceptable radwaste class values in int form are 0, 1 and 2..."
    )
