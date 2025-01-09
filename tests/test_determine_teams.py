import utils.config as cfg
from models.generate_teams import (
    generate_diverse_team,
    generate_expert_team,
    generate_random_team,
)
from models.sources import Sources
from models.team import Team


def check_team(team: Team):
    for agent in team.agents:
        assert len(team.source_network[agent]) == team.source_degree


def test_expert_team():
    pass


# def test_best_group():
#     global community_example
#     heuristic_size = 5
#     team_size = 3
#     sources = Sources(11)
#     team = expert_team(sources, heuristic_size, team_size)
#     assert len(team.members) == team_size

#     agent_dict = {
#         agent: community_example.source_network.nodes[agent][cfg.agent_competence]
#         for agent in community_example.agents
#     }
#     competences = list(set(agent_dict.values()))
#     competences.sort(reverse=True)
#     best_competences = competences[:team_size]
#     for k, competence in enumerate(best_competences):
#         assert competence <= team.source_network.nodes[k][cfg.agent_competence]
#     check_team(team)


# def test_random_group():
#     global community_example
#     group_size = 5
#     team = random_team(community_example, group_size)
#     assert len(team.agents) == group_size
#     check_team(team)


# def test_diverse_team():
#     global community_example
#     group_size = 7
#     team = diverse_team(community_example, group_size)
#     assert len(team.agents) == group_size
#     check_team(team)
