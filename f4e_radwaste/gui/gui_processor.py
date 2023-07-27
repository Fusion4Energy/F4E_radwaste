from pathlib import Path

from f4e_radwaste.data_formats.data_absolute_activity import DataAbsoluteActivity
from f4e_radwaste.data_formats.data_mesh_info import DataMeshInfo
from f4e_radwaste.helpers import format_time_seconds_to_str
from f4e_radwaste.post_processing.calculate_dose_rates import DoseCalculator
from f4e_radwaste.post_processing.input_data import InputData
from f4e_radwaste.readers import isotope_criteria_file
from f4e_radwaste.readers.aux_material_file import read_element_mixes_of_materials
from f4e_radwaste.readers.dose_matrix_file import (
    read_dose_1_m_factors,
    read_contact_dose_rate_factors,
)


class GUIProcessor:
    def __init__(self, data_tables_folder_path: Path):
        self.data_tables_folder_path: Path = data_tables_folder_path
        self.input_data: InputData = load_input_data_tables(data_tables_folder_path)
        self.dose_calculator = DoseCalculator(
            dose_1_m_factors=read_dose_1_m_factors(),
            cdr_factors=read_contact_dose_rate_factors(),
            element_mix_by_material_id=read_element_mixes_of_materials(
                data_tables_folder_path.parent
            ),
        )

        self.make_decay_times_readable_in_activity_df()

    def make_decay_times_readable_in_activity_df(self):
        decay_times = self.input_data.data_absolute_activity.decay_times
        readable_values = []
        for value_seconds in decay_times:
            readable_values.append(format_time_seconds_to_str(value_seconds))
        self.input_data.data_absolute_activity.decay_times = readable_values


def load_input_data_tables(data_tables_folder_path: Path) -> InputData:
    return InputData(
        DataAbsoluteActivity.load(data_tables_folder_path),
        DataMeshInfo.load(data_tables_folder_path),
        isotope_criteria_file.read_file(),
    )
