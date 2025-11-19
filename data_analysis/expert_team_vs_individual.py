import pandas as pd

from models.generate_teams import generate_expert_team
from models.sources import Sources


def produce_df_expert_team_individual(
    outcome: str = "accuracy_opinion", n_decimals=3
) -> pd.DataFrame:
    results: list = []
    for n_sources in [13, 17]:
        for rel_mean in [0.55, 0.6, 0.65, 0.7, 0.75]:
            heuristic_size = 5
            sources = Sources(n_sources, ("equi", rel_mean, 0.2))
            team_dummy = generate_expert_team(sources, heuristic_size, 1)
            best_individual = team_dummy.members[0]
            best_individual_score = best_individual.score

            expert_team = generate_expert_team(sources, heuristic_size, team_size=9)
            expert_team_outcome = 0.0
            if outcome == "accuracy_opinion":
                expert_team_outcome, _ = expert_team.accuracy_opinion()
            elif outcome == "accuracy_evidence":
                expert_team_outcome = expert_team.accuracy_evidence()
            elif outcome == "accuracy_bounded":
                expert_team_outcome, _ = expert_team.accuracy_bounded()

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
