from grid_simulation import GridSimulation

if __name__ == "__main__":
    rels = [
        ("equi", rel_range)
        for rel_range in [
            (0.45, 0.65),
            (0.5, 0.7),
            # (0.55, 0.75),
            # (0.6, 0.8),
            # (0.65, 0.85),
        ]
    ]
    GridSimulation(
        team_types=["qualified_diverse_90", "diverse"],
        n_sources_list=[13],
        reliability_distribution_list=rels,
        n_samples=10**2,
        estimate_sample_size=10**2,
    ).run()
