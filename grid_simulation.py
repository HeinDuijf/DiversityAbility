import pandas as pd
from IPython.display import display

from simulation import Simulation


class GridSimulation:
    def __init__(
        self,
        team_types: list,
        n_sources_list: list,
        reliability_distribution_list: list,
        n_samples: int,
        heuristic_size: int | list = 5,
        team_size: int = 9,
        estimate_sample_size: int | None = None,
    ):
        self.team_types = team_types
        self.n_sources_list = n_sources_list
        self.reliability_distribution_list = reliability_distribution_list
        self.n_samples = n_samples
        self.heuristic_size = heuristic_size
        self.team_size = team_size
        self.estimate_sample_size = estimate_sample_size

    def run(self):
        params_df = self.create_parameter_df()
        display(params_df)
        total = len(params_df)
        for idx, params in params_df.iterrows():
            # convert to dict and turn NaN values into None
            params_dict = params.where(pd.notnull(params), None).to_dict()
            print(f"Running simulation {idx} out of {total}...")
            Simulation(**params_dict).run()

    def create_parameter_df(self):
        data = [
            {
                "team_types": self.team_types,
                "n_sources": n_sources,
                "reliability_distribution": rel_dist,
                "heuristic_size": self.heuristic_size,
                "team_size": self.team_size,
                "n_samples": self.n_samples,
                "estimate_sample_size": None,
            }
            for n_sources in self.n_sources_list
            for rel_dist in self.reliability_distribution_list
        ]
        for item in data:
            if item["n_sources"] > 20:
                item["estimate_sample_size"] = self.estimate_sample_size
        return pd.DataFrame(data=data)


if __name__ == "__main__":
    GridSimulation(
        team_types=["expert", "diverse"],
        n_sources_list=[13],
        reliability_distribution_list=[("equi", rel_mean, 0.2) for rel_mean in [0.55]],
        n_samples=5,
        estimate_sample_size=5,
    ).run()
