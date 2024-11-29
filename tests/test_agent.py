import utils.config as cfg
from models.agent import Agent
from models.sources import Sources


def check_agent_attributes(agent: Agent, params: dict):
    assert agent.no == params["no"]
    assert agent.heuristic == params["heuristic"]
    assert agent.sources == params["sources"]
    assert agent.score < 1
    assert 0 < agent.score
    assert agent.opinion in [cfg.vote_for_negative, cfg.vote_for_positive]


def test_agent():
    sources_1 = Sources(5)
    params_1 = {"no": 0, "heuristic": [0, 2, 4], "sources": sources_1}
    agent_1 = Agent(**params_1)
    check_agent_attributes(agent_1, params_1)
