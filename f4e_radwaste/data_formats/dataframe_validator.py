from abc import ABC, abstractmethod

import pandas as pd


class DataFrameValidator(ABC):
    EXPECTED_INDEX_NAMES = []
    EXPECTED_COLUMNS = []

    def __init__(self, dataframe):
        self._dataframe = dataframe
        self._validate_dataframe_format()

    def _validate_dataframe_format(self):
        indices_identical = self._dataframe.index.names == self.EXPECTED_INDEX_NAMES
        expected_columns_are_present = all(
            expected_column in self._dataframe.columns.tolist()
            for expected_column in self.EXPECTED_COLUMNS
        )

        if not indices_identical or not expected_columns_are_present:
            raise ValueError(
                "The format of the dataframe is not correct. "
                "It has to be a MultiIndex DataFrame with index:"
                f" {self.EXPECTED_INDEX_NAMES} and columns: {self.EXPECTED_COLUMNS}"
            )

    @abstractmethod
    def get_filtered_dataframe(self, **kwargs) -> pd.DataFrame:
        mask = pd.Series(True, index=self._dataframe.index)

        for key, filter_values in kwargs.items():
            if filter_values is not None:
                mask &= self._dataframe.index.get_level_values(key).isin(filter_values)

        return self._dataframe.loc[mask]
