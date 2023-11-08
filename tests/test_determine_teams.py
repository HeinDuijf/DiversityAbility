import utils.config as cfg
from community import Community
from determine_teams import best_team, diverse_team, random_team

community_example: Community
params_example: dict


def setup_module():
    global community_example
    global params_example

    params = {
        "number_of_agents": 30,
        "number_of_sources": 11,
        "influence_degree": 5,
        "source_degree": 5,
        "edges": None,
        "create": True,
    }
    community_example = Community(**params)


def check_team(com: Community):
    global params_example
    for agent in com.agents:
        assert len(com.source_network[agent]) == com.source_degree


def test_best_group():
    global community_example
    group_size = 3
    team = best_team(community_example, group_size)
    assert len(team.agents) == group_size

    agent_dict = {
        agent: community_example.source_network.nodes[agent][cfg.agent_competence]
        for agent in community_example.agents
    }
    competences = list(set(agent_dict.values()))
    competences.sort(reverse=True)
    best_competences = competences[:group_size]
    for k, competence in enumerate(best_competences):
        assert competence <= team.source_network.nodes[k][cfg.agent_competence]
    check_team(team)


def test_random_group():
    global community_example
    group_size = 5
    team = random_team(community_example, group_size)
    assert len(team.agents) == group_size
    check_team(team)


def test_diverse_team():
    global community_example
    group_size = 7
    team = diverse_team(community_example, group_size)
    assert len(team.agents) == group_size
    check_team(team)
