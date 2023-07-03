from typing import List, Optional

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
