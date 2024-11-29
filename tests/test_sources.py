import utils.config as cfg
from models.sources import Sources


def check_sources_attributes(sources: Sources, params: dict):
    assert sources.n_sources == params["n_sources"]
    assert sources.reliability_distribution == params["reliability_distribution"]
    assert len(sources.sources) == params["n_sources"]
    rel_range = sources.reliability_distribution[1]
    assert all(
        min(rel_range) <= sources.reliabilities[source] for source in sources.sources
    )
    assert all(
        sources.reliabilities[source] <= max(rel_range) for source in sources.sources
    )
    assert all(
        sources.valences[source] in [cfg.vote_for_negative, cfg.vote_for_positive]
        for source in sources.sources
    )


def test_sources():
    params_1: dict = {
        "n_sources": 5,
        "reliability_distribution": ("unidist", (0.4, 0.7)),
    }
    params_2: dict = {
        "n_sources": 21,
        "reliability_distribution": ("unidist", (0.6, 0.8)),
    }

    sources_1 = Sources(**params_1)
    sources_2 = Sources(**params_2)

    check_sources_attributes(sources_1, params_1)
    check_sources_attributes(sources_2, params_2)

    all_heuristics = [
        (a, b) for a in sources_1.sources for b in sources_1.sources if a < b
    ]
    assert set(all_heuristics) == set(sources_1.all_heuristics(2))
