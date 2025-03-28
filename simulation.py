import copy
import itertools as it
import time
from concurrent.futures import ProcessPoolExecutor as Pool

import pandas as pd
import tqdm

from models.generate_teams import (
    generate_diverse_team,
    generate_expert_team,
    generate_qualified_diverse_team,
    generate_random_team,
)
from models.sources import Sources


class Simulation:
    def __init__(
        self,
        filename_csv: str = None,
        team_types: list = ["expert", "diverse"],
        n_sources: int = 13,
        reliability_distribution=("equidist", (0.5, 0.7)),
        heuristic_size: int = 5,
        team_size: int = 9,
        n_samples: int = 10**3,
        estimate_sample_size: int = None,
    ):
        time_str = time.strftime("%Y%m%d_%H%M%S")
        self.filename_csv = filename_csv
        if filename_csv is None:
            self.filename_csv = f"data/simulation_{time_str}.csv"
        self.sources = Sources(
            n_sources=n_sources, reliability_distribution=reliability_distribution
        )
        self.n_sources = n_sources
        self.reliability_distribution = reliability_distribution

        self.team_types = team_types
        self.heuristic_size = heuristic_size
        self.team_size = team_size
        self.n_samples = n_samples
        self.estimate_sample_size = estimate_sample_size

    def run(self):
        with Pool() as pool:
            params, total = self.get_params()
            results_df = pd.DataFrame(
                tqdm.tqdm(
                    pool.map(self.team_simulate, params),
                    total=total,
                ),
            )
        results_df.to_csv(self.filename_csv)

    def get_params(self):
        params_set = []
        total: int = 0
        if "expert" in self.team_types:
            params_set = it.chain(params_set, ["expert"])
            total += 1
        for team_type in self.team_types:
            if "diverse" in team_type:
                params_set = it.chain(params_set, it.repeat(team_type, self.n_samples))
                total += self.n_samples
        return params_set, total

    def team_simulate(self, team_type: str):
        team_params = {
            "sources": copy.deepcopy(self.sources),
            "heuristic_size": self.heuristic_size,
            "team_size": self.team_size,
        }
        if team_type == "expert":
            team = generate_expert_team(**team_params)
            accuracy, precision = team.accuracy()
        elif team_type == "diverse":
            team = generate_diverse_team(**team_params)
            accuracy, precision = team.accuracy(
                estimate_sample_size=self.estimate_sample_size
            )
        elif team_type == "random":
            team = generate_random_team(**team_params)
            accuracy, precision = team.accuracy(
                estimate_sample_size=self.estimate_sample_size
            )
        elif "qualified_diverse" in team_type:
            qualified_percentile = float(team_type.split("_")[-1])
            team = generate_qualified_diverse_team(
                **team_params, qualifying_percentile=qualified_percentile
            )
            accuracy, precision = team.accuracy(
                estimate_sample_size=self.estimate_sample_size
            )

        reliability_mean = (
            self.reliability_distribution[1][1] - self.reliability_distribution[1][0]
        ) / 2 + self.reliability_distribution[1][0]
        # sources_reliability_distribution_str = str(
        #     self.sources_reliability_distribution
        # ).replace(",", " to")

        results_dict = {
            "team_size": self.team_size,
            "n_sources": self.n_sources,
            "heuristic_size": self.heuristic_size,
            "reliability_mean": reliability_mean,
            # "sources_reliability_dist_str": sources_reliability_distribution_str,
            "n_samples": self.n_samples,
            # "problem_difficulty": team.problem_difficulty(),
            "team_type": team_type,
            "accuracy": accuracy,
            "precision": precision,
            "pool_accuracy": team.pool_accuracy(),
            "bounded_pool_accuracy": team.bounded_pool_accuracy(),
            "diversity": team.diversity(),
            "average": team.average(),
        }
        return results_dict


if __name__ == "__main__":
    Simulation(n_sources=11, n_samples=10, estimate_sample_size=5).run()
