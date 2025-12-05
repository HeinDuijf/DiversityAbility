import numpy as np

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
    reliabilities = 0.5 * np.ones(11)
    reliabilities[:3] = [0.6, 0.6, 0.5]
    sources.reliabilities = reliabilities
    members = [
        Agent(0, [0, 1, 2], sources),
        Agent(1, [1, 2, 3], sources),
        Agent(2, [2, 3, 4], sources),
    ]

    params = {"members": members, "sources": sources}
    team = Team(**params)

    check_team_attributes(team, params)
    accuracy, _ = team.accuracy_opinion()
    assert team.aggregate() == cfg.vote_for_positive
    assert accuracy < team.accuracy_evidence()
    assert team.accuracy_evidence() > team.accuracy_bounded()
