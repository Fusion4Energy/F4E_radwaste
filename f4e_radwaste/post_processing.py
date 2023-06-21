from typing import List, Optional

from f4e_radwaste.constants import (
    KEY_ABSOLUTE_ACTIVITY,
    KEY_ISOTOPE,
    KEY_VOXEL,
    KEY_MASS_GRAMS,
)
from f4e_radwaste.data_formats.data_absolute_activity import DataAbsoluteActivity
from f4e_radwaste.data_formats.data_isotope_criteria import DataIsotopeCriteria
from f4e_radwaste.data_formats.data_mass import DataMass
from f4e_radwaste.data_formats.data_mesh_activity import DataMeshActivity


def group_data_by_time_and_materials(
    data_absolute_activity: DataAbsoluteActivity,
    data_mass: DataMass,
    decay_time: float,
    materials: Optional[List[int]],
) -> Optional[DataMeshActivity]:
    # Get the activity only at the cells and decay time of interest
    selected_cells = data_mass.get_cells_from_materials(materials=materials)
    filtered_activity = data_absolute_activity.get_filtered_dataframe(
        decay_times=[decay_time],
        cells=selected_cells,
    )[KEY_ABSOLUTE_ACTIVITY]

    if filtered_activity.empty:
        return None

    # Multiple cells with the same combination of voxel and isotope may exist,
    # sum the absolute activity of those
    combined_activity = filtered_activity.groupby([KEY_VOXEL, KEY_ISOTOPE]).sum()

    # Calculate the specific activity in Bq/g
    voxel_masses = (
        data_mass.get_filtered_dataframe(materials=materials)[KEY_MASS_GRAMS]
        .groupby(KEY_VOXEL)
        .sum()
    )
    voxel_specific_activity = combined_activity.div(voxel_masses, fill_value=0.0)

    # Format the dataframe as DataMeshActivity
    voxel_activity_dataframe = voxel_specific_activity.unstack(fill_value=0.0)
    voxel_activity_dataframe.columns.name = None

    # Add the mass information to the dataframe
    voxel_activity_dataframe.insert(0, KEY_MASS_GRAMS, voxel_masses)

    return DataMeshActivity(voxel_activity_dataframe)


def classify_waste(
    mesh_activity: DataMeshActivity, isotope_criteria: DataIsotopeCriteria
):
    pass
