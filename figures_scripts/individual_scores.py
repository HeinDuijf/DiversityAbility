import os
from math import comb

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from models.generate_teams import generate_expert_team
from models.sources import Sources


def boxplot_individual_scores(date="202412"):
    files = [
        file
        for file in os.listdir("data")
        if file[:10] == "simulation" and date in file and "README" not in file
    ]
    scores_df_13 = pd.DataFrame()
    for file in files:
        df = pd.read_csv(f"data/{file}")
        rel_mean = df.at[0, "reliability_mean"]
        n_sources = df.at[0, "n_sources"]
        if n_sources != 13:
            break
        heuristic_size = df.at[0, "heuristic_size"]
        reliability_distribution = ("equi", (rel_mean - 0.1, rel_mean + 0.1))
        sources = Sources(n_sources, reliability_distribution)
        n_possible_heuristics = comb(n_sources, heuristic_size)
        team = generate_expert_team(sources, heuristic_size, n_possible_heuristics)
        data = np.array([agent.score for agent in team.members])
        data_df = pd.DataFrame(data, columns=[rel_mean])
        scores_df_13 = pd.concat([scores_df_13, data_df], axis=1)

    sns.set_style("whitegrid")
    font_style = {"family": "Times New Roman", "size": 12}
    plt.rc("font", **font_style)
    plt.figure(figsize=(6, 3))

    fig = sns.boxplot(data=scores_df_13, palette="Grays")
    fig.set_yticks(0.4 + 0.1 * np.arange(7, dtype=int))
    # fig.set_title("Individual scores")
    fig.set_xlabel("Mean source reliability")
    fig.set_ylabel("Score")
    plt.savefig(
        "figures/individual_scores.eps", bbox_inches="tight", dpi=800, format="eps"
    )
    plt.savefig("figures/individual_scores.png", bbox_inches="tight", dpi=800)
    plt.close()


def df_individual_scores(date="202412"):
    files = [
        file
        for file in os.listdir("data")
        if file[:10] == "simulation" and date in file and "README" not in file
    ]
    data_scores = np.array([])
    for file in files:
        df = pd.read_csv(f"data/{file}")
        rel_mean = df.at[0, "reliability_mean"]
        n_sources = df.at[0, "n_sources"]
        heuristic_size = df.at[0, "heuristic_size"]
        reliability_distribution = ("equi", (rel_mean - 0.1, rel_mean + 0.1))
        sources = Sources(n_sources, reliability_distribution)
        n_possible_heuristics = comb(n_sources, heuristic_size)
        team = generate_expert_team(sources, heuristic_size, n_possible_heuristics)
        data = np.array([agent.score for agent in team.members])
        data_mean = data.mean()
        data_std = data.std()
        data_max = data.max()
        data_min = data.min()
        data_scores = np.concatenate(
            [
                data_scores,
                [n_sources, rel_mean, data_mean, data_std, data_max, data_min],
            ]
        )

    data_scores = np.reshape(data_scores, (10, 6))
    scores_df = pd.DataFrame(
        data_scores, columns=["n_sources", "rel_mean", "mean", "std", "max", "min"]
    )
    scores_df.sort_values("rel_mean")
    return scores_df


if __name__ == "__main__":
    boxplot_individual_scores()
