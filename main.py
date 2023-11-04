from simulation import Simulation

if __name__ == "__main__":
    params = {
        "team_types": ["best", "most_diverse", "random"],
        "source_reliability_range": (0.5, 0.7),
        "number_of_agents": 20,
        "number_of_communities": 10 ** 3,
        "number_of_voting_simulations": 10 ** 3,
        "source_degree": 5,
    }
    group_sizes = [5, 11]  # 21]
    sources_range = [11, 21]  # 21, 31]
    for number_of_sources in sources_range:
        for group_size in group_sizes:
            print(
                f"Started: Number of sources {number_of_sources} | Group size:"
                f" {group_size}"
            )
            Simulation(
                group_size=group_size, number_of_sources=number_of_sources, **params,
            ).run()
