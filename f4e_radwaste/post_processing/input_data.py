from dataclasses import dataclass
from typing import Optional, List

import pandas as pd

from f4e_radwaste.constants import (
    KEY_ABSOLUTE_ACTIVITY,
    KEY_VOXEL,
    KEY_ISOTOPE,
    KEY_MASS_GRAMS,
)
from f4e_radwaste.data_formats.data_absolute_activity import DataAbsoluteActivity
from f4e_radwaste.data_formats.data_isotope_criteria import DataIsotopeCriteria
from f4e_radwaste.data_formats.data_mass import DataMass
from f4e_radwaste.data_formats.data_mesh_activity import DataMeshActivity
from f4e_radwaste.data_formats.data_mesh_info import DataMeshInfo
from f4e_radwaste.helpers import format_time_seconds_to_str
from f4e_radwaste.post_processing.calculate_dose_rates import DoseCalculator
from f4e_radwaste.post_processing.classify_waste import classify_waste
from f4e_radwaste.post_processing.component_output import ComponentOutput
from f4e_radwaste.post_processing.components_info import ComponentsInfo
from f4e_radwaste.post_processing.folder_paths import FolderPaths
from f4e_radwaste.post_processing.mesh_ouput import MeshOutput


@dataclass
class InputData:
    data_absolute_activity: DataAbsoluteActivity
    data_mesh_info: DataMeshInfo
    isotope_criteria: DataIsotopeCriteria

    def save_data_tables(self, folder_paths: FolderPaths):
        self.data_absolute_activity.save_dataframe_to_hdf5(folder_paths.data_tables)
        self.data_mesh_info.save(folder_paths.data_tables)

    def try_get_mesh_output_by_time_and_materials(
        self, decay_time: float, materials: Optional[List[int]] = None
    ) -> Optional[MeshOutput]:
        try:
            return self.get_mesh_output_by_time_and_materials(decay_time, materials)
        except ValueError:
            return None

    def get_mesh_output_by_time_and_materials(
        self, decay_time, materials
    ) -> MeshOutput:
        data_mesh_activity = self.get_mesh_activity_by_time_and_materials(
            decay_time=decay_time,
            materials=materials,
        )

        data_mesh_activity = classify_waste(data_mesh_activity, self.isotope_criteria)

        return MeshOutput(
            name=create_name_by_time_and_materials(decay_time, materials),
            data_mesh_info=self.data_mesh_info,
            data_mesh_activity=data_mesh_activity,
        )

    def get_mesh_activity_by_time_and_materials(
        self, decay_time: float, materials: Optional[List[int]] = None
    ) -> DataMeshActivity:
        data_mass = self.data_mesh_info.data_mass
        selected_cells, voxel_masses = data_mass.get_cells_and_masses_from_selection(
            materials
        )

        # Get the activity only at the cells and decay time of interest
        filtered_activity = self.data_absolute_activity.get_filtered_dataframe(
            decay_times=[decay_time],
            cells=selected_cells,
        )[KEY_ABSOLUTE_ACTIVITY]

        if filtered_activity.empty:
            raise ValueError

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

    def get_collapsed_activity(
        self, decay_time: float, materials: List[int], voxels: List[int]
    ) -> DataMeshActivity:
        data_mass = self.data_mesh_info.data_mass
        selected_cells, voxel_masses = data_mass.get_cells_and_masses_from_selection(
            materials, voxels
        )

        # Get the activity only at the cells, voxels and decay time of interest
        filtered_activity = self.data_absolute_activity.get_filtered_dataframe(
            decay_times=[decay_time],
            cells=selected_cells,
            voxels=voxels,
        )

        combined_activity = filtered_activity.groupby([KEY_ISOTOPE]).sum()

        # Calculate the specific activity in Bq/g
        package_mass = voxel_masses.sum()
        voxel_specific_activity = combined_activity.div(package_mass, fill_value=0.0)

        voxel_activity_dataframe = voxel_specific_activity.T

        voxel_activity_dataframe.columns.name = None
        voxel_activity_dataframe.index = [0]
        voxel_activity_dataframe.index.name = KEY_VOXEL

        # Add the mass information to the dataframe
        voxel_activity_dataframe.insert(0, KEY_MASS_GRAMS, package_mass)

        return DataMeshActivity(voxel_activity_dataframe)

    def get_component_output_by_time_and_ids(
        self,
        decay_time: float,
        components_info: ComponentsInfo,
        dose_calculator: DoseCalculator,
    ) -> ComponentOutput:
        comp_mesh_activity = self.get_component_mesh_activity_by_time_and_ids(
            decay_time=decay_time, components_info=components_info
        )

        comp_mesh_activity = classify_waste(comp_mesh_activity, self.isotope_criteria)

        comp_mesh_activity = dose_calculator.calculate_doses(
            comp_activity=comp_mesh_activity,
            cdr_factor_columns=components_info.cdr_factors,
        )

        return ComponentOutput(
            name=f"{format_time_seconds_to_str(decay_time)}_by_component",
            data_mesh_activity=comp_mesh_activity,
        )

    def get_component_mesh_activity_by_time_and_ids(
        self, decay_time: float, components_info: ComponentsInfo
    ) -> DataMeshActivity:
        component_series: List[pd.Series] = []
        for component_name, cell_ids in components_info.get_components():
            filtered_activity = self.data_absolute_activity.get_filtered_dataframe(
                decay_times=[decay_time],
                cells=cell_ids,
            )[KEY_ABSOLUTE_ACTIVITY]

            # A component may contain several voxels and cells, sum the absolute
            # activity of those
            combined_activity = filtered_activity.groupby([KEY_ISOTOPE]).sum()

            # Calculate the specific activity in Bq/g
            mass_of_component = self.data_mesh_info.data_mass.get_mass_from_cells(
                cell_ids
            )
            voxel_specific_activity = combined_activity.div(
                mass_of_component, fill_value=0.0
            )

            voxel_specific_activity.name = component_name
            voxel_specific_activity[KEY_MASS_GRAMS] = mass_of_component
            component_series.append(voxel_specific_activity)

        # Prepare the dataframe for DataMeshActivity
        activities = pd.concat(component_series, axis=1)
        activities = activities.transpose()
        activities.fillna(0.0, inplace=True)
        activities.index.name = KEY_VOXEL
        activities.columns.name = None

        return DataMeshActivity(activities)

    def apply_filter_include_cells(self, cells_to_include: List[int]):
        # Filter DataAbsoluteActivity
        filtered_absolute_activity_df = (
            self.data_absolute_activity.get_filtered_dataframe(
                cells=cells_to_include,
            )
        )
        self.data_absolute_activity = DataAbsoluteActivity(
            filtered_absolute_activity_df
        )

        # Filter DataMeshInfo
        filtered_data_mass_df = self.data_mesh_info.data_mass.get_filtered_dataframe(
            cells=cells_to_include
        )
        self.data_mesh_info.data_mass = DataMass(filtered_data_mass_df)


def create_name_by_time_and_materials(
    decay_time: float, materials: Optional[List[int]] = None
) -> str:
    time_str = format_time_seconds_to_str(decay_time)
    if materials is None:
        materials = "all_materials"
    return f"Time {time_str} with materials {materials}"
