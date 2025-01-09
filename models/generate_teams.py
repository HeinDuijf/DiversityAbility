import random as rd
import time

from models.agent import Agent
from models.sources import Sources
from models.team import Team
from utils.basic_functions import calculate_diversity


def generate_expert_team(sources: Sources, heuristic_size: int, team_size: int):
    possible_agents = [
        Agent(id, heuristic, sources)
        for id, heuristic in enumerate(sources.all_heuristics(heuristic_size))
    ]
    agent_score_tuples = [[agent, agent.score] for agent in possible_agents]
    agent_score_tuples.sort(key=lambda item: item[1], reverse=True)
    best_agents = [agent for [agent, _] in agent_score_tuples[:team_size]]
    return Team(best_agents, sources)


def generate_diverse_team(sources: Sources, heuristic_size: int, team_size: int):
    possible_agents = (
        Agent(id, heuristic, sources)
        for id, heuristic in enumerate(sources.all_heuristics(heuristic_size))
    )
    diversity_dict = {agent: 0 for agent in possible_agents}
    diverse_group = []
    for _ in range(team_size):
        max_diversity = max(diversity_dict.values())
        new_member = rd.choice(
            [
                agent
                for (agent, diversity) in diversity_dict.items()
                if diversity == max_diversity
            ]
        )
        diverse_group.append(new_member)
        diversity_dict.pop(new_member)
        for agent in diversity_dict.keys():
            diversity_dict[agent] += calculate_diversity(
                agent.heuristic, new_member.heuristic
            )
    return Team(diverse_group, sources)


def generate_random_team(sources: Sources, heuristic_size: int, team_size: int):
    all_heuristics = list(sources.all_heuristics(heuristic_size))
    random_heuristics = rd.sample(all_heuristics, team_size)
    random_group = [
        Agent(no, heuristic, sources) for no, heuristic in enumerate(random_heuristics)
    ]
    return Team(random_group, sources)


if __name__ == "__main__":
    sources = Sources(n_sources=21)
    start = time.time()
    team = generate_diverse_team(sources, heuristic_size=5, team_size=9)
    mid = time.time()
    print(f"Accuracy team: {team.accuracy()}")
    stop = time.time()
    print(f"Time to determine team = {mid - start}")
    print(f"Time to calculate accuracy = {stop - mid}")
