from community import Community
from determine_teams import best_team, diverse_team, random_team

community_example: Community
params_example: dict


def setup_module():
    global community_example
    global params_example

    params = {
        "number_of_agents": 100,
        "number_of_sources": 11,
        "influence_degree": 5,
        "source_degree": 5,
        "edges": None,
        "create": True,
    }
    community_example = Community(**params)


def test_best_group():
    global community_example
    group_size = 3
    result = best_team(community_example, group_size)
    group = result["group"]
    assert len(group) == group_size


def test_random_group():
    global community_example
    group_size = 3
    result = random_team(community_example, group_size)
    group = result["group"]
    assert len(group) == group_size
