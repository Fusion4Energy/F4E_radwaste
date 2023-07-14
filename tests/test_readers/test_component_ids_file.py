import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from f4e_radwaste.readers.component_ids_file import (
    get_component_ids_from_folder,
    get_relevant_cells_from_components,
)

EXAMPLE_COMPONENT_IDS_FILE = """[
    ["Component_name_1", [1,2,3,4,5,6]],
    ["Component_name_1", [123]],
    ["Component_name_1", [22,2322]]
]
"""


class ComponentIdsFileTests(unittest.TestCase):
    def test_get_component_ids_from_folder(self):
        with patch("builtins.open", return_value=StringIO(EXAMPLE_COMPONENT_IDS_FILE)):
            result = get_component_ids_from_folder(Path("file"))

        expected = [
            ["Component_name_1", [1, 2, 3, 4, 5, 6]],
            ["Component_name_1", [123]],
            ["Component_name_1", [22, 2322]],
        ]

        self.assertListEqual(expected, result)

    def test_get_relevant_cells_from_components(self):
        component_ids = [
            ["Component_name_1", [1, 2, 3, 4, 5, 6]],
            ["Component_name_1", [123]],
            ["Component_name_1", [22, 2322]],
        ]
        result = get_relevant_cells_from_components(component_ids)
        expected = [1, 2, 3, 4, 5, 6, 123, 22, 2322]

        self.assertListEqual(result, expected)
