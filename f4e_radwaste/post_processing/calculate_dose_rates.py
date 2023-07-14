import pandas as pd

from f4e_radwaste.constants import KEY_DOSE_1_METER
from f4e_radwaste.data_formats.data_mesh_activity import DataMeshActivity


def calculate_dose_at_1_meter(
    data_mesh_activity: DataMeshActivity, dose_1_m_factors: pd.Series
) -> DataMeshActivity:
    activity_df = data_mesh_activity.get_filtered_dataframe()
    dose_1m_column = (activity_df * dose_1_m_factors).sum(axis=1)

    updated_df = data_mesh_activity.get_dataframe_with_added_columns(
        {KEY_DOSE_1_METER: dose_1m_column}
    )
    # TODO: confirm that we don't need to multiply by the mass
    return DataMeshActivity(updated_df)


def calculate_contact_dose_rate(
    data_mesh_activity: DataMeshActivity, cdr_factors: pd.DataFrame
) -> DataMeshActivity:
    pass
