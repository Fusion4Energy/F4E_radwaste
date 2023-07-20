from pathlib import Path
from typing import Dict, TextIO, List
import re
import periodictable as pt
import pandas as pd

FILENAME = "auxUMdata.inp"

MATERIAL_SECTION_START = re.compile(r"Material Definition:\s+\d+")
MATERIAL_SECTION_END = re.compile(r"Activated Cells:\s+\d+")


def read_element_mixes_of_materials(path_to_input_folder: Path) -> Dict[int, pd.Series]:
    with open(path_to_input_folder / FILENAME, "r") as infile:
        number_of_mixes = _read_header(infile)

        element_mixes = {}
        for element_mix_index in range(number_of_mixes):
            material_id, isotope_ids, isotope_proportions = _read_isotope_mix(infile)

            element_mix = _calculate_element_mix_from_isotopes(
                isotope_ids, isotope_proportions
            )

            element_mixes[material_id] = element_mix

    return element_mixes


def _read_header(infile: TextIO) -> int:
    while True:
        line = infile.readline()
        if line == "":
            raise RuntimeError(
                f"{FILENAME} file doesn't have the line: 'Material Definition:' ..."
            )

        if MATERIAL_SECTION_START.match(line):
            return int(line.split()[-1])


def _read_isotope_mix(infile: TextIO):
    first_line = infile.readline()

    material_id, number_of_isotopes = first_line.split()
    material_id = int(material_id)
    number_of_isotopes = int(number_of_isotopes)

    isotope_ids = []
    while len(isotope_ids) < number_of_isotopes:
        line = infile.readline()
        isotope_ids += line.split()

    isotope_proportions = []
    while len(isotope_proportions) < number_of_isotopes:
        line = infile.readline()
        isotope_proportions += [float(x) for x in line.split()]

    return material_id, isotope_ids, isotope_proportions


def _calculate_element_mix_from_isotopes(
    isotope_ids: List[str], isotope_proportions: List[float]
) -> pd.Series:
    element_ids = [int(isotope_id[:-4]) for isotope_id in isotope_ids]

    # Sum the proportions of repeated elements
    ids_and_proportions = {}
    for element_id, proportion in zip(element_ids, isotope_proportions):
        if element_id in ids_and_proportions:
            ids_and_proportions[element_id] += proportion
        else:
            ids_and_proportions[element_id] = proportion

    elements = _convert_element_number_to_symbols(ids_and_proportions.keys())

    element_mix = pd.Series(index=elements, data=ids_and_proportions.values())
    element_mix = _normalize_series(element_mix)
    return element_mix


def _convert_element_number_to_symbols(element_ids):
    elements = []

    for element_id in element_ids:
        elements.append(pt.elements[element_id].symbol)

    return elements


def _normalize_series(series: pd.Series):
    return series / series.sum()
