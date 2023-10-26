import networkx as nx
from community import Community
from scripts import config as cfg

params_blank = {
    "number_of_agents": 2,
    "number_of_elites": 0,
    "influence_degree": 0,
    "probability_preferential_attachment": None,
    "probability_homophilic_attachment": None,
    "edges": None,
}
community_blank = Community(**params_blank)
community_without_hom: Community = community_blank
community_with_hom: Community = community_blank
community_from_edges: Community = community_blank
community_simple_source = community_blank

params_without_hom: dict = {}
params_with_hom: dict = {}
params_from_edges: dict = {}
params_simple_source: dict = {}


def setup_module(module):
    global community_without_hom
    global community_with_hom
    global community_from_edges
    global community_simple_source
    global params_without_hom
    global params_with_hom
    global params_from_edges
    global params_simple_source

    params_without_hom = {
        "number_of_agents": 100,
        "number_of_elites": 20,
        "influence_degree": 6,
        "probability_preferential_attachment": 0.6,
        "probability_homophilic_attachment": None,
        "edges": None,
    }
    community_without_hom = Community(**params_without_hom)

    params_with_hom = {
        "number_of_agents": 200,
        "number_of_elites": 77,
        "influence_degree": 8,
        "probability_preferential_attachment": 0.6,
        "probability_homophilic_attachment": 0.7,
        "edges": None,
    }
    community_with_hom = Community(**params_with_hom)
    edges = list(nx.complete_graph(30, nx.DiGraph()).edges)
    params_from_edges = {
        "number_of_agents": 200,
        "number_of_elites": 5,
        "influence_degree": 2,
        "probability_preferential_attachment": 0.6,
        "probability_homophilic_attachment": 0.7,
        "edges": edges,
    }
    community_from_edges = Community(**params_from_edges)

    params_simple_source = {
        "number_of_agents": 2,
        "number_of_sources": 3,
        "source_degree": 3,
        "number_of_elites": 0,
        "influence_degree": 1,
        # "probability_preferential_attachment": None,
        "probability_homophilic_attachment": None,
        # "edges": [],
    }
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
        [
            len(community.source_network[agent]) == community.source_degree
            for agent in community.agents
        ]
    )
    assert all(
        [len(community.source_network[source]) == 0 for source in community.sources]
    )


def check_community(community: Community, params: dict):
    check_number_of_agents(community, params)
    if params["edges"] is None:
        check_influence_degree(community, params)
    check_source_network(community)


def test_create_initial_network_without_homophilic_attachment():
    global community_without_hom
    global params_without_hom
    check_number_of_agents(community_without_hom, params_without_hom)
    check_influence_degree(community_without_hom, params_without_hom)


def test_create_initial_network_with_homophilic_attachment():
    global community_with_hom
    global params_with_hom
    check_number_of_agents(community_with_hom, params_with_hom)
    check_influence_degree(community_with_hom, params_with_hom)


def test_create_network_from_edges():
    global community_from_edges
    global params_from_edges
    check_number_of_agents(community_from_edges, params_from_edges)
    assert set(params_from_edges["edges"]) == set(community_from_edges.edges)
    assert set(params_from_edges["edges"]) == set(
        community_from_edges.influence_network.edges()
    )


def test_create_network():
    global community_without_hom
    global params_without_hom
    check_community(community_without_hom, params_without_hom)
    global community_with_hom
    global params_with_hom
    check_community(community_with_hom, params_with_hom)
    global community_from_edges
    global params_from_edges
    check_community(community_from_edges, params_from_edges)


def test_rewire_network():
    nodes_mass = community_without_hom.agents_mass
    nodes_elite = community_without_hom.agents_elite
    network_pre = community_without_hom.influence_network
    network_post = community_without_hom.rewire_network(network_pre)
    edges_to_mass_pre = [
        (source, target)
        for (source, target) in network_pre.edges()
        if target in nodes_mass
    ]
    edges_to_mass_post = [
        (source, target)
        for (source, target) in network_post.edges()
        if target in nodes_mass
    ]
    assert len(edges_to_mass_pre) == len(edges_to_mass_post)
    edges_to_elite_pre = [
        (source, target)
        for (source, target) in network_pre.edges()
        if target in nodes_elite
    ]
    edges_to_elite_post = [
        (source, target)
        for (source, target) in network_post.edges()
        if target in nodes_elite
    ]
    assert len(edges_to_elite_pre) == len(edges_to_elite_post)


