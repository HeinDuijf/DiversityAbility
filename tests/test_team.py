import utils.config as cfg
from models.agent import Agent
from models.sources import Sources
from models.team import Team


def check_team_attributes(team: Team, params: dict):
    assert team.members == params["members"]
    assert team.sources == params["sources"]
    assert team.size == len(params["members"])


def test_team():
    sources = Sources(11)
    for source in sources.sources:
        sources.set_valence(source, cfg.vote_for_positive)
    members = [
        Agent(0, [0, 1, 2], sources),
        Agent(1, [1, 2, 3], sources),
        Agent(2, [2, 3, 4], sources),
    ]

    params = {"members": members, "sources": sources}
    team = Team(**params)

    check_team_attributes(team, params)

    assert team.aggregate() == cfg.vote_for_positive
