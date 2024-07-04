import pandas as pd

from simulation import Simulation

if __name__ == "__main__":
    columns = [
        "team_types",
        "number_of_agents",
        "number_of_communities",
        "number_of_voting_simulations",
        "source_degree",
        "sources_reliability_distribution",
        "group_size",
        "number_of_sources",
    ]
    team_types = ["best", "most_divers", "random"]
    data = [
        [team_types, 20, 10**4, 10**4, 5, rel_range, group_size, n_sources]
        for n_sources in [11, 21, 31]
        for group_size in [5, 11, 21]
        for rel_range in [(0.45, 0.65), (0.5, 0.7), (0.55, 0.75), (0.6, 0.8)]
    ]
    df = pd.DataFrame(data=data, columns=columns)
    print(df)
    for row in df.iterrows():
        print(f"Simulation {row[0]}")
        params = row[1]
        Simulation(**params).run()
