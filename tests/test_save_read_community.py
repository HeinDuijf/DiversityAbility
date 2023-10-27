import os

from community import Community
from scripts.save_read_community import (
    community_compress,
    community_unpack,
    read_community_from_file,
    save_community_to_file,
)


def test_community_compress():
    params: dict = {
        "number_of_agents": 3,
        # "number_of_elites": 2,
        "influence_degree": 2,
        "number_of_sources": 11,
        "source_degree": 1,
        "probability_homophilic_attachment": 0.8,
        "probability_preferential_attachment": 0.4,
        "edges": [(0, 1), (0, 2), (1, 2), (1, 0), (2, 1)],
        "source_edges": [(0, "s0"), (1, "s1"), (2, "s2")],
    }
    community = Community(**params)
    community_compressed = community_compress(community)
    assert community_compressed["N"] == params["number_of_agents"]
    # assert community_compressed["E"] == params["number_of_elites"]
    assert community_compressed["d"] == params["influence_degree"]
    assert community_compressed["h"] == params["probability_homophilic_attachment"]
    assert community_compressed["pp"] == params["probability_preferential_attachment"]
    assert community_compressed[0] == "1,2"
    assert community_compressed[1] == "2,0"
    assert community_compressed[2] == "1"
    assert community_compressed["S0"] == "s0"
    assert community_compressed["S1"] == "s1"
    assert community_compressed["S2"] == "s2"


def test_community_unpack():
    community_compressed: dict = {
        "N": 3,
        # "E": 2,
        "d": 2,
        "NS": 11,
        "ds": 1,
        "h": 0.8,
        "pp": 0.4,
        "e": [(0, 1), (0, 2), (1, 2), (1, 0), (2, 1)],
        0: "1,2",
        1: "2,0",
        2: "1",
        "S0": "s0",
        "S1": "s1",
        "S2": "s2",
    }
    community_unpacked = community_unpack(community_compressed)
    assert community_unpacked.number_of_agents == community_compressed["N"]
    # assert community_unpacked.number_of_elites == community_compressed["E"]
    # assert community_unpacked.influence_degree == params["d"]
    assert (
        community_unpacked.probability_homophilic_attachment
        == community_compressed["h"]
    )
    assert (
        community_unpacked.probability_preferential_attachment
        == community_compressed["pp"]
    )
    for agent in community_unpacked.agents:
        if agent in community_compressed.keys():
            assert set(community_unpacked.influence_network[agent]) == set(
                [int(neighbor) for neighbor in community_compressed[agent].split(",")]
            )
    assert community_unpacked.number_of_sources == community_compressed["NS"]
    assert all(
        [
            set(list(community_unpacked.source_network[agent]))
            == set(community_compressed[f"S{agent}"].split(","))
            for agent in community_unpacked.agents
            if f"S{agent}" in community_compressed.keys()
        ]
    )


def test_save_and_read():
    params: dict = {
        "number_of_agents": 100,
        # "number_of_elites": 35,
        "influence_degree": 7,
        "probability_homophilic_attachment": None,
        "probability_preferential_attachment": 0.4,
    }
    community = Community(**params)
    save_community_to_file(filename="data/test_community", community=community)
    community_read = read_community_from_file(filename="data/test_community")
    assert community.number_of_agents == community_read.number_of_agents
    # assert community.number_of_elites == community_read.number_of_elites
    assert community.influence_degree == community_read.influence_degree
    assert (
        community.probability_homophilic_attachment
        == community_read.probability_homophilic_attachment
    )
    assert (
        community.probability_preferential_attachment
        == community_read.probability_preferential_attachment
    )
    community_edges = list(community.influence_network.edges())
    community2_edges = list(community_read.influence_network.edges())
    for edge in community_edges:
        assert edge in community2_edges
    os.remove("data/test_community.pickle")
