import copy

import networkx as nx
from community import Community
from utils import config as cfg

params_blank = {
    "number_of_agents": 3,
    "number_of_sources": 3,
    "source_degree": 2,
    "edges": None,
    "create": False,
}
community_blank = Community(**params_blank)
community_example: Community = copy.deepcopy(community_blank)
community_from_edges: Community = copy.deepcopy(community_blank)
community_simple_source = copy.deepcopy(community_blank)

params_blank["create"] = True
params_example: dict = copy.deepcopy(params_blank)
params_from_edges: dict = copy.deepcopy(params_blank)
params_simple_source: dict = copy.deepcopy(params_blank)


def setup_module():
    global community_example
    global community_from_edges
    global community_simple_source
    global params_example
    global params_from_edges
    global params_simple_source

    params_example["number_of_agents"] = 100
    params_example["influence_degree"] = 6
    community_example = Community(**params_example)

    edges = list(nx.complete_graph(30, nx.DiGraph()).edges)
    params_from_edges = {
        "number_of_agents": 200,
        "influence_degree": 2,
        "edges": edges,
    }
    community_from_edges = Community(**params_from_edges)

    params_simple_source["number_of_agents"] = 3
    params_simple_source["number_of_sources"] = 3
    params_simple_source["source_degree"] = 3
    params_simple_source["influence_degree"] = 1

    community_simple_source = Community(**params_simple_source)


def check_number_of_agents(community: Community, params: dict):
    assert community.influence_network.number_of_nodes() == params["number_of_agents"]
    assert community.number_of_agents == params["number_of_agents"]
    assert community.agents == list(range(params["number_of_agents"]))


def check_influence_degree(community: Community, params: dict):
    assert all(
        [
            community.influence_network.out_degree[node] == params["influence_degree"]
            for node in community.agents
        ]
    )


def check_source_network(community: Community):
    assert all(
        [
            all(
                [
                    target in community.sources
                    for target in community.source_network[agent]
                ]
            )
            for agent in community.agents
        ]
    )
    assert all(
        [len(community.source_network[source]) == 0 for source in community.sources]
    )


def check_source_degree(community):
    assert all(
        [
            len(community.source_network[agent]) == community.source_degree
            for agent in community.agents
        ]
    )


def test_set_source_network():
    global community_simple_source
    new_source_network = nx.DiGraph()
    new_source_network.add_nodes_from(community_simple_source.sources)
    new_source_network.add_nodes_from(["s100", "s101"])
    new_source_network.add_nodes_from(community_simple_source.agents)
    new_source_network.add_nodes_from([100, 101])
    new_source_network.remove_nodes_from([0])
    new_source_network.add_edges_from([(0, "s0"), (1, "s2")])
    new_community = copy.deepcopy(community_simple_source)
    new_community.set_source_network(new_source_network)
    new_agents = community_simple_source.agents + [100, 101]
    assert set(new_community.sources) == set(
        community_simple_source.sources + ["s100", "s101"]
    )
    assert set(new_community.agents) == set(new_agents)
    assert set(new_community.sources) == set(
        [
            source
            for source in new_community.source_network.nodes()
            if isinstance(source, str)
        ]
    )
    check_source_network(community_simple_source)
    check_source_network(new_community)
    assert set(new_community.source_network[0]) == {"s0"}
    assert set(new_community.source_network[1]) == {"s2"}


def check_community(community: Community, params: dict):
    check_number_of_agents(community, params)
    if params["edges"] is None:
        check_influence_degree(community, params)
    check_source_network(community)


def test_create_initial_network_without_homophilic_attachment():
    global community_example
    global params_example
    check_number_of_agents(community_example, params_example)
    check_influence_degree(community_example, params_example)


# def test_create_initial_network_with_homophilic_attachment():
#     global community_with_hom
#     global params_with_hom
#     check_number_of_agents(community_with_hom, params_with_hom)
#     check_influence_degree(community_with_hom, params_with_hom)


def test_create_network_from_edges():
    global community_from_edges
    global params_from_edges
    check_number_of_agents(community_from_edges, params_from_edges)
    assert set(params_from_edges["edges"]) == set(community_from_edges.edges)
    assert set(params_from_edges["edges"]) == set(
        community_from_edges.influence_network.edges()
    )


def test_create_network():
    global community_example
    global params_example
    check_community(community_example, params_example)
    # global community_with_hom
    # global params_with_hom
    # check_community(community_with_hom, params_with_hom)
    global community_from_edges
    global params_from_edges
    check_community(community_from_edges, params_from_edges)


