import pandas as pd
import re

from f4e_radwaste.constants import (
    KEY_TIME,
    KEY_VOXEL,
    KEY_CELL,
    KEY_ISOTOPE,
    KEY_ABSOLUTE_ACTIVITY,
)
from f4e_radwaste.data_formats.data_absolute_activity import DataAbsoluteActivity


def read_file(file_path) -> DataAbsoluteActivity:
    """
    Parses the DGS.dat file and returns an instance of AbsoluteActivity. The activity
    is given as Bq (it was calculated as Bq/cm3 * partial cell volume in the voxel).
    """
    with open(file_path, "r", encoding="utf-8") as infile:
        # Skip the first line: " Photon Isotope"
        next(infile)
        # Read the number of decay times: "Number of decay times:         2"
        number_decay_times = int(next(infile).split()[-1])
        # Read all the indexes that have non-zero results
        data = _read_results(infile, number_decay_times)

    dgs_dataframe = pd.DataFrame(data)
    del data  # memory performance reasons

    # Set the format to that of DataAbsoluteActivity
    index_columns = [KEY_TIME, KEY_VOXEL, KEY_CELL, KEY_ISOTOPE]
    dgs_dataframe.set_index(index_columns, inplace=True)
    fix_isotope_names(dgs_dataframe)

    return DataAbsoluteActivity(dgs_dataframe)


def _read_results(infile, number_decay_times):
    data = {
        KEY_TIME: [],
        KEY_VOXEL: [],
        KEY_CELL: [],
        KEY_ISOTOPE: [],
        KEY_ABSOLUTE_ACTIVITY: [],
    }

    # Read each line in a loop
    for line in infile:
        if line.startswith(" Case:"):
            # e.g. ' Case:         5808  Nmat:            2'
            voxel_index = int(re.findall(r"\d+", line)[0])
            next(infile)  # Skip the line: ' Cells: \n'
            cell_ids = [int(x) for x in next(infile).split()]
            next(infile)  # Skip the line: ' Volumes: \n'
            # Volume in cm3 of each material cell inside the voxel
            volumes = [float(x) for x in next(infile).split()]

            for _time_index in range(number_decay_times):
                # 'Time  1.000E+05 S'
                decay_time = float(next(infile).split()[1])

                for cell_id, volume in zip(cell_ids, volumes):
                    next(infile)  # Skip the line: 'Number of materials:         20'
                    isotope_names = next(infile).split()
                    isotope_activities = [float(x) for x in next(infile).split()]

                    for isotope, activity in zip(isotope_names, isotope_activities):
                        data[KEY_TIME].append(decay_time)
                        data[KEY_VOXEL].append(voxel_index)
                        data[KEY_CELL].append(cell_id)
                        data[KEY_ISOTOPE].append(isotope)
                        data[KEY_ABSOLUTE_ACTIVITY].append(activity * volume)

    return data


def fix_isotope_names(dataframe: pd.DataFrame):
    """
    Adapt the name of the isotopes of the DGS file to the formatting of criteria.json
    """
    isotope_index = dataframe.index.names.index(KEY_ISOTOPE)
    current_isotope_names = dataframe.index.levels[isotope_index].values

    corrected_names = []
    for name in current_isotope_names:
        name = name.capitalize()
        if name[-2:] == "m1":
            name = name[:-1]
        elif name[-2:] == "m2":
            name = name[:-2] + "n"
        corrected_names.append(name)

    dataframe.index = dataframe.index.set_levels(corrected_names, level=KEY_ISOTOPE)
