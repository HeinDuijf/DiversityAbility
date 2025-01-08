import os

import pandas as pd

from models.determine_teams import expert_team
from models.sources import Sources


def produce_df_expert_team_individual(outcome: str = "accuracy", n_decimals=3):
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
        heuristic_size = df.at[0, "heuristic_size"]

        rel_range = (rel_mean - 0.1, rel_mean + 0.1)
        sources = Sources(n_sources, ("equi", rel_range))
        team_dummy = expert_team(sources, heuristic_size, 1)
        best_individual = team_dummy.members[0]

        expert_team_outcome = df.at[0, outcome]
        best_individual_score = best_individual.score

        individual_error = 1 - best_individual_score
        expert_team_error = 1 - expert_team_outcome

        if expert_team_error > individual_error:
            error_reduction = (
                100 * (expert_team_error - individual_error) / individual_error
            )
            # error_reduction = - (expert_error / diverse_error)
        elif individual_error > expert_team_error:
            error_reduction = (
                -100 * (individual_error - expert_team_error) / expert_team_error
            )
            # error_reduction = diverse_error / expert_error
        else:
            error_reduction = 0

        results.append(
            [
                n_sources,
                rel_mean,
                round(best_individual_score - expert_team_outcome, n_decimals),
                round(error_reduction),
            ]
        )
    columns = ["n_sources", "rel_mean", "difference", "error_reduction"]
    return pd.DataFrame(results, columns=columns)
