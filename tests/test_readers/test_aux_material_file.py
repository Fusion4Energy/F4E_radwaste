import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from f4e_radwaste.readers.aux_material_file import read_element_mixes_of_materials

# noinspection SpellCheckingInspection
EXAMPLE_AUX_MATERIAL_FILE = """DataPath /path.../common_data
CuvMsh   ../01_Neutron_transport/cuvmsk
SrcImp   srcimp
# Header lines not useful here...
CDGS     cdgs
Material Definition: 2
4 12
    30060      30070      40090      40090      50100      50110  
    60120      60130      70140      70150      80160      80170  
2.9693100e-07  3.6152121e-06  2.0931232e-03  9.9417384e-01  3.3317428e-07  1.3410666e-06  
7.3746526e-04  7.9762301e-06  7.3387256e-05  2.7382491e-07  2.0829503e-03  7.9345065e-07  
29 6
    80160      80170      80180     150310     160320     160330  
1.9761751e-05  7.5277666e-09  4.0610301e-08  6.1545366e-06  2.8237210e-05  2.2294864e-07  
Activated Cells: 3
    12700         4 8.1791200e-02
    12704         4 8.1791200e-02
    12705        29 8.5879000e-02
"""


class MCNPOutputFileTests(unittest.TestCase):
    @staticmethod
    def test_read_element_mixes_of_materials():
        expected_element_mixes = {
            4: pd.Series(
                index=["Li", "Be", "B", "C", "N", "O"],
                data=[
                    2.9693100e-07 + 3.6152121e-06,
                    2.0931232e-03 + 9.9417384e-01,
                    3.3317428e-07 + 1.3410666e-06,
                    7.3746526e-04 + 7.9762301e-06,
                    7.3387256e-05 + 2.7382491e-07,
                    2.0829503e-03 + 7.9345065e-07,
                ],
            ),
            29: pd.Series(
                index=["O", "P", "S"],
                data=[
                    1.9761751e-05 + 7.5277666e-09 + 4.0610301e-08,
                    6.1545366e-06,
                    2.8237210e-05 + 2.2294864e-07,
                ],
            ),
        }

        with patch("builtins.open", return_value=StringIO(EXAMPLE_AUX_MATERIAL_FILE)):
            result = read_element_mixes_of_materials(Path("folder"))

        pd.testing.assert_series_equal(expected_element_mixes[4], result[4])
        pd.testing.assert_series_equal(expected_element_mixes[29], result[29])
