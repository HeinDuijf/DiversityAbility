import random as rd

import networkx as nx
import numpy as np

from utils import config as cfg
from utils.basic_functions import calculate_accuracy_and_precision, majority_winner

# from icecream import ic


class Community:
    def __init__(
        self,
        number_of_agents: int = 100,
        number_of_sources: int = 100,
        sources_reliability_range=(0.5, 0.7),
        # Todo: set probability distribution of sources: string or (string, (params))
        # For example "norm" and ("norm", (mean, std)) and "uni" and ("uni", (min, max))
        source_degree: int = 5,
        # Todo: set influence types (string, *params)
        influence=("all"),  # ("rd", 6), ("pref", 0.6), ("hom", 0.7), ("prefhom",
        # 0.6, 0.7
        influence_degree: int = 1,
        edges: list = None,
        source_edges: list = None,
        create: bool = True,
    ):
        self.number_of_agents: int = number_of_agents
        self.number_of_sources: int = number_of_sources
        self.sources_reliability_range = sources_reliability_range
        self.source_degree: int = source_degree
        self.influence_degree: int = influence_degree

        self.edges: list = edges
        self.source_edges: list = source_edges

        self.agents: list = list(range(number_of_agents))
        self.sources: list = [f"s{k}" for k in range(self.number_of_sources)]

        # Initialize networks
        self.source_network = nx.DiGraph()
        self.influence_network = nx.DiGraph()

        # The central methods
        if create:
            self.create_source_network()
            self.create_influence_network()

    def create_source_network(self):
        """Returns a random directed source_network with two types of nodes: agents
        and sources. The source_network only contains edges from agents to sources."""
        # Initialize influence_network and agents
        source_network = nx.DiGraph()
        source_network.add_nodes_from(self.agents)
        source_network.add_nodes_from(self.sources)

        if self.source_edges is not None:
            source_network.add_edges_from(self.source_edges)
            self.source_network = source_network
            self.initialize_source_attributes()
            return

        # Add random edges
        for agent in self.agents:
            sources = rd.sample(self.sources, self.source_degree)
            edges_from_agent = [(agent, source) for source in sources]
            source_network.add_edges_from(edges_from_agent)
        self.source_network = source_network
        self.initialize_source_attributes()

    def set_source_network(self, source_network):
        agents = self.agents
        new_agents = [agent for agent in agents if agent not in source_network.nodes()]
        self.sources = list(
            [node for node in source_network.nodes() if isinstance(node, str)]
        )
        self.add_agents_from(new_agents)
        self.source_network = source_network
        for edge in self.influence_network.edges:
            self.initialize_diversity(edge)

    def initialize_source_attributes(self):
        for source in self.sources:
            self.initialize_source_reliability(source)

    def initialize_source_reliability(self, source: str, reliability: float = None):
        # Todo: include other ways to set source reliability
        if reliability is None:
            reliability = rd.uniform(
                self.sources_reliability_range[0], self.sources_reliability_range[1]
            )
        self.source_network.nodes[source][cfg.source_reliability] = reliability

    def create_influence_network(self):
        """Creates the influence network, which is a directed network on the agents.
        The creation method is random unless edges are given."""
        if self.edges is not None:
            self.create_influence_network_from_edges()
            self.initialize_attributes()
            return

        self.create_random_influence_network()
        self.initialize_attributes()

    def create_influence_network_from_edges(self):
        self.influence_network = nx.DiGraph()
        self.influence_network.add_nodes_from(self.agents)
        self.influence_network.add_edges_from(self.edges)

    def create_random_influence_network(self):
        # Initialize influence_network and agents
        net = nx.DiGraph()
        net.add_nodes_from(self.agents)
        # Add random edges
        for agent in self.agents:
            potential_targets = self.agents.copy()
            potential_targets.remove(agent)
            targets = rd.sample(potential_targets, self.influence_degree)
            edges_from_node = [(agent, target) for target in targets]
            net.add_edges_from(edges_from_node)
        return net

    def initialize_attributes(self):
        for agent in self.agents:
            self.initialize_competence(agent)
        for edge in self.influence_network.edges:
            self.initialize_diversity(edge)

    def initialize_competence(self, agent):
        self.influence_network.nodes[agent][
            cfg.agent_competence
        ] = self.calculate_competence(agent=agent)

    def initialize_diversity(self, edge):
        self.influence_network.edges[edge][
            cfg.edge_diversity
        ] = self.calculate_diversity(edge)

    def calculate_diversity(self, edge):
        agent1 = edge[0]
        agent2 = edge[1]
        sources_agent1 = self.source_network[agent1]
        sources_agent2 = self.source_network[agent2]
        if len(sources_agent1) == 0:
            return 0
        novel_sources_agent1 = [
            source for source in sources_agent1 if source not in sources_agent2
        ]
        diversity = len(novel_sources_agent1) / len(sources_agent1)
        return diversity

    def calculate_competence(self, agent=None, sources=None):
        competence: float = 0
        if agent is not None:
            sources = list(self.source_network[agent])
        number_of_sources = len(sources)
        threshold = number_of_sources / 2
        powerset = (
            list(bin(number)[2:].zfill(number_of_sources))
            for number in range(2 ** number_of_sources)
        )
        for subset in powerset:
            if not subset.count("1") < threshold:
                probabilities_list = [
                    self.source_network.nodes[sources[k]][cfg.source_reliability]
                    for k in range(number_of_sources)
                    if subset[k] == "1"
                ] + [
                    1 - self.source_network.nodes[sources[k]][cfg.source_reliability]
                    for k in range(number_of_sources)
                    if subset[k] == "0"
                ]
                probability_subset = np.prod(probabilities_list)
                if subset.count("1") > threshold:
                    competence += probability_subset
                elif subset.count("1") == 0.5:
                    competence += probability_subset / 2
        return competence

    def optimal_group(self, group_size):
        agent_tuples = [
            [agent, self.influence_network.nodes[agent][cfg.agent_competence]]
            for agent in self.agents
        ]
        agent_tuples.sort(key=lambda item: item[1], reverse=True)
        optimal_group = [agent for [agent, competence] in agent_tuples[:group_size]]
        return optimal_group

    def random_group(self, group_size):
        return rd.sample(self.agents, group_size)

    def diverse_group(self, group_size):
        diverse_group = []
        agents_sources: dict = {
            agent: self.source_network[agent] for agent in self.agents
        }
        agents_diversity: dict = {
            agent: len(agents_sources[agent]) for agent in self.agents
        }
        for _ in range(group_size):
            max_diversity = max(agents_diversity.values())
            max_diverse_agents = [
                agent
                for agent in self.agents
                if agents_diversity[agent] == max_diversity
            ]
            new_agent = rd.choice(max_diverse_agents)
            new_agent_sources = agents_sources[new_agent]
            diverse_group.append(new_agent)
            for agent in self.agents:
                agents_sources[agent] = list(
                    set(agents_sources[agent]).difference(set(new_agent_sources))
                )
                agents_diversity[agent] = len(agents_sources[agent])
        return diverse_group

    def problem_difficulty(self):
        return self.calculate_competence(sources=self.sources)

    def estimated_community_accuracy(
        self, number_of_voting_simulations: int, alpha: float = 0.05
    ):
        """ Method for estimating the collective accuracy of the community.
        :param number_of_voting_simulations: int
            Number of simulations to estimate the collective accuracy
        :param alpha: float
            p-value for confidence interval.
        :returns result: dict
            result["accuracy"]: estimated collective accuracy,
            result["precision"]: the confidence interval associated with p-value
            alpha
        """
        vote_outcomes = [self.vote() for _ in range(number_of_voting_simulations)]
        result = calculate_accuracy_and_precision(vote_outcomes, alpha=alpha)
        return result

    def vote(self):
        self.update_votes()
        list_of_votes = [
            self.influence_network.nodes[agent][cfg.agent_vote] for agent in self.agents
        ]
        return majority_winner(list_of_votes)

    def update_votes(self):
        # Todo: note that agents share their opinion, not their underlying sources.
        #  Think about whether we should implement another mechanism where agents
        #  share their sources instead.
        self.update_opinions()
        for agent in self.agents:
            neighborhood = list(self.influence_network[agent]) + [agent]
            neighborhood_opinions = [
                self.influence_network.nodes[neighbor_agent][cfg.agent_opinion]
                for neighbor_agent in neighborhood
            ]
            self.influence_network.nodes[agent][cfg.agent_vote] = majority_winner(
                neighborhood_opinions
            )

    def update_opinions(self):
        for source in self.sources:
            if rd.random() < self.source_network.nodes[source][cfg.source_reliability]:
                self.source_network.nodes[source][
                    cfg.source_valence
                ] = cfg.vote_for_positive
            else:
                self.source_network.nodes[source][
                    cfg.source_valence
                ] = cfg.vote_for_negative

        for agent in self.agents:
            source_valences = [
                self.source_network.nodes[source][cfg.source_valence]
                for source in self.source_network[agent]
            ]
            self.influence_network.nodes[agent][cfg.agent_opinion] = majority_winner(
                source_valences
            )

    def add_agents_from(self, new_agents: list):
        if not isinstance(new_agents, list):
            new_agents = [new_agents]
        self.agents += new_agents
        self.number_of_agents = len(self.agents)
        self.influence_network.add_nodes_from(new_agents)
        self.source_network.add_nodes_from(new_agents)
        for agent in new_agents:
            self.influence_network.nodes[agent][cfg.agent_competence] = 0

    def remove_agents_from(self, remove_agents: list):
        if not isinstance(remove_agents, list):
            remove_agents = [remove_agents]
        self.agents = [agent for agent in self.agents if agent not in remove_agents]
        self.number_of_agents = len(self.agents)
        self.influence_network.remove_nodes_from(remove_agents)
        self.source_network.remove_nodes_from(remove_agents)

    def add_sources_from(
        self, new_sources: list, new_source_reliabilities: list = None
    ):
        if not isinstance(new_sources, list):
            new_sources = [new_sources]
        if new_source_reliabilities is None:
            new_source_reliabilities = [None for _ in new_sources]
        self.sources += new_sources
        self.number_of_sources = self.number_of_sources + len(new_sources)
        self.source_network.add_nodes_from(new_sources)
        for k, new_source in enumerate(new_sources):
            reliability = new_source_reliabilities[k]
            self.initialize_source_reliability(new_source, reliability)

    def remove_sources_from(self, sources_remove):
        if not isinstance(sources_remove, list):
            sources_remove = [sources_remove]
        agents_affected = [
            agent
            for source in sources_remove
            for agent in self.source_network.in_edges[source]
        ]
        self.sources = [
            source for source in self.sources if source not in sources_remove
        ]
        self.number_of_sources = len(self.sources)
        self.source_network.remove_nodes_from(sources_remove)
        for agent in agents_affected:
            self.initialize_competence(agent)
            for target in self.influence_network[agent]:
                self.initialize_diversity((agent, target))

    def add_source_edges_from(self, new_source_edges: list):
        new_sources = [source for agent, source in new_source_edges]
        new_agents = [agent for agent, source in new_source_edges]
        self.add_sources_from(new_sources)
        self.add_agents_from(new_agents)
        self.source_network.add_edges_from(new_source_edges)
        for agent in new_agents:
            self.initialize_competence(agent)
        for edge in new_source_edges:
            self.initialize_diversity(edge)

    def add_influence_edges_from(self, new_edges: list):
        self.influence_network.add_edges_from(new_edges)
        for edge in new_edges:
            self.initialize_diversity(edge)
