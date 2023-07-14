import pandas as pd


def read_dose_1_m_factors(file_path) -> pd.Series:
    df_dose_1_m_factors = pd.read_csv(
        file_path,
        skiprows=3,
        index_col=0,
        usecols=[0, 1],
        header=None,
    )
    df_dose_1_m_factors.index.name = None
    return df_dose_1_m_factors[1]


def read_contact_dose_rate_factors(file_path) -> pd.DataFrame:
    df_cdr_factors = pd.read_csv(
        file_path,
        skiprows=2,
        index_col=0,
    )
    df_cdr_factors = df_cdr_factors.drop(columns=df_cdr_factors.columns[0], axis=1)
    return df_cdr_factors
