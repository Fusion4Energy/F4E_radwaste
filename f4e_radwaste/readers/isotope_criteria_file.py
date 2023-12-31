import json
from pathlib import Path

import pandas as pd

from f4e_radwaste.constants import (
    KEY_ISOTOPE,
    KEY_HALF_LIFE,
    KEY_CSA_DECLARATION,
    KEY_LMA,
    KEY_TFA_CLASS,
    KEY_TFA_DECLARATION,
    KEY_LDF_DECLARATION,
)
from f4e_radwaste.data_formats.data_isotope_criteria import DataIsotopeCriteria

PATH_TO_CRITERIA_FILE = Path(__file__).parents[1] / "resources/criteria.json"


def read_file(path_to_criteria=PATH_TO_CRITERIA_FILE) -> DataIsotopeCriteria:
    """
    Reads the JSON file with the isotope criteria and returns an instance of
    DataIsotopeCriteria.
    """
    with open(path_to_criteria, "r", encoding="utf-8") as infile:
        criteria_file = json.load(infile)

    criteria_data = {
        KEY_ISOTOPE: [],
        KEY_HALF_LIFE: [],
        KEY_CSA_DECLARATION: [],
        KEY_LMA: [],
        KEY_TFA_CLASS: [],
        KEY_TFA_DECLARATION: [],
        KEY_LDF_DECLARATION: [],
    }

    for isotope, parameters in criteria_file.items():
        criteria_data[KEY_ISOTOPE].append(isotope)

        parameters = [float(x) if x != "" else None for x in parameters]
        criteria_data[KEY_HALF_LIFE].append(parameters[0])
        criteria_data[KEY_CSA_DECLARATION].append(parameters[1])
        criteria_data[KEY_LMA].append(parameters[2])
        criteria_data[KEY_TFA_DECLARATION].append(parameters[4])
        criteria_data[KEY_LDF_DECLARATION].append(parameters[5])

        # TFA class should be an int
        tfa_class = int(parameters[3]) if parameters[3] is not None else None
        criteria_data[KEY_TFA_CLASS].append(tfa_class)

    criteria_dataframe = pd.DataFrame(data=criteria_data)
    criteria_dataframe.set_index([KEY_ISOTOPE], inplace=True)

    return DataIsotopeCriteria(criteria_dataframe)
