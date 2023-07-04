import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from f4e_radwaste.data_formats.data_absolute_activity import DataAbsoluteActivity
from f4e_radwaste.data_formats.data_isotope_criteria import DataIsotopeCriteria
from f4e_radwaste.data_formats.data_mesh_info import DataMeshInfo
from f4e_radwaste.helpers import format_time_seconds_to_str
from f4e_radwaste.meshgrids import create_grid
from f4e_radwaste.post_processing import (
    group_data_by_time_and_materials,
    classify_waste,
)
from f4e_radwaste.readers import dgs_file, mesh_info_file, isotope_criteria_file


@dataclass
class FolderPaths:
    input_files: Path
    data_tables: Path
    csv_results: Path
    vtk_results: Path


@dataclass
class InputData:
    data_absolute_activity: DataAbsoluteActivity
    data_mesh_info: DataMeshInfo
    isotope_criteria: DataIsotopeCriteria

    def save_data_tables(self, folder_paths: FolderPaths):
        self.data_absolute_activity.save_dataframe_to_hdf5(folder_paths.data_tables)
        self.data_mesh_info.save(folder_paths.data_tables)


def standard_process(input_folder_path: Path):
    # Get the data
    folder_paths = get_folder_paths(input_folder_path)
    input_data = load_input_data_from_folder(folder_paths.input_files)

    # Save the data tables before formatting
    input_data.save_data_tables(folder_paths)

    # Process and save the data grouped by material in VTK and CSV
    process_data_by_material(input_data, folder_paths)


def process_data_by_material(input_data: InputData, folder_paths: FolderPaths):
    decay_times = input_data.data_absolute_activity.decay_times
    materials = input_data.data_mesh_info.data_mass.materials

    for decay_time in decay_times:
        for material in materials:
            data_mesh_activity = group_data_by_time_and_materials(
                data_absolute_activity=input_data.data_absolute_activity,
                data_mass=input_data.data_mesh_info.data_mass,
                decay_time=decay_time,
                materials=[material],
            )
            if data_mesh_activity is None:
                continue

            classify_waste(data_mesh_activity, input_data.isotope_criteria)
            grid = create_grid(input_data.data_mesh_info, data_mesh_activity)

            save_mesh_as_csv_and_vtk(
                data_mesh_activity, grid, folder_paths, decay_time, material
            )

        # All materials combination
        data_mesh_activity = group_data_by_time_and_materials(
            data_absolute_activity=input_data.data_absolute_activity,
            data_mass=input_data.data_mesh_info.data_mass,
            decay_time=decay_time,
            materials=None,
        )

        classify_waste(data_mesh_activity, input_data.isotope_criteria)
        grid = create_grid(input_data.data_mesh_info, data_mesh_activity)

        save_mesh_as_csv_and_vtk(
            data_mesh_activity, grid, folder_paths, decay_time, "all_materials"
        )


def save_mesh_as_csv_and_vtk(
    data_mesh_activity, grid, folder_paths, decay_time, material
):
    decay_time_str = format_time_seconds_to_str(decay_time)
    dataset_name = f"{decay_time_str}_{material}"

    data_mesh_activity.to_csv(folder_paths.csv_results, dataset_name)
    grid.save(f"{folder_paths.vtk_results}/{dataset_name}.vts")

    print(f"{material} for time {decay_time_str}")


def load_input_data_from_folder(folder_path: Path) -> InputData:
    data_absolute_activity = dgs_file.read_file(folder_path / "DGSdata.dat")
    data_mesh_info = mesh_info_file.read_file(folder_path / "meshinfo")
    isotope_criteria = isotope_criteria_file.read_file(
        Path(__file__).parent / "resources/criteria.json"
    )
    return InputData(data_absolute_activity, data_mesh_info, isotope_criteria)


def get_folder_paths(input_folder_path: Path) -> FolderPaths:
    data_tables_path = input_folder_path / "data_tables"
    csv_results_path = input_folder_path / "csv_files"
    vtk_results_path = input_folder_path / "vtk_files"

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


if __name__ == "__main__":
    standard_process(Path(r"D:\WORK\tryingSimple\tests\old_data\ivvs_cart"))
