import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from f4e_radwaste.readers.filter_cells_file import read_file

EXAMPLE_FILTER_CELLS_FILE = """{
    "cells_to_include": [
        940023, 940024, 940025, 940026
    ]
}
"""
INCORRECT_FILE = """{
    "cells_to_include": {
        940023, 940024, 940025, 940026
    }
}
"""


class FilterCellsFileTests(unittest.TestCase):
    def test_filter_cells_file_correct(self):
        with patch("builtins.open", return_value=StringIO(EXAMPLE_FILTER_CELLS_FILE)):
            result = read_file(Path("file"))

        self.assertListEqual([940023, 940024, 940025, 940026], result)
