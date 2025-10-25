import os

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
        data: 1D array of sample data.
        median_hypothesis: Hypothesized median value to test against. Used for one-
        sample test.
        data_paired: 1D array of paired sample data. If provided, a paired test is
        performed.
        perform_bca_ci: Boolean determining whether to perform BCa for CIs, which
        is computationally costly.
    Returns:
        A dictionary with p-value, effect size, z-statistic, confidence intervals,
        presence of ties, and ratio of differences.
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
    p_value = scipy_wilcoxon.pvalue
    # statistic = wilcoxon_result.statistic

    # Step 2: Remove zeros
    data_diff = data_diff[data_diff != 0]
    n = len(data_diff)
    ties = True if len(data) != n else False

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

    # Step 9:
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
    heuristic_size: int | list[int] = 5,
    n_decimals: int = 3,
    p_decimals: int = 4,
    date: str = "",
    perform_bca_ci: bool = True,
) -> pd.DataFrame:
    files = [
        file
        for file in os.listdir("data")
        if file[:10] == "simulation" and date in file and "README" not in file
    ]
    if isinstance(heuristic_size, list):
        heuristic_size = str(heuristic_size)[1:-1].replace(", ", "-")  # type: ignore

    results = []
    for file in files:
        df = pd.read_csv(f"data/{file}")
        if heuristic_size in df.heuristic_size.values:
            if diverse_team_type in df.team_type.values:
                n_sources = df.at[0, "n_sources"]
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

                if outcome == "pool_accuracy":
                    difference = diverse_accuracy - expert_accuracy
                    pvalue = 0
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
        df = df[df["team_type"] == "diverse"]
        data_x = np.array(df[x])
        data_y = np.array(df[y])
        statistics_result = wilcoxon_results(data_x, data_paired=data_y)
        # statistics_result = perform_paired(file, "diverse", x, y)
        results.append(
            [
                n_sources,
                rel_mean,
                round(statistics_result["difference"], n_decimals),
                statistics_result["p_value"],
                statistics_result["effect_size"],
                round(statistics_result["ci_low"], n_decimals),
                round(statistics_result["ci_high"], n_decimals),
                statistics_result["ties"],
                # ratio = statistic_results["ratio"]
                # round(statistics_result["difference"], n_decimals),
                # round(statistics_result["p_value"], 4),
                # round(statistics_result["statistic"]),
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
    ]
    return pd.DataFrame(results, columns=columns)
