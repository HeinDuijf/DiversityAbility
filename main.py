from grid_simulation import GridSimulation

if __name__ == "__main__":
    rels = [("equi", rel_mean, 0.2) for rel_mean in [0.55, 0.6, 0.65, 0.7, 0.75]]

    GridSimulation(
        team_types=["expert", "diverse"],
        n_sources_list=[13, 17],
        reliability_distribution_list=rels,
        n_samples=10**4,
    ).run()
