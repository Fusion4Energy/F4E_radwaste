import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from f4e_radwaste.readers.component_ids_file import get_component_ids_from_file

EXAMPLE_COMPONENT_IDS_FILE = """[
    ["Component_name_1", [1,2,3,4,5,6]],
    ["Component_name_1", [123]],
    ["Component_name_1", [22,2322]]
]
"""


class ComponentIdsFileTests(unittest.TestCase):
    def test_get_component_ids_from_file(self):
        with patch("builtins.open", return_value=StringIO(EXAMPLE_COMPONENT_IDS_FILE)):
            result = get_component_ids_from_file(Path("file"))

        expected = [
            ["Component_name_1", [1, 2, 3, 4, 5, 6]],
            ["Component_name_1", [123]],
            ["Component_name_1", [22, 2322]],
        ]

        self.assertListEqual(expected, result)
