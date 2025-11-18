import copy
import itertools as it
import time
from concurrent.futures import ProcessPoolExecutor as Pool
from functools import partial

import pandas as pd
from tqdm.auto import tqdm

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
        filename_csv: str | None = None,
        team_types: list = ["expert", "diverse"],
        n_sources: int = 13,
        reliability_distribution=("equidist", 0.6, 0.2),
        heuristic_size: int = 5,
        team_size: int = 9,
        n_samples: int = 10**3,
        estimate_sample_size: int | None = None,
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
        # Run simulations in parallel for accuracies and bounded pool accuracies
        with Pool() as pool:
            params, total = self.get_params()
            results_df = pd.DataFrame(
                tqdm(
                    pool.map(self.team_simulate, params),
                    total=total,
                    desc="Calculating/estimating accuracy and bounded pool accuracy",
                )
            )

        # Run simulations in parallel for pool accuracies
        with Pool() as pool:
            team_simulate_pool = partial(self.team_simulate, pool=True)
            total = len(self.team_types)
            results_pool = pd.DataFrame(
                tqdm(
                    pool.map(team_simulate_pool, self.team_types),
                    total=total,
                    desc="Calculating pool accuracy",
                )
            )

        # Update pool accuracies in results_df
        for team_type in self.team_types:
            team_pool_accuracy = results_pool[results_pool["team_type"] == team_type][
                "pool_accuracy"
            ].mean()
            results_df.loc[results_df["team_type"] == team_type, "pool_accuracy"] = (
                team_pool_accuracy
            )

        # Save results to CSV
        results_df.to_csv(self.filename_csv)

    def get_params(self):
        params = []
        total: int = 0
        if "expert" in self.team_types:
            params = it.chain(params, ["expert"])
            total += 1
        for team_type in self.team_types:
            if "diverse" in team_type:
                params = it.chain(params, it.repeat(team_type, self.n_samples))
                total += self.n_samples
        return params, total

    def team_simulate(self, team_type: str, pool: bool = False):
        team_params = {
            "sources": copy.deepcopy(self.sources),
            "heuristic_size": self.heuristic_size,
            "team_size": self.team_size,
        }
        if team_type == "expert":
            team = generate_expert_team(**team_params)
            accuracy, precision = team.accuracy()
            bounded_pool_accuracy, bounded_precision = team.bounded_pool_accuracy()
        elif team_type == "diverse":
            team = generate_diverse_team(**team_params)
            accuracy, precision = team.accuracy(
                estimate_sample_size=self.estimate_sample_size
            )
            bounded_pool_accuracy, bounded_precision = team.bounded_pool_accuracy(
                estimate_sample_size=self.estimate_sample_size
            )
        elif team_type == "random":
            team = generate_random_team(**team_params)
            accuracy, precision = team.accuracy(
                estimate_sample_size=self.estimate_sample_size
            )
            bounded_pool_accuracy, bounded_precision = team.bounded_pool_accuracy(
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
            bounded_pool_accuracy, bounded_precision = team.bounded_pool_accuracy(
                estimate_sample_size=self.estimate_sample_size
            )
        else:
            raise ValueError(f"Unknown team type: {team_type}")

        heuristic_str = str(self.heuristic_size)  # type: ignore
        if isinstance(self.heuristic_size, list):
            heuristic_str = str(heuristic_str)[1:-1].replace(", ", "-")  # type: ignore

        results_dict = {
            "team_size": self.team_size,
            "n_sources": self.n_sources,
            "heuristic_size": heuristic_str,
            "reliability_mean": self.reliability_distribution[1],
            "reliability_range": self.reliability_distribution[2],
            "n_samples": self.n_samples,
            "team_type": team_type,
            "accuracy": accuracy,
            "precision": precision,
            "pool_accuracy": team.pool_accuracy() if pool else None,
            "bounded_pool_accuracy": bounded_pool_accuracy,
            "bounded_precision": bounded_precision,
            "diversity": team.diversity(),
            "average": team.average(),
        }
        return results_dict


if __name__ == "__main__":
    Simulation(n_sources=21, n_samples=2, estimate_sample_size=100).run()
