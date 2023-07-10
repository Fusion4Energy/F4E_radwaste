import os
import shutil
from pathlib import Path

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
from f4e_radwaste.readers.component_ids_file import (
    get_component_ids_from_folder,
    get_relevant_cells_from_components,
)

FILENAME_MESHINFO = "meshinfo"
FILENAME_DGS_DATA = "DGSdata.dat"
PATH_TO_CRITERIA_FILE = Path(__file__).parent / "resources/criteria.json"
FOLDER_NAME_DATA_TABLES = "data_tables"
FOLDER_NAME_CSV = "csv_files"
FOLDER_NAME_VTK = "vtk_files"


def standard_process(input_folder_path: Path):
    # Get the data
    folder_paths = get_folder_paths(input_folder_path)
    input_data = load_input_data_from_folder(folder_paths.input_files)

    # Save the data tables before formatting
    input_data.save_data_tables(folder_paths)

    # Process and save the data grouped by material in VTK and CSV
    process_input_data_by_material(input_data, folder_paths)


def filtered_process(input_folder_path: Path):
    # Get the data
    folder_paths = get_folder_paths(input_folder_path)
    input_data = load_input_data_from_folder(folder_paths.input_files)
    cells_to_include = filter_cells_file.read_file(folder_paths.input_files)

    # Apply the filter
    input_data.apply_filter_include_cells(cells_to_include)

    # Save the data tables before formatting
    input_data.save_data_tables(folder_paths)

    # Process and save the data grouped by material in VTK and CSV
    process_input_data_by_material(input_data, folder_paths)


def by_component_process(input_folder_path: Path):
    # Get the data
    folder_paths = get_folder_paths(input_folder_path)
    input_data = load_input_data_from_folder(folder_paths.input_files)
    component_ids = get_component_ids_from_folder(folder_paths.input_files)

    # Filter in only the cells that appear in the components for performance reasons
    cells_to_include = get_relevant_cells_from_components(component_ids)
    input_data.apply_filter_include_cells(cells_to_include)

    # Process and save the data grouped by component in CSV
    process_input_data_by_components(input_data, folder_paths, component_ids)


def get_folder_paths(input_folder_path: Path) -> FolderPaths:
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
    isotope_criteria = isotope_criteria_file.read_file(PATH_TO_CRITERIA_FILE)
    return InputData(data_absolute_activity, data_mesh_info, isotope_criteria)


if __name__ == "__main__":
    filtered_process(Path(r"D:\WORK\tryingSimple\tests\old_data\ivvs_cart"))
