import itertools

import pandas as pd
from Archive.stats_scripts.table_absolute_change import table_absolute_change
from Archive.stats_scripts.table_std_coefficients import table_std_coefficients
from Archive.stats_scripts.table_variance import table_variance
from Archive.stats_scripts.table_variance_multiple_datasets import (
    table_variance_multiple_datasets,
)


def compare_dataframes(
    dataframe_correct: pd.DataFrame, dataframe_test: pd.DataFrame, error: float = 0.1
):
    assert list(dataframe_correct.index) == list(dataframe_test.index)
    assert list(dataframe_correct.columns) == list(dataframe_test.columns)

    locations = list(
        itertools.product(dataframe_correct.index, dataframe_correct.columns)
    )
    for location in locations:
        value_df1 = dataframe_correct.at[location]
        value_df2 = dataframe_test.at[location]
        assert value_df2 > (value_df1 - error * abs(value_df1))
        assert value_df2 < (value_df1 + error * abs(value_df1))


def test_table_variance():
    df_test = table_variance(data_file="../../tests/data/clean.csv")
    df_correct = pd.read_csv("../../tests/data/table_variance.csv", index_col=0)
    compare_dataframes(df_correct, df_test, error=0.1)


def test_table_variance_multiple_datasets():
    df_test = table_variance_multiple_datasets(data_file="../../tests/data/clean.csv")
    df_correct = pd.read_csv(
        "../../tests/data/table_variance_multiple.csv", index_col=0
    )
    compare_dataframes(df_correct, df_test, error=0.1)


def test_table_std_coefficients():
    df_test = table_std_coefficients(data_file="../../tests/data/clean.csv")
    df_correct = pd.read_csv("../../tests/data/table_std_coeff.csv", index_col=0)
    compare_dataframes(df_correct, df_test, error=0.1)


def test_table_absolute_change():
    df_test = table_absolute_change(data_file="../../tests/data/clean.csv")
    df_correct = pd.read_csv("../../tests/data/table_abs_change.csv", index_col=0)
    compare_dataframes(df_correct, df_test, error=0.1)
