from simulation.grid_simulation import GridSimulation

if __name__ == "__main__":
    rels = [
        ("unidist", rel_range)
        for rel_range in [(0.45, 0.65), (0.5, 0.7), (0.55, 0.75), (0.6, 0.8)]
    ]
    GridSimulation(
        team_types=["expert", "diverse"],
        n_sources_list=[13, 17, 21],
        reliability_distribution_list=rels,
        n_samples=10**4,
    )
