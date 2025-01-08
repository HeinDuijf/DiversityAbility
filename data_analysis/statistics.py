import os

import numpy as np
import pandas as pd
import scipy.stats as stats


def produce_df(team_type="expert", outcome: str = "accuracy", n_decimals=1):
    date = "202412"
    files = [
        file
        for file in os.listdir("data")
        if file[:10] == "simulation" and date in file and "README" not in file
    ]
    results = []
    for file in files:
        df = pd.read_csv(f"data/{file}")
        n_sources = df.at[0, "n_sources"]
        rel_mean = df.at[0, "reliability_mean"]
        if team_type == "expert":
            result = df.at[0, outcome]
            result = result * 100
            std = 0
        elif team_type == "diverse":
            df_div = df[df["team_type"] == "diverse"]
            df_test = df_div.copy()
            result = df_test[outcome].mean()
            result = result * 100
            std = df_test[outcome].std()
            std = std * 100

        results.append(
            [
                n_sources,
                rel_mean,
                round(result, n_decimals),
                round(std, n_decimals),
            ]
        )
    columns = ["n_sources", "rel_mean", outcome, "std"]
    return pd.DataFrame(results, columns=columns)


def produce_df_1samp(outcome: str = "accuracy", n_decimals=3):
    date = "202412"
    files = [
        file
        for file in os.listdir("data")
        if file[:10] == "simulation" and date in file and "README" not in file
    ]
    results = []
    for file in files:
        df = pd.read_csv(f"data/{file}")
        n_sources = df.at[0, "n_sources"]
        rel_mean = df.at[0, "reliability_mean"]
        df_div = df[df["team_type"] == "diverse"]
        df_test = df_div.copy()
        diverse_accuracy = df_test[outcome].mean()
        expert_accuracy = df.at[0, outcome]

        diverse_error = 1 - diverse_accuracy
        expert_error = 1 - expert_accuracy

        if expert_error > diverse_error:
            error_reduction = 100 * (expert_error - diverse_error) / diverse_error
            # error_reduction = - (expert_error / diverse_error)
        elif diverse_error > expert_error:
            error_reduction = -100 * (diverse_error - expert_error) / expert_error
            # error_reduction = diverse_error / expert_error
        else:
            error_reduction = 0

        if outcome == "pool_accuracy":
            statistic = np.nan
            pvalue = 0
            diverse_std = np.nan
        else:
            diverse_std = df_test[outcome].std()
            result = stats.wilcoxon(df_test[outcome] - expert_accuracy)
            pvalue = result.pvalue
            statistic = result.statistic

        results.append(
            [
                n_sources,
                rel_mean,
                round(pvalue, 4),
                statistic,
                round(diverse_accuracy - expert_accuracy, n_decimals),
                round(error_reduction),
                diverse_std,
            ]
        )
    columns = [
        "n_sources",
        "rel_mean",
        "p_value",
        "statistic",
        "difference",
        "error_reduction",
        "std",
    ]
    return pd.DataFrame(results, columns=columns)


def perform_paired(
    file, team_type="diverse", x="pool_accuracy", y="bounded_pool_accuracy"
):
    if file[-4:] != ".csv":
        file = f"{file}.csv"
    df = pd.read_csv(f"data/{file}")
    df = df[df["team_type"] == team_type]
    # df_div = df[df["team_type"] == "diverse"]
    df_test = df.copy()
    result = stats.wilcoxon(df_test[x], df_test[y])
    pvalue = result.pvalue
    n_instances = df_test.index.size
    statistic = result.statistic / (n_instances**2)
    x_mean = df_test[x].mean()
    y_mean = df_test[y].mean()
    result_dict = {
        "p_value": pvalue,
        "statistic": statistic,
        "difference": x_mean - y_mean,
    }
    return result_dict


def produce_df_paired(
    x: str = "pool_accuracy", y="bounded_pool_accuracy", n_decimals: int = 3
):
    date = "202412"
    files = [
        file
        for file in os.listdir("data")
        if file[:10] == "simulation" and date in file and "README" not in file
    ]
    results = []
    for file in files:
        df = pd.read_csv(f"data/{file}")
        n_sources = df.at[0, "n_sources"]
        rel_mean = df.at[0, "reliability_mean"]
        result = perform_paired(file, "diverse", x, y)
        results.append(
            [
                n_sources,
                rel_mean,
                round(result["p_value"], 4),
                round(result["statistic"]),
                round(result["difference"], n_decimals),
            ]
        )
    columns = ["n_sources", "rel_mean", "p_value", "statistic", "difference"]
    return pd.DataFrame(results, columns=columns)
