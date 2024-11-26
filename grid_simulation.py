import pandas as pd

from simulation import Simulation


class GridSimulation:
    def __init__(
        self,
        team_types: list,
        n_sources_list: list,
        reliability_distribution_list: list,
        n_samples: int,
    ):
        self.team_types = team_types
        self.n_sources_list = n_sources_list
        self.reliability_distribution_list = reliability_distribution_list
        self.n_samples = n_samples

    def run(self):
        params_df = self.create_parameter_df()
        print(params_df)
        for row in params_df.iterrows():
            print(f"Running simulation {row[0]}")
            params = row[1]
            Simulation(**params).run()

    def create_parameter_df(self):
        data = [
            {
                "team_types": self.team_types,
                "n_sources": n_sources,
                "reliability_distribution": rel_dist,
                "heuristic_size": 5,
                "team_size": 9,
                "n_samples": self.n_samples,
            }
            for n_sources in self.n_sources_list
            for rel_dist in self.reliability_distribution_list
        ]
        return pd.DataFrame(data=data)


if __name__ == "__main__":
    GridSimulation(
        team_types=["expert", "diverse"],
        n_sources_list=[11, 13],
        reliability_distribution_list=[
            ("unidist", rel_range) for rel_range in [(0.45, 0.65)]
        ],
        n_samples=10,
    ).run()
