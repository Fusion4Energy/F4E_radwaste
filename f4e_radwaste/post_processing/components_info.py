from typing import List

from f4e_radwaste.data_formats.data_mass import DataMass
from f4e_radwaste.post_processing.calculate_dose_rates import DoseCalculator


class ComponentsInfo:
    def __init__(
        self,
        component_ids: List[List],
        data_mass: DataMass,
        dose_calculator: DoseCalculator,
    ):
        self.names, self.cell_ids = zip(*component_ids)

        mat_id_proportions = data_mass.calculate_material_id_proportions(self.cell_ids)

        self.cdr_factors = dose_calculator.calculate_cdr_factors_list(
            material_id_proportions=mat_id_proportions
        )