def test_add_agents_from():
    community = Community(number_of_agents=20)
    initial_agents = community.agents
    community.add_agents_from([99, 33])
    assert all([agent in initial_agents for agent in community.agents])
    assert all(
        [agent in [99, 33] for agent in community.agents if agent not in initial_agents]
    )
    assert community.number_of_agents == 20 + 2


def test_remove_agents_from():
    community = Community(number_of_agents=20)
    initial_agents = community.agents
    community.remove_agents_from([1, 3])
    assert all([agent in initial_agents for agent in community.agents])
    assert all([agent not in [1, 3] for agent in community.agents])
    assert all([agent not in community.source_network.nodes() for agent in [1, 3]])
    assert all(
        [agent in community.agents for agent in community.influence_network.nodes()]
    )
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


def test_initialize_attributes():
    global community_with_hom
    community_with_hom.initialize_attributes()
    assert all(
        [
            0
            <= community_with_hom.influence_network.nodes[agent][cfg.agent_competence]
            <= 1
            for agent in community_with_hom.agents
        ]
    )
    assert all(
        0 <= community_with_hom.influence_network.edges[edge][cfg.edge_diversity] <= 1
        for edge in community_with_hom.influence_network.edges
    )
    # assert all(
    #     [
    #         -1
    #         <= community_with_hom.influence_network.edges[edge][cfg.edge_correlation]
    #         <= 1
    #         for edge in community_with_hom.influence_network.edges
    #     ]
    # )
    # nodes_type_elite = [
    #     node
    #     for node in community_with_hom.influence_network.agents()
    #     if community_with_hom.influence_network.nodes[node]["type"] == "elite"
    # ]
    # nodes_type_mass = [
    #     node
    #     for node in community_with_hom.influence_network.agents()
    #     if community_with_hom.influence_network.nodes[node]["type"] == "mass"
    # ]
    # assert set(community_with_hom.agents_elite) == set(nodes_type_elite)
    # assert set(community_with_hom.agents_mass) == set(nodes_type_mass)
    # elite_competence = community_with_hom.elite_competence
    # mass_competence = community_with_hom.mass_competence
    # assert all(
    #     [
    #         community_with_hom.influence_network.agents[node]["competence"]
    #         == elite_competence
    #         for node in nodes_type_elite
    #     ]
    # )
    # assert all(
    #     [
    #         community_with_hom.influence_network.agents[node]["competence"]
    #         == mass_competence
    #         for node in nodes_type_mass
    #     ]
    # )


def test_total_influence_elites():
    global community_from_edges
    assert community_from_edges.total_influence_elites() == (5 * 29)


def test_total_influence_mass():
    global community_from_edges
    assert community_from_edges.total_influence_mass() == (25 * 29)


def test_update_votes():
    global community_with_hom
    community_with_hom.update_votes()
    for agent in community_with_hom.agents:
        agent_vote = community_with_hom.influence_network.nodes[agent][cfg.agent_vote]
        agent_has_vote: bool = (
            agent_vote == cfg.vote_for_positive or agent_vote == cfg.vote_for_negative
        )
        assert agent_has_vote


def test_update_opinions():
    global community_with_hom
    community_with_hom.update_opinions()
    for node in community_with_hom.agents:
        node_opinion = community_with_hom.influence_network.nodes[node][
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
            community_simple_source.calculate_diversity(edge) == 0
            for edge in community_simple_source.influence_network.edges
        ]
    )

    community_simple_source.source_network.remove_edge(0, "s0")
    community_simple_source.source_network.remove_edge(1, "s1")
    assert all(
        [
            community_simple_source.calculate_diversity(edge) == 0.5
            for edge in community_simple_source.influence_network.edges
        ]
    )

    community_simple_source.source_network.remove_edge(0, "s2")
    community_simple_source.source_network.remove_edge(1, "s2")
    assert all(
        [
            community_simple_source.calculate_diversity(edge) == 1
            for edge in community_simple_source.influence_network.edges
        ]
    )


def test_best_group():
    global community_simple_source
    assert all(
        [
            agent in community_simple_source.agents
            for agent in community_simple_source.optimal_group(1)
        ]
    )
