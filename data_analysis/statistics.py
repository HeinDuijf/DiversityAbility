import os
import warnings

import numpy as np
import pandas as pd
import scipy.stats as stats
from joblib import Parallel, delayed
from scipy.stats import norm


def bca_ci(
    data, stat_func=np.median, n_boot=20_000, alpha=0.05, n_jobs=-1, random_state=37
):
    """Compute Bias-Corrected and Accelerated (BCa) bootstrap confidence intervals."""
    rng = np.random.default_rng(random_state)
    n = len(data)
    obs_stat = stat_func(data)

    # Bootstrap resampling
    def one_rep(_):
        sample = rng.choice(data, size=n, replace=True)
        return stat_func(sample)

    boot_stats = np.array(
        Parallel(n_jobs=n_jobs)(delayed(one_rep)(i) for i in range(n_boot))
    )

    # Bias correction
    prop = np.clip((boot_stats < obs_stat).mean(), 1e-10, 1 - 1e-10)
    z0 = norm.ppf(prop)

    # Jackknife acceleration
    jack_stats = np.array([stat_func(np.delete(data, i)) for i in range(n)])
    jack_mean = jack_stats.mean()
    num = np.sum((jack_mean - jack_stats) ** 3)
    den = 6.0 * (np.sum((jack_mean - jack_stats) ** 2) ** 1.5)
    a = num / den if den != 0 else 0.0

    # Adjusted percentiles
    z_alpha_low = norm.ppf(alpha / 2)
    z_alpha_high = norm.ppf(1 - alpha / 2)
    adj_low = norm.cdf(z0 + (z0 + z_alpha_low) / (1 - a * (z0 + z_alpha_low)))
    adj_high = norm.cdf(z0 + (z0 + z_alpha_high) / (1 - a * (z0 + z_alpha_high)))

    ci_low, ci_high = np.quantile(boot_stats, [adj_low, adj_high])
    return ci_low, ci_high


def wilcoxon_results(
    data: np.ndarray,
    data_paired: np.ndarray | None = None,
    median_hypothesis: float | None = None,
    perform_bca_ci: bool = True,
):
    """Perform Wilcoxon signed-rank test and compute effect size and BCa confidence
    intervals.

    Args:
        data: 1D array of sample data. If provided a one-sample test is performed.
        median_hypothesis: Hypothesized median value to test against. Used for one-
        sample test.
        data_paired: 1D array of paired sample data. If provided, a paired test is
        performed.
        perform_bca_ci: Boolean determining whether to perform BCa for CIs, which
        is computationally costly.

    Returns:
        A dictionary with p-value, effect size, z-statistic, confidence intervals,
        presence of ties, and ratio (proportion of differences with the dominant sign).
    """
    if median_hypothesis is not None:
        data_diff = data - median_hypothesis
    elif data_paired is not None:
        data_diff = data - data_paired
    else:
        raise ValueError("Either median_hypothesis or data_paired must be provided.")

    # Step 1: Initial Wilcoxon test to get p-value
    scipy_wilcoxon = stats.wilcoxon(
        data_diff,
        alternative="two-sided",
    )
    p_value = scipy_wilcoxon.pvalue  # type: ignore
    # statistic = wilcoxon_result.statistic

    # Step 2: Remove zeros
    data_diff = data_diff[data_diff != 0]
    n = len(data_diff)
    ties = True if len(data) != n else False

    if ties:
        warnings.warn(
            "The Wilcoxon test may not be accurate because the data contains ties."
        )

    # Step 3: Get absolute differences and ranks
    data_diff_abs = np.abs(data_diff)
    ranks = stats.rankdata(data_diff_abs)  # rank smallest to largest, average for ties

    # Step 4: Sum ranks for positive and negative differences
    sum_pos_ranks = np.sum(ranks[data_diff > 0])
    sum_neg_ranks = np.sum(ranks[data_diff < 0])

    # Step 5: Wilcoxon statistic (sum of positive ranks)
    W = min(sum_pos_ranks, sum_neg_ranks)
    # W_pos = sum_pos_ranks

    # Step 6: Expected value and variance under H0 (no ties)
    E_W = n * (n + 1) / 4
    Var_W = n * (n + 1) * (2 * n + 1) / 24

    # Step 7: Compute Z statistic ignoring the sign (no continuity correction for large
    # sample size)
    Z = abs((W - E_W) / np.sqrt(Var_W))

    # Step 8: Compute bias-corrected and accelerated (BCa) confidence intervals (CI)
    # for the median of differences
    ci_low, ci_high = np.nan, np.nan
    if perform_bca_ci:
        ci_low, ci_high = bca_ci(data_diff)

    # Step 9: Compute ratio of positive differences
    ratio_pos = data_diff[data_diff > 0].size / n
    ratio = max(ratio_pos, 1 - ratio_pos)

    return {
        "difference": np.median(data_diff),
        "p_value": p_value,
        "effect_size": Z / np.sqrt(n),
        "z-statistic": Z,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "ties": ties,
        "ratio": ratio,
    }


