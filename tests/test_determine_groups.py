from community import Community
from determine_groups import best_group, most_diverse_group, random_group

community: Community
params: dict


def setup_module():
    global community
    global params

    params = {
        "number_of_agents": 100,
        "number_of_sources": 11,
        "influence_degree": 5,
        "source_degree": 5,
        "probability_preferential_attachment": 0.6,
        "probability_homophilic_attachment": None,
        "edges": None,
        "create": True,
    }
    community = Community(**params)


def test_best_group():
    group_size = 3
    result = best_group(community, group_size)
    group = result["group"]
    assert len(group) == group_size


def test_random_group():
    group_size = 3
    result = random_group(community, group_size)
    group = result["group"]
    assert len(group) == group_size
