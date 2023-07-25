import os
import shutil
from pathlib import Path

from f4e_radwaste.post_processing.calculate_dose_rates import DoseCalculator
from f4e_radwaste.post_processing.components_info import ComponentsInfo
from f4e_radwaste.post_processing.folder_paths import FolderPaths
from f4e_radwaste.post_processing.input_data import InputData
from f4e_radwaste.post_processing.post_processing import (
    process_input_data_by_material,
    process_input_data_by_components,
)
from f4e_radwaste.readers import (
    dgs_file,
    mesh_info_file,
    isotope_criteria_file,
    filter_cells_file,
)
from f4e_radwaste.readers.aux_material_file import read_element_mixes_of_materials
from f4e_radwaste.readers.component_ids_file import (
    get_component_ids_from_folder,
    get_relevant_cells_from_components,
)
from f4e_radwaste.readers.dose_matrix_file import (
    read_dose_1_m_factors,
    read_contact_dose_rate_factors,
)


# def standard_process(input_folder_path: Path):
#     # Get the data
#     folder_paths = get_folder_paths(input_folder_path)
#     input_data = load_input_data_from_folder(folder_paths.input_files)
#
#     # Save the data tables before formatting
#     input_data.save_data_tables(folder_paths)
#
#     # Process and save the data grouped by material in VTK and CSV
#     process_input_data_by_material(input_data, folder_paths)
#
#
# def filtered_process(input_folder_path: Path):
#     # Get the data
#     folder_paths = get_folder_paths(input_folder_path)
#     input_data = load_input_data_from_folder(folder_paths.input_files)
#     cells_to_include = filter_cells_file.read_file(folder_paths.input_files)
#
#     # Apply the filter
#     input_data.apply_filter_include_cells(cells_to_include)
#
#     # Save the data tables before formatting
#     input_data.save_data_tables(folder_paths)
#
#     # Process and save the data grouped by material in VTK and CSV
#     process_input_data_by_material(input_data, folder_paths)
#
#
# def by_component_process(input_folder_path: Path):
#     # Get the data
#     folder_paths = get_folder_paths(input_folder_path)
#     input_data = load_input_data_from_folder(folder_paths.input_files)
#     component_ids = get_component_ids_from_folder(folder_paths.input_files)
#     dose_calculator = DoseCalculator(
#         dose_1_m_factors=read_dose_1_m_factors(PATH_TO_DOSE_FACTORS_FILE),
#         cdr_factors=read_contact_dose_rate_factors(PATH_TO_DOSE_FACTORS_FILE),
#         element_mix_by_material_id=read_element_mixes_of_materials(
#             folder_paths.input_files
#         ),
#     )
#
#     # Filter in only the cells that appear in the components for performance reasons
#     cells_to_include = get_relevant_cells_from_components(component_ids)
#     input_data.apply_filter_include_cells(cells_to_include)
#
#     # Process and save the data grouped by component in CSV
#     process_input_data_by_components(
#         input_data, folder_paths, component_ids, dose_calculator
#     )


if __name__ == "__main__":
    by_component_process(Path(r"D:\WORK\tryingSimple\tests\old_data\ivvs_cart"))
