import pandas as pd

from f4e_radwaste.constants import (
    TYPE_TFA,
    TYPE_A,
    TYPE_B,
    KEY_RADWASTE_CLASS,
    KEY_IRAS,
    KEY_LMA,
    KEY_TOTAL_SPECIFIC_ACTIVITY,
    KEY_RELEVANT_SPECIFIC_ACTIVITY,
)
from f4e_radwaste.data_formats.data_isotope_criteria import DataIsotopeCriteria
from f4e_radwaste.data_formats.data_mesh_activity import DataMeshActivity


def classify_waste(
    data_mesh_activity: DataMeshActivity, isotope_criteria: DataIsotopeCriteria
) -> DataMeshActivity:
    # Get the activity of all isotopes
    all_isotopes_activity = data_mesh_activity.get_filtered_dataframe(
        columns=isotope_criteria.all_isotopes_names
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
        columns=isotope_criteria.relevant_isotopes_names
    )
    total_relevant_activity = relevant_isotopes_activity.sum(axis=1)

    # Assign names to the new series and merge them into a new dataframe
    classified_dataframe = data_mesh_activity.get_dataframe_with_added_columns(
        {
            KEY_RADWASTE_CLASS: radwaste_class,
            KEY_IRAS: iras,
            KEY_LMA: lma_exceeded,
            KEY_TOTAL_SPECIFIC_ACTIVITY: total_specific_activity,
            KEY_RELEVANT_SPECIFIC_ACTIVITY: total_relevant_activity,
        }
    )

    return DataMeshActivity(classified_dataframe)
