from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import pandas as pd

from f4e_radwaste.constants import (
    KEY_ABSOLUTE_ACTIVITY,
    KEY_ISOTOPE,
    KEY_VOXEL,
    KEY_MASS_GRAMS,
    TYPE_TFA,
    TYPE_A,
    TYPE_B,
    KEY_IRAS,
    KEY_LMA,
    KEY_RELEVANT_SPECIFIC_ACTIVITY,
    KEY_TOTAL_SPECIFIC_ACTIVITY,
    KEY_RADWASTE_CLASS,
)
from f4e_radwaste.data_formats.data_absolute_activity import DataAbsoluteActivity
from f4e_radwaste.data_formats.data_isotope_criteria import DataIsotopeCriteria
from f4e_radwaste.data_formats.data_mass import DataMass
from f4e_radwaste.data_formats.data_mesh_activity import DataMeshActivity
from f4e_radwaste.data_formats.data_mesh_info import DataMeshInfo
from f4e_radwaste.helpers import format_time_seconds_to_str
from f4e_radwaste.meshgrids import create_grid


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


def process_input_data_by_material(input_data: InputData, folder_paths: FolderPaths):
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


def apply_filter_include_cells(input_data: InputData, cells_to_include: List[int]):
    # Filter DataAbsoluteActivity
    filtered_absolute_activity_df = (
        input_data.data_absolute_activity.get_filtered_dataframe(
            cells=cells_to_include,
        )
    )
    input_data.data_absolute_activity = DataAbsoluteActivity(
        filtered_absolute_activity_df
    )

    # Filter DataMeshInfo
    filtered_data_mass_df = input_data.data_mesh_info.data_mass.get_filtered_dataframe(
        cells=cells_to_include
    )
    input_data.data_mesh_info.data_mass = DataMass(filtered_data_mass_df)


def group_data_by_time_and_materials(
    data_absolute_activity: DataAbsoluteActivity,
    data_mass: DataMass,
    decay_time: float,
    materials: Optional[List[int]] = None,
) -> Optional[DataMeshActivity]:
    selected_cells, voxel_masses = data_mass.get_cells_and_masses_from_materials(
        materials
    )

    # Get the activity only at the cells and decay time of interest
    filtered_activity = data_absolute_activity.get_filtered_dataframe(
        decay_times=[decay_time],
        cells=selected_cells,
    )[KEY_ABSOLUTE_ACTIVITY]

    if filtered_activity.empty:
        return None

    # Multiple cells with the same combination of voxel and isotope may exist,
    #  sum the absolute activity of those
    combined_activity = filtered_activity.groupby([KEY_VOXEL, KEY_ISOTOPE]).sum()

    # Calculate the specific activity in Bq/g
    voxel_specific_activity = combined_activity.div(voxel_masses, fill_value=0.0)

    # Format the dataframe as DataMeshActivity
    voxel_activity_dataframe = voxel_specific_activity.unstack(fill_value=0.0)
    voxel_activity_dataframe.columns.name = None

    # Add the mass information to the dataframe
    voxel_activity_dataframe.insert(0, KEY_MASS_GRAMS, voxel_masses)

    return DataMeshActivity(voxel_activity_dataframe)


def save_mesh_as_csv_and_vtk(
    data_mesh_activity, grid, folder_paths, decay_time, material
):
    decay_time_str = format_time_seconds_to_str(decay_time)
    dataset_name = f"{decay_time_str}_{material}"

    data_mesh_activity.to_csv(folder_paths.csv_results, dataset_name)
    grid.save(f"{folder_paths.vtk_results}/{dataset_name}.vts")

    print(f"{material} for time {decay_time_str}")


def classify_waste(
    data_mesh_activity: DataMeshActivity, isotope_criteria: DataIsotopeCriteria
):
    # Get the activity of all isotopes
    all_isotopes_activity = data_mesh_activity.get_filtered_dataframe(
        isotopes=isotope_criteria.all_isotopes_names
    )

    # Calculate radwaste relevant parameters
    iras = (all_isotopes_activity / (10**isotope_criteria.tfa_class)).sum(axis=1)
    lma_exceeded = all_isotopes_activity.ge(isotope_criteria.lma).sum(axis=1)
    total_specific_activity = all_isotopes_activity.sum(axis=1)

    # Calculate radwaste class
    mask_iras_exceeded = iras >= 1
    mask_lma_exceeded = lma_exceeded >= 1
    radwaste_class = pd.Series(data=TYPE_TFA, index=iras.index)
    radwaste_class[mask_iras_exceeded] = TYPE_A
    radwaste_class[mask_iras_exceeded * mask_lma_exceeded] = TYPE_B

    # Get the activity of relevant isotopes (have a TFA class)
    relevant_isotopes_activity = data_mesh_activity.get_filtered_dataframe(
        isotopes=isotope_criteria.relevant_isotopes_names
    )
    total_relevant_activity = relevant_isotopes_activity.sum(axis=1)

    # Assign names to the new series and merge them into a new dataframe
    data_mesh_activity.add_columns(
        {
            KEY_RADWASTE_CLASS: radwaste_class,
            KEY_IRAS: iras,
            KEY_LMA: lma_exceeded,
            KEY_TOTAL_SPECIFIC_ACTIVITY: total_specific_activity,
            KEY_RELEVANT_SPECIFIC_ACTIVITY: total_relevant_activity,
        }
    )
