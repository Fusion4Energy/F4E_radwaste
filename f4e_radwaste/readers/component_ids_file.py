"""
Reader for the JSON file containing the division of components by cell ids. The format
of the JSON is as follows:
[
    ["Component_name_1", [1,2,3,4,5,6]],
    ["Component_name_1", [123]],
    ["Component_name_1", [22,2322]]
]
"""
import json
from typing import List

FILENAME = "components.json"


def get_component_ids_from_folder(path_to_folder) -> List[List]:
    """
    Returns a list, every item represents a component as a tuple.
    Every tuple contains as first item the component name and as second item a list of
    the cell ids that form that component.
    """
    with open(path_to_folder / FILENAME, "r") as infile:
        component_ids = json.load(infile)
    return component_ids


def get_relevant_cells_from_components(component_ids: List[List]) -> List[int]:
    filter_cells = []
    for _component_name, cell_ids in component_ids:
        for cell_id in cell_ids:
            if cell_id not in filter_cells:
                filter_cells.append(cell_id)
    return filter_cells
