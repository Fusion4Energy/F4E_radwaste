import os
import shutil
from pathlib import Path

from f4e_radwaste.constants import (
    FOLDER_NAME_DATA_TABLES,
    FOLDER_NAME_CSV,
    FOLDER_NAME_VTK,
    FILENAME_DGS_DATA,
    FILENAME_MESHINFO,
)
from f4e_radwaste.post_processing.calculate_dose_rates import DoseCalculator
from f4e_radwaste.post_processing.components_info import ComponentsInfo
from f4e_radwaste.post_processing.folder_paths import FolderPaths
from f4e_radwaste.post_processing.input_data import InputData
from f4e_radwaste.readers import (
    filter_cells_file,
    dgs_file,
    mesh_info_file,
    isotope_criteria_file,
)
from f4e_radwaste.readers.aux_material_file import read_element_mixes_of_materials
from f4e_radwaste.readers.component_ids_file import get_component_ids_from_folder
from f4e_radwaste.readers.dose_matrix_file import (
    read_dose_1_m_factors,
    read_contact_dose_rate_factors,
)


class StandardProcessor:
    def __init__(self, input_folder_path: Path):
        self.folder_paths = create_folder_paths(input_folder_path)
        self.input_data = load_input_data_from_folder(input_folder_path)

    def process(self):
        """Process and save the data grouped by material in VTK and CSV"""
        self.input_data.save_data_tables(self.folder_paths)
        self.process_input_data_by_material()

    def process_input_data_by_material(self):
        decay_times = self.input_data.data_absolute_activity.decay_times
        materials = self.input_data.data_mesh_info.data_mass.materials

        for decay_time in decay_times:
            for material in materials:
                output = self.input_data.try_get_mesh_output_by_time_and_materials(
                    decay_time=decay_time, materials=[material]
                )

                if output is None:
                    continue

                output.save(self.folder_paths)

            output = self.input_data.try_get_mesh_output_by_time_and_materials(
                decay_time
            )
            output.save(self.folder_paths)


class FilteredProcessor(StandardProcessor):
    def __init__(self, input_folder_path: Path):
        super().__init__(input_folder_path)

        # Apply the cell filtering
        cells_to_include = filter_cells_file.read_file(self.folder_paths.input_files)
        self.input_data.apply_filter_include_cells(cells_to_include)


class ByComponentProcessor(StandardProcessor):
    def __init__(self, input_folder_path: Path):
        super().__init__(input_folder_path)

        self.dose_calculator = DoseCalculator(
            dose_1_m_factors=read_dose_1_m_factors(),
            cdr_factors=read_contact_dose_rate_factors(),
            element_mix_by_material_id=read_element_mixes_of_materials(
                self.folder_paths.input_files
            ),
        )
        self.components_info = ComponentsInfo(
            component_ids=get_component_ids_from_folder(self.folder_paths.input_files),
            data_mass=self.input_data.data_mesh_info.data_mass,
            dose_calculator=self.dose_calculator,
        )

        # Filter in only the cells that appear in the components for performance
        self.input_data.apply_filter_include_cells(
            self.components_info.get_all_cell_ids()
        )

    def process(self):
        self.process_input_data_by_components()

    def process_input_data_by_components(self):
        decay_times = self.input_data.data_absolute_activity.decay_times

        for decay_time in decay_times:
            component_output = self.input_data.get_component_output_by_time_and_ids(
                decay_time=decay_time,
                components_info=self.components_info,
                dose_calculator=self.dose_calculator,
            )

            component_output.save(self.folder_paths)


def create_folder_paths(input_folder_path: Path) -> FolderPaths:
    data_tables_path = input_folder_path / FOLDER_NAME_DATA_TABLES
    csv_results_path = input_folder_path / FOLDER_NAME_CSV
    vtk_results_path = input_folder_path / FOLDER_NAME_VTK

    # Ensure that the folders exist and are empty
    sub_folders = [data_tables_path, csv_results_path, vtk_results_path]
    for sub_folder in sub_folders:
        if sub_folder.is_dir():
            shutil.rmtree(sub_folder)
        os.mkdir(sub_folder)

    return FolderPaths(
        input_files=input_folder_path,
        data_tables=data_tables_path,
        csv_results=csv_results_path,
        vtk_results=vtk_results_path,
    )


def load_input_data_from_folder(folder_path: Path) -> InputData:
    data_absolute_activity = dgs_file.read_file(folder_path / FILENAME_DGS_DATA)
    data_mesh_info = mesh_info_file.read_file(folder_path / FILENAME_MESHINFO)
    isotope_criteria = isotope_criteria_file.read_file()

    return InputData(
        data_absolute_activity,
        data_mesh_info,
        isotope_criteria,
    )