# def test_rewire_network():
#     nodes_mass = community_example.agents_mass
#     nodes_elite = community_example.agents_elite
#     network_pre = community_example.influence_network
#     network_post = community_example.rewire_network(network_pre)
#     edges_to_mass_pre = [
#         (source, target)
#         for (source, target) in network_pre.edges()
#         if target in nodes_mass
#     ]
#     edges_to_mass_post = [
#         (source, target)
#         for (source, target) in network_post.edges()
#         if target in nodes_mass
#     ]
#     assert len(edges_to_mass_pre) == len(edges_to_mass_post)
#     edges_to_elite_pre = [
#         (source, target)
#         for (source, target) in network_pre.edges()
#         if target in nodes_elite
#     ]
#     edges_to_elite_post = [
#         (source, target)
#         for (source, target) in network_post.edges()
#         if target in nodes_elite
#     ]
#     assert len(edges_to_elite_pre) == len(edges_to_elite_post)


def test_add_agents_from():
    community = Community(number_of_agents=20)
    initial_agents = community.agents.copy()
    community.add_agents_from([99, 33])
    assert set(initial_agents + [99, 33]) == set(community.agents)
    assert all([agent in community.source_network.nodes() for agent in [99, 33]])
    assert set(community.agents) == set(community.influence_network.nodes())
    assert community.number_of_agents == 20 + 2


def test_remove_agents_from():
    community = Community(number_of_agents=20)
    initial_agents = community.agents.copy()
    new_agents = [agent for agent in initial_agents if agent != 1 and agent != 3]
    community.remove_agents_from([1, 3])
    assert set(new_agents) == set(community.agents)
    assert all([agent not in community.source_network.nodes() for agent in [1, 3]])
    assert set(community.agents) == set(community.influence_network.nodes())
    assert community.number_of_agents == 20 - 2


def test_add_sources_from():
    community = Community(number_of_agents=20, number_of_sources=10)
    initial_sources = community.sources
    community.add_sources_from(["s99", "s33"])
    assert all([source in initial_sources for source in community.sources])
    assert all(
        [
            source in ["s99", "s33"]
            for source in community.sources
            if source not in initial_sources
        ]
    )
    assert community.number_of_sources == 10 + 2


def test_add_influence_edges_from():
    global community_simple_source
    global params_simple_source
    community_new = copy.deepcopy(community_simple_source)
    params_new = copy.deepcopy(params_simple_source)
    community_new.add_influence_edges_from(
        [
            (agent1, agent2)
            for agent1 in community_new.agents
            for agent2 in community_new.agents
            if (agent1, agent2) not in community_simple_source.influence_network.edges
            if agent1 != agent2
        ]
    )
    params_new["influence_degree"] = 2
    check_community(community_new, params_new)


def test_initialize_attributes():
    global community_example
    community_example.initialize_attributes()
    assert all(
        [
            0
            <= community_example.influence_network.nodes[agent][cfg.agent_competence]
            <= 1
            for agent in community_example.agents
        ]
    )
    assert all(
        0 <= community_example.influence_network.edges[edge][cfg.edge_diversity] <= 1
        for edge in community_example.influence_network.edges
    )


def test_update_votes():
    global community_example
    community_example.update_votes()
    for agent in community_example.agents:
        agent_vote = community_example.influence_network.nodes[agent][cfg.agent_vote]
        agent_has_vote: bool = (
            agent_vote == cfg.vote_for_positive or agent_vote == cfg.vote_for_negative
        )
        assert agent_has_vote


def test_update_opinions():
    global community_example
    community_example.update_opinions()
    for node in community_example.agents:
        node_opinion = community_example.influence_network.nodes[node][
            cfg.agent_opinion
        ]
        node_has_opinion: bool = (
            node_opinion == cfg.vote_for_positive
            or node_opinion == cfg.vote_for_negative
        )
        assert node_has_opinion


def test_estimated_community_accuracy():
    # Todo: test estimate_community_accuracy
    pass


def test_vote():
    # Todo: test vote
    pass


def test_calculate_diversity():
    global community_simple_source
    assert all(
        [
            community_simple_source.calculate_edge_diversity(edge) == 0
            for edge in community_simple_source.influence_network.edges
        ]
    )

    community_simple_source.source_network.remove_edge(0, "s0")
    community_simple_source.source_network.remove_edge(1, "s1")
    assert community_simple_source.calculate_edge_diversity((0, 1)) == 0.5

    community_simple_source.source_network.remove_edge(0, "s2")
    community_simple_source.source_network.remove_edge(1, "s2")
    assert community_simple_source.calculate_edge_diversity((0, 1)) == 1


def test_best_group():
    global community_simple_source
    assert all(
        [
            agent in community_simple_source.agents
            for agent in community_simple_source.optimal_group(1)
        ]
    )
