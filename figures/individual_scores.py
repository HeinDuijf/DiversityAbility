from math import comb

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from models.generate_teams import generate_expert_team
from models.sources import Sources


def boxplot_individual_scores(n_sources: int = 13, heuristic_size: int = 5, show=False):
    scores_df = pd.DataFrame()
    rel_mean_list = [0.55, 0.6, 0.65, 0.7, 0.75]
    for rel_mean in rel_mean_list:
        reliability_distribution = ("equi", rel_mean, 0.2)
        sources = Sources(n_sources, reliability_distribution)
        n_possible_heuristics = comb(n_sources, heuristic_size)
        team = generate_expert_team(sources, heuristic_size, n_possible_heuristics)
        data = np.array([agent.score for agent in team.members])
        data_df = pd.DataFrame(data, columns=[rel_mean])
        scores_df = pd.concat([scores_df, data_df], axis=1)

    sns.set_style("whitegrid")
    font_style = {"family": "Times New Roman", "size": 12}
    plt.rc("font", **font_style)
    plt.figure(figsize=(6, 3))

    fig = sns.boxplot(data=scores_df, palette="Grays")
    fig.set_yticks(0.4 + 0.1 * np.arange(7, dtype=int))
    # fig.set_title("Individual scores")
    fig.set_xlabel("Mean source reliability")
    fig.set_ylabel("Score")
    if show:
        plt.show()

    plt.savefig(
        "./figures/images/individual_scores.eps",
        bbox_inches="tight",
        dpi=800,
        format="eps",
    )
    plt.savefig("./figures/images/individual_scores.png", bbox_inches="tight", dpi=800)
    plt.close()


def df_individual_scores(n_sources: int = 13, heuristic_size: int = 5):
    data_scores = np.array([])
    scores_df = pd.DataFrame()
    rel_mean_list = [0.55, 0.6, 0.65, 0.7, 0.75]
    for n_sources in [13, 17]:
        for rel_mean in rel_mean_list:
            reliability_distribution = ("equi", rel_mean, 0.2)
            sources = Sources(n_sources, reliability_distribution)
            n_possible_heuristics = comb(n_sources, heuristic_size)
            team = generate_expert_team(sources, heuristic_size, n_possible_heuristics)
            data = np.array([agent.score for agent in team.members])
            data = np.array([agent.score for agent in team.members])
            data_mean = data.mean() * 100
            data_std = data.std() * 100
            data_max = data.max() * 100
            data_min = data.min() * 100
            data_5 = np.percentile(data, 5) * 100
            data_25 = np.percentile(data, 25) * 100
            data_75 = np.percentile(data, 75) * 100
            data_95 = np.percentile(data, 95) * 100
            data_scores = np.concatenate(
                [
                    data_scores,
                    [
                        f"{n_sources:.0f}",
                        f"{rel_mean * 100:.0f}",
                        f"{data_mean:.1f}",
                        f"{data_min:.1f}",
                        f"{data_5:.1f}",
                        f"{data_25:.1f}",
                        f"{data_75:.1f}",
                        f"{data_95:.1f}",
                        f"{data_max:.1f}",
                        f"{data_std:.1f}",
                    ],
                ]
            )

    data_scores = np.reshape(data_scores, (10, 10))
    scores_df = pd.DataFrame(
        data_scores,
        columns=[
            "n_sources",
            "rel_mean",
            "mean",
            "min",
            "5th_pct",
            "25th_pct",
            "75th_pct",
            "95th_pct",
            "max",
            "std",
        ],
    )
    scores_df.style.format(
        subset=[
            "mean",
            "std",
            "max",
            "min",
            "5th_pct",
            "25th_pct",
            "75th_pct",
            "95th_pct",
        ],
        precision=3,
    )
    scores_df.style.format(subset=["n_sources"], precision=0)
    scores_df.sort_values("rel_mean", inplace=True)
    return scores_df


if __name__ == "__main__":
    boxplot_individual_scores()