def produce_df_1samp(
    outcome: str = "accuracy_opinion",
    diverse_team_type: str = "diverse",
    heuristic_size: int | list[int] = 5,
    team_size: int = 9,
    reliability_range: float = 0.2,
    n_sources_list: list[int] = [13, 17],
    n_decimals: int = 3,
    p_decimals: int = 4,
    date: str = "",
    perform_bca_ci: bool = True,
) -> pd.DataFrame:
    """Produces a DataFrame summarizing one-sample Wilcoxon test results comparing
    diverse team performance against expert team performance.

    Note: Assumes simulation data files are in folder named 'data'

    Args:
        outcome: The performance metric to analyze. Defaults to "accuracy_opinion".
        diverse_team_type: The type of diverse team to analyze. Defaults to "diverse".
        heuristic_size: The heuristic size used in the simulations. Can be an integer
        or a list of integers. Defaults to 5.
        team_size: The team size. Defaults to 9.
        reliability_range: The range of the source reliability distribition. Defaults
        to 0.2.
        n_sources_list: The number of sources to consider. Defaults to [13, 17].
        n_decimals: Number of decimal places to round the difference and confidence
        intervals. Defaults to 3.
        p_decimals: Number of decimal places to round the p-value. Defaults to 4.
        date: Date string to filter simulation files. Defaults to empty string ''.
        perform_bca_ci: Whether to compute BCa confidence intervals. Defaults to True.

    Returns:
        A pandas DataFrame containing the results of the one-sample Wilcoxon tests.
        Column names are self-explanatory, except for
        'ties': Indicates whether there were tied ranks in the test
        'ratio': Represents the proportion of differences with the dominant sign.
        A ratio of 0.8 means 80% of non-zero differences had the same sign.
    """

    files = [
        file
        for file in os.listdir("data")
        if file.split("_")[0] == "simulation" and date in file.split("_")[1]
    ]
    heuristic_str: str | int = heuristic_size  # type: ignore
    if isinstance(heuristic_size, list):
        heuristic_str = str(heuristic_str)[1:-1].replace(", ", "-")  # type: ignore

    results = []
    for file in files:
        df = pd.read_csv(f"data/{file}")
        if (
            heuristic_str in df.heuristic_size.values
            and team_size in df.team_size.values
            and reliability_range in df.reliability_range.values
        ):
            if diverse_team_type in df.team_type.values:
                n_sources = df.at[0, "n_sources"]
                if n_sources not in n_sources_list:
                    continue
                rel_mean = df.at[0, "reliability_mean"]
                df_diverse = df[df["team_type"] == diverse_team_type]
                # df_diverse = df_dummy.copy()
                diverse_accuracy = df_diverse[outcome].median()
                expert_accuracy = df[df["team_type"] == "expert"][outcome].median()

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

                if outcome == "accuracy_evidence":
                    difference = diverse_accuracy - expert_accuracy
                    pvalue = np.nan
                    effect_size = np.nan
                    ci_low = np.nan
                    ci_high = np.nan
                    ties = False
                    ratio = np.nan

                else:
                    statistic_results = wilcoxon_results(
                        np.array(df_diverse[outcome]),
                        median_hypothesis=expert_accuracy,
                        perform_bca_ci=perform_bca_ci,
                    )
                    difference = statistic_results["difference"]
                    pvalue = statistic_results["p_value"]
                    effect_size = statistic_results["effect_size"]
                    ci_low = statistic_results["ci_low"]
                    ci_high = statistic_results["ci_high"]
                    ties = statistic_results["ties"]
                    ratio = statistic_results["ratio"]

                results.append(
                    [
                        n_sources,
                        rel_mean,
                        round(difference, n_decimals),
                        round(error_reduction, 1),
                        round(pvalue, p_decimals),
                        round(effect_size, 3),
                        ci_low,
                        ci_high,
                        ties,
                        ratio,
                    ]
                )

    columns = [
        "n_sources",
        "rel_mean",
        "difference",
        "error_reduction",
        "p_value",
        "effect_size",
        "ci_low",
        "ci_high",
        "ties",
        "ratio",
    ]
    return pd.DataFrame(results, columns=columns)


