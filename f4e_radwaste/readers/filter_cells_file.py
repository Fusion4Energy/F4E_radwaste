"""
File to read the JSON file that contains the list of cells to include in the analysis
in a filtered post-process. The file should have the following format:
{
    "cells_to_include": [
        940023, 940024, 940025, 940026, ...
    ]
}
"""

import json
from pathlib import Path

KEY_CELLS_TO_INCLUDE = "cells_to_include"


def read_file(path: Path) -> list[int]:
    """
    Returns the list of cells that should be included in the analysis.
    """
    with open(path, "r") as infile:
        data = json.load(infile)

    cells_to_include = data[KEY_CELLS_TO_INCLUDE]

    return cells_to_include
