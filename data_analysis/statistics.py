import os

import numpy as np
import pandas as pd
import scipy.stats as stats


def produce_df(
    outcome: str = "accuracy",
    team_type: str = "expert",
    heuristic_size: int = 5,
    n_decimals: int = 1,
    date: str = "",
):
    files = [
        file
        for file in os.listdir("data")
        if file[:10] == "simulation" and date in file and "README" not in file
    ]
    results = []
    for file in files:
        df = pd.read_csv(f"data/{file}")
        if team_type in df.team_type.values:
            if heuristic_size in df.heuristic_size.values:
                n_sources = df.at[0, "n_sources"]
                rel_mean = df.at[0, "reliability_mean"]
                df_team_type = df[df["team_type"] == team_type]
                result = df_team_type[outcome].mean()
                result = result * 100
                std = df_team_type[outcome].std()
                std = std * 100
                if team_type == "expert":
                    std = 0

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


def produce_df_1samp(
    outcome: str = "accuracy",
    diverse_team_type: str = "diverse",
    heuristic_size: int = 5,
    n_decimals: int = 3,
    p_decimals: int = 4,
    date: str = "",
):
    files = [
        file
        for file in os.listdir("data")
        if file[:10] == "simulation" and date in file and "README" not in file
    ]
    if not isinstance(heuristic_size, int):
        heuristic_size = str(heuristic_size)[1:-1].replace(", ", "-")

    results = []
    for file in files:
        df = pd.read_csv(f"data/{file}")
        if heuristic_size in df.heuristic_size.values:
            if diverse_team_type in df.team_type.values:
                n_sources = df.at[0, "n_sources"]
                rel_mean = df.at[0, "reliability_mean"]
                df_diverse = df[df["team_type"] == diverse_team_type]
                # df_diverse = df_dummy.copy()
                diverse_accuracy = df_diverse[outcome].mean()
                expert_accuracy = df[df["team_type"] == "expert"][outcome].mean()

                diverse_error = 1 - diverse_accuracy
                expert_error = 1 - expert_accuracy

                if diverse_accuracy > expert_accuracy:
                    error_reduction = (
                        100 * (expert_error - diverse_error) / diverse_error
                    )
                    # error_reduction = - (expert_error / diverse_error)
                elif expert_accuracy > diverse_accuracy:
                    error_reduction = (
                        -100 * (diverse_error - expert_error) / expert_error
                    )
                    # error_reduction = diverse_error / expert_error
                else:
                    error_reduction = 0

                if outcome == "pool_accuracy":
                    statistic = np.nan
                    pvalue = 0
                    diverse_std = np.nan
                else:
                    diverse_std = df_diverse[outcome].std()
                    result = stats.wilcoxon(df_diverse[outcome] - expert_accuracy)
                    pvalue = result.pvalue
                    statistic = result.statistic

                results.append(
                    [
                        n_sources,
                        rel_mean,
                        round(pvalue, p_decimals),
                        statistic,
                        round(diverse_accuracy - expert_accuracy, n_decimals),
                        round(error_reduction, 1),
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