def produce_df_paired(
    x: str = "accuracy_evidence",
    y: str = "accuracy_bounded",
    diverse_team_type: str = "diverse",
    heuristic_size: int | list[int] = 5,
    team_size: int = 9,
    reliability_range: float = 0.2,
    n_sources_list: list[int] = [13, 17],
    n_decimals: int = 3,
    p_decimals: int = 4,
    date: str = "",
    perform_bca_ci: bool = True,
):
    """Produces a DataFrame summarizing paired Wilcoxon test results comparing
    diverse team performance for mechanisms x and y.

    Note: Assumes simulation data files are in folder named 'data'.

    Args:
        x: The first deliberative mechanism. Defaults to 'accuracy_evidence'.
        y: The second deliberative mechanism. Defaults to 'accuracy_bounded'.
        diverse_team_type: The type of diverse team to analyze. Defaults to "diverse".
        heuristic_size: The heuristic size used in the simulations. Can be an integer
        or a list of integers. Defaults to 5.
        team_size: The team size. Defaults to 9.
        reliability_range: The range of the source reliability distribition. Defaults
        to 0.2.
        n_sources_list: The number of sources to consider. Defaults to [13, 17].
        n_decimals: Number of decimal places to round the difference and confidence
        intervals. Defaults to 3.
        p_decimals: Number of decimal places to round the p-value. Defaults to 4.
        date: Date string to filter simulation files. Defaults to empty string ''.
        perform_bca_ci: Whether to compute BCa confidence intervals. Defaults to True.

    Returns:
        A pandas DataFrame containing the results of the one-sample Wilcoxon tests.
        Column names are self-explanatory, except for
        'ties': Indicates whether there were tied ranks in the test
        'ratio': Represents the proportion of differences with the dominant sign.
        A ratio of 0.8 means 80% of non-zero differences had the same sign.
    """
    files = [
        file
        for file in os.listdir("data")
        if file.split("_")[0] == "simulation" and date in file.split("_")[1]
    ]
    heuristic_str: str | int = heuristic_size  # type: ignore
    if isinstance(heuristic_size, list):
        heuristic_str = str(heuristic_str)[1:-1].replace(", ", "-")  # type: ignore

    results = []
    for file in files:
        df = pd.read_csv(f"data/{file}")
        if (
            heuristic_str in df.heuristic_size.values
            and team_size in df.team_size.values
            and reliability_range in df.reliability_range.values
        ):
            if diverse_team_type in df.team_type.values:
                n_sources = df.at[0, "n_sources"]
                if n_sources not in n_sources_list:
                    continue
                rel_mean = df.at[0, "reliability_mean"]
                df_diverse = df[df["team_type"] == diverse_team_type]
                data_x = np.array(df_diverse[x])
                data_y = np.array(df_diverse[y])
                statistics_result = wilcoxon_results(
                    data_x, data_paired=data_y, perform_bca_ci=perform_bca_ci
                )
                results.append(
                    [
                        n_sources,
                        rel_mean,
                        round(statistics_result["difference"], n_decimals),
                        round(statistics_result["p_value"], p_decimals),
                        statistics_result["effect_size"],
                        round(statistics_result["ci_low"], n_decimals),
                        round(statistics_result["ci_high"], n_decimals),
                        statistics_result["ties"],
                        statistics_result["ratio"],
                    ]
                )
    columns = [
        "n_sources",
        "rel_mean",
        "difference",
        "p_value",
        "effect_size",
        "ci_low",
        "ci_high",
        "ties",
        "ratio",
    ]
    return pd.DataFrame(results, columns=columns)

    # date = "202412"
    # files = [
    #     file
    #     for file in os.listdir("data")
    #     if file[:10] == "simulation" and date in file and "README" not in file
    # ]
    # results = []
    # for file in files:
    #     df = pd.read_csv(f"data/{file}")
    #     n_sources = df.at[0, "n_sources"]
    #     rel_mean = df.at[0, "reliability_mean"]
    #     df = df[df["team_type"] == "diverse"]
    #     data_x = np.array(df[x])
    #     data_y = np.array(df[y])
    #     statistics_result = wilcoxon_results(data_x, data_paired=data_y)

    #     results.append(
    #         [
    #             n_sources,
    #             rel_mean,
    #             round(statistics_result["difference"], n_decimals),
    #             statistics_result["p_value"],
    #             statistics_result["effect_size"],
    #             round(statistics_result["ci_low"], n_decimals),
    #             round(statistics_result["ci_high"], n_decimals),
    #             statistics_result["ties"],
    #             statistics_result["ratio"],
    #         ]
    #     )
    # columns = [
    #     "n_sources",
    #     "rel_mean",
    #     "difference",
    #     "p_value",
    #     "effect_size",
    #     "ci_low",
    #     "ci_high",
    #     "ties",
    #     "ratio",
    # ]
    # return pd.DataFrame(results, columns=columns)
