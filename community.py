import math
import random as rd

import networkx as nx
import numpy as np

from scripts import config as cfg
from scripts.basic_functions import majority_winner


class Community:
    def __init__(
        self,
        number_of_agents: int = 100,
        number_of_sources: int = 100,
        sources_reliability_range=(0.5, 0.7),
        # Todo: set probability distribution of sources: string or (string, (params))
        # For example "norm" and ("norm", (mean, std)) and "uni" and ("uni", (min, max))
        source_degree: int = 5,
        influence_degree: int = 6,
        number_of_elites: int = 40,
        probability_preferential_attachment: float = 0.6,
        probability_homophilic_attachment: float = None,
        edges: list = None,
        source_edges: list = None,
    ):
        self.number_of_agents: int = number_of_agents
        self.number_of_sources: int = number_of_sources
        self.sources_reliability_range = sources_reliability_range
        self.source_degree: int = source_degree
        self.influence_degree: int = influence_degree
        self.number_of_elites: int = number_of_elites
        self.number_of_mass: int = number_of_agents - number_of_elites
        # self.elite_competence: float = elite_competence
        # self.mass_competence: float = mass_competence
        self.probability_preferential_attachment: float = (
            probability_preferential_attachment
        )
        self.probability_homophilic_attachment: float = (
            probability_homophilic_attachment
        )
        self.edges: list = edges
        self.source_edges: list = source_edges

        self.agents: list = list(range(number_of_agents))
        self.sources: list = [f"s{k}" for k in range(self.number_of_sources)]
        self.agents_elite: list = self.agents[: self.number_of_elites]
        self.agents_mass: list = self.agents[-self.number_of_mass :]

        # The central methods
        self.source_network = self.create_source_network()
        self.influence_network = self.create_influence_network()

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
            return self.source_network

        # Add random edges
        for agent in self.agents:
            sources = rd.sample(self.sources, self.source_degree)
            edges_from_agent = [(agent, source) for source in sources]
            source_network.add_edges_from(edges_from_agent)
        self.source_network = source_network
        self.initialize_source_attributes()
        return self.source_network

    def initialize_source_attributes(self):
        # Todo: include other ways to set source reliability
        for source in self.sources:
            self.source_network.nodes[source][cfg.source_reliability] = rd.uniform(
                self.sources_reliability_range[0], self.sources_reliability_range[1]
            )

    def create_influence_network(self):
        """Returns a directed influence_network according to multi-type preferential
        attachment by amending the Barabási-Albert preferential attachment procedure,
        unless edges are given."""
        if self.edges is not None:
            self.influence_network = self.create_network_from_edges()
            self.initialize_attributes()
            return self.influence_network

        # Create initial influence_network.
        if self.probability_homophilic_attachment is None:
            # Create influence_network without homophilic influence
            initial_network = (
                self.create_initial_network_without_homophilic_attachment()
            )
        else:
            initial_network = self.create_initial_network_with_homophilic_attachment()

        # Preferential rewiring.
        self.influence_network = self.rewire_network(initial_network)
        self.initialize_attributes()
        return self.influence_network

    def create_network_from_edges(self):
        network = nx.DiGraph()
        network.add_nodes_from(self.agents)
        network.add_edges_from(self.edges)
        return network

    def create_initial_network_without_homophilic_attachment(self):
        # Initialize influence_network and agents
        initial_network = nx.DiGraph()
        initial_network.add_nodes_from(self.agents)
        # Add random edges
        for node in self.agents:
            potential_targets = self.agents.copy()
            potential_targets.remove(node)
            targets = rd.sample(potential_targets, self.influence_degree)
            edges_from_node = [(node, target) for target in targets]
            initial_network.add_edges_from(edges_from_node)
        return initial_network

    def create_initial_network_with_homophilic_attachment(self):
        # Initialize influence_network and agents
        initial_network = nx.DiGraph()
        initial_network.add_nodes_from(self.agents)

        # Homophilic attachment
        for node in self.agents:
            random_list = np.random.random_sample(self.influence_degree)
            number_targets_same_type = len(
                [x for x in random_list if x < self.probability_homophilic_attachment]
            )
            number_targets_diff_type = self.influence_degree - number_targets_same_type
            if node in self.agents_elite:
                nodes_same_type = self.agents_elite.copy()
                nodes_same_type.remove(node)
                nodes_diff_type = self.agents_mass
            else:
                nodes_same_type = self.agents_mass.copy()
                nodes_same_type.remove(node)
                nodes_diff_type = self.agents_elite
            targets_same_type = rd.sample(nodes_same_type, number_targets_same_type)
            targets_diff_type = rd.sample(nodes_diff_type, number_targets_diff_type)
            targets = targets_same_type + targets_diff_type
            edges_from_source = [(node, target) for target in targets]
            initial_network.add_edges_from(edges_from_source)
        return initial_network

    def rewire_network(self, initial_network):
        # Initialize influence_network and agents
        network = nx.DiGraph()
        network.add_nodes_from(self.agents)

        # Multi-type preferential attachment
        edges_to_do = list(initial_network.edges()).copy()
        rd.shuffle(edges_to_do)
        for (source, target) in edges_to_do:
            # Define potential targets
            if target in self.agents_elite:
                nodes_of_target_type = self.agents_elite
            else:
                nodes_of_target_type = self.agents_mass
            potential_targets = [
                node
                for node in nodes_of_target_type
                if node not in network[source] and node != source
            ]

            if rd.random() < self.probability_preferential_attachment:
                # Preferential attachment
                list_of_tuples = list(
                    network.in_degree(potential_targets)
                )  # list of tuples of the form (node, in_degree of node)
                potential_targets_in_degrees = list(
                    map(lambda tuple_item: tuple_item[1], list_of_tuples)
                )
                if not potential_targets:
                    break
                elif all(w == 0 for w in potential_targets_in_degrees):
                    # catches the case where all weights are zero
                    target_new = rd.choice(potential_targets)
                else:
                    target_new = rd.choices(
                        population=potential_targets,
                        weights=potential_targets_in_degrees,
                    )[0]
                    # Note on [0]: rd.choices produces a list
            else:
                # Random attachment
                target_new = rd.choice(potential_targets)
            # add edge to new influence_network and remove edge from edges_to_do
            network.add_edge(source, target_new)
        return network

    def initialize_attributes(self):
        for agent in self.agents:
            self.influence_network.nodes[agent][
                cfg.agent_competence
            ] = self.calculate_competence(agent)
        for edge in self.influence_network.edges:
            self.influence_network.edges[edge][
                cfg.edge_diversity
            ] = self.calculate_diversity(edge)
            # self.influence_network.edges[edge][
            #     cfg.edge_correlation
            # ] = self.calculate_correlation(edge)

    def calculate_diversity(self, edge):
        agent1 = edge[0]
        agent2 = edge[1]
        sources_agent1 = self.source_network[agent1]
        sources_agent2 = self.source_network[agent2]
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

    def calculate_correlation(self, edge):
        # Todo: fix and test correlation function and use it to set edge attribute
        #  in the source network.
        # Todo: measure diversity: Can we use correlation for this?
        probability_11 = 0
        probability_00 = 0
        probability_10 = 0
        probability_01 = 0
        agent1 = edge[0]
        agent2 = edge[1]
        sources_agent1 = self.source_network[agent1]
        sources_agent2 = self.source_network[agent2]
        sources = sorted(set(sources_agent1).union(set(sources_agent2)))
        number_of_sources = len(sources)

        powerset = (
            list(bin(number)[2:].zfill(number_of_sources))
            for number in range(2 ** number_of_sources)
        )
        for subset in powerset:
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
            agent1_opinion = majority_winner(
                [
                    subset[k]
                    for k in range(number_of_sources)
                    if sources[k] in sources_agent1
                ]
            )
            agent2_opinion = majority_winner(
                [
                    subset[k]
                    for k in range(number_of_sources)
                    if sources[k] in sources_agent2
                ]
            )
            if agent1_opinion == "1" and agent2_opinion == "1":
                probability_11 += probability_subset
            elif agent1_opinion == "1" and agent2_opinion == "0":
                probability_10 += probability_subset
            elif agent1_opinion == "0" and agent2_opinion == "1":
                probability_01 += probability_subset
            elif agent1_opinion == "0" and agent2_opinion == "0":
                probability_00 += probability_subset

        accuracy_agent1 = probability_11 + probability_10
        accuracy_agent2 = probability_11 + probability_01
        assert accuracy_agent1 < 1
        assert probability_10 != 0
        assert accuracy_agent2 < 1
        assert probability_11 != 0

        correlation = (
            probability_11 * probability_00 - probability_10 * probability_01
        ) / (
            math.sqrt(
                accuracy_agent1
                * (1 - accuracy_agent1)
                * accuracy_agent2
                * (1 - accuracy_agent2)
            )
        )
        return correlation

    def total_influence_elites(self):  # Todo: remove?
        edges_to_elites = [
            (source, target)
            for (source, target) in self.influence_network.edges()
            if target in self.agents_elite
        ]
        return len(edges_to_elites)

    def total_influence_mass(self):  # Todo: Remove?
        return len(self.influence_network.edges()) - self.total_influence_elites()

    def best_group(self, group_size):
        agent_tuples = [
            [agent, self.influence_network.nodes[agent][cfg.agent_competence]]
            for agent in self.agents
        ]
        agent_tuples.sort(key=lambda item: item[1], reverse=True)
        best_group = [agent for [agent, competence] in agent_tuples[:group_size]]
        return best_group

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
