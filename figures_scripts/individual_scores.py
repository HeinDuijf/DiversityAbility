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
        "figures/individual_scores.eps", bbox_inches="tight", dpi=800, format="eps"
    )
    plt.savefig("figures/individual_scores.png", bbox_inches="tight", dpi=800)
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
