import random as rd
from itertools import combinations

from community import Community
from scripts.basic_functions import calculate_diversity


def best_group(community: Community, group_size: int):
    possible_source_sets = list(
        combinations(community.sources, community.source_degree)
    )
    competence_tuples = [
        [source_set, community.calculate_competence(sources=source_set)]
        for source_set in possible_source_sets
    ]
    competence_tuples.sort(key=lambda item: item[1], reverse=True)
    best_source_sets = [
        source_set for [source_set, competence] in competence_tuples[:group_size]
    ]
    best_agents = list(range(group_size))
    source_net = community.source_network.copy()
    source_net.remove_nodes_from(community.agents)
    source_net.add_nodes_from(best_agents)
    for agent in best_agents:
        edges = [(agent, source) for source in best_source_sets[agent]]
        source_net.add_edges_from(edges)
    result = {"group": best_agents, "source_network": source_net}
    return result


def most_diverse_group(community: Community, group_size: int):
    possible_source_sets = list(
        combinations(community.sources, community.source_degree)
    )
    diversity_dict = {source_set: 0 for source_set in possible_source_sets}
    diverse_source_sets = []
    for _ in range(group_size):
        max_diversity = max(diversity_dict.values())
        new_source_set = rd.choice(
            [
                source_set
                for (source_set, diversity) in diversity_dict.items()
                if diversity == max_diversity
            ]
        )
        diverse_source_sets.append(new_source_set)
        for source_set in diversity_dict.keys():
            diversity_dict[source_set] += calculate_diversity(
                source_set, new_source_set
            )
    diverse_group = list(range(group_size))
    source_net = community.source_network.copy()
    source_net.remove_nodes_from(community.agents)
    source_net.add_nodes_from(diverse_group)
    for agent in diverse_group:
        edges = [(agent, source) for source in diverse_source_sets[agent]]
        source_net.add_edges_from(edges)
    result = {"group": diverse_group, "source_network": source_net}
    return result


def random_group(community: Community, group_size: int):
    possible_source_sets = list(
        combinations(community.sources, community.source_degree)
    )
    random_source_sets = rd.sample(possible_source_sets, group_size)
    random_agents = list(range(group_size))
    source_net = community.source_network.copy()
    source_net.remove_nodes_from(community.agents)
    source_net.add_nodes_from(random_agents)
    for agent in random_agents:
        edges = [(agent, source) for source in random_source_sets[agent]]
        source_net.add_edges_from(edges)
    result = {"group": random_agents, "source_network": source_net}
    return result
