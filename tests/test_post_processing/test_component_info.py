import unittest

import pandas as pd

from f4e_radwaste.constants import KEY_VOXEL, KEY_MATERIAL, KEY_CELL, KEY_MASS_GRAMS
from f4e_radwaste.data_formats.data_mass import DataMass
from f4e_radwaste.post_processing.calculate_dose_rates import (
    DoseCalculator,
)
from f4e_radwaste.post_processing.components_info import ComponentsInfo


class ComponentsInfoTests(unittest.TestCase):
    def setUp(self):
        # Component ids
        component_names = ["Component 1", "Component 1", "Component 3", "Component 4"]
        component_cells = [[1, 2], [3, 4], [33], [44]]
        self.component_ids = list(zip(component_names, component_cells))

        # DataMass
        data = {
            KEY_VOXEL: [1, 1, 2, 3, 3, 3],
            KEY_MATERIAL: [10, 20, 10, 40, 50, 0],
            KEY_CELL: [1, 2, 3, 4, 33, 44],
            KEY_MASS_GRAMS: [5, 10, 5, 5, 6, 0],
        }
        df = pd.DataFrame(data)
        df.set_index([KEY_VOXEL, KEY_MATERIAL, KEY_CELL], inplace=True)
        self.data_mass = DataMass(df)

        # DoseCalculator
        dose_1_m_factors = pd.Series(
            index=["He8", "Be7", "Be11", "B12", "B13", "B14"],
            data=[1.40e-08, 8.49e-10, 1.59e-08, 5.87e-10, 3.11e-09, 5.55e-08],
        )
        cdr_factors = pd.DataFrame(
            index=["He8", "Fe55", "Be11", "B12", "B13", "B14"],
            data={
                "H": [1.09e-07, 4.80e-09, 2.59e-07, 1.08e-08, 5.07e-08, 1.24e-06],
                "He": [2.17e-07, 9.53e-09, 5.07e-07, 2.11e-08, 9.98e-08, 2.41e-06],
                "Li": [2.51e-07, 1.10e-08, 5.80e-07, 2.42e-08, 1.15e-07, 2.74e-06],
            },
        )
        material_mix_1 = pd.Series(
            index=["He", "H"],
            data=[0.6, 0.4],
        )
        material_mix_2 = pd.Series(
            index=["He", "B"],
            data=[0.5, 0.5],
        )
        material_mixes_by_id = {
            10: material_mix_1,
            20: material_mix_2,
            40: material_mix_1,
            50: material_mix_1,
        }
        self.dose_calculator = DoseCalculator(
            dose_1_m_factors=dose_1_m_factors,
            cdr_factors=cdr_factors,
            element_mix_by_material_id=material_mixes_by_id,
        )

    def test_components_info_init(self):
        components_info = ComponentsInfo(
            component_ids=self.component_ids,
            data_mass=self.data_mass,
            dose_calculator=self.dose_calculator,
        )

        expected_cdr_factor_fe55_comp_1 = (0.4 * 4.80e-09 + 0.6 * 9.53e-09) * 5 / 15
        expected_cdr_factor_fe55_comp_1 += (9.53e-09 * 0.5) * 10 / 15
        self.assertAlmostEqual(
            expected_cdr_factor_fe55_comp_1, components_info.cdr_factors[0]["Fe55"]
        )
