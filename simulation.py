import concurrent.futures as cf
import copy
import os
import random as rd
import shutil
import time

import networkx as nx
import numpy as np

import scripts.config as cfg
from community import Community
from determine_groups import best_group, most_diverse_group, random_group
from scripts.basic_functions import (
    calculate_accuracy_and_precision,
    calculate_diversity,
)
from scripts.save_read_community import save_community_to_file


class Simulation:
    def __init__(
        self,
        number_of_communities: int,
        number_of_voting_simulations: int,
        folder_communities: str = None,
        filename_csv: str = None,
        number_of_agents: int = 100,
        degree: int = 6,
        probability_preferential_attachment: float = 0.6,
        elite_competence_range=(0.55, 0.7),
        mass_competence_range=(0.55, 0.7),
        number_of_elites_range=(25, 45),
        probability_homophilic_attachment_range=(0.5, 0.75),
    ):
        self.start_time = time.time()
        time_str = time.strftime("%Y%m%d_%H%M%S")
        if filename_csv is None:
            self.filename_csv = f"data/simulation_{time_str}.csv"
        if folder_communities is None:
            self.folder_communities = f"data/communities_{time_str}"
        self.number_of_communities = number_of_communities
        self.number_of_voting_simulations = number_of_voting_simulations
        self.number_of_agents = number_of_agents
        self.degree = degree
        self.probability_preferential_attachment = probability_preferential_attachment
        self.elite_competence_range = elite_competence_range
        self.mass_competence_range = mass_competence_range
        self.number_of_elites_range = number_of_elites_range
        self.probability_homophilic_attachment_range = (
            probability_homophilic_attachment_range
        )

    def run(self):
        print(f"Started simulation at {time.ctime()}")
        self.start_time = time.time()
        self.initialize_dirs()
        self.write_readme()
        self.write_head_line()
        with cf.ProcessPoolExecutor() as executor:
            executor.map(self.single_run, range(self.number_of_communities))
        print("The simulation is a great success.")

    def single_run(self, number: int):
        community = self.generate_community()
        save_community_to_file(
            filename=f"{self.folder_communities}/communities/{number}",
            community=community,
        )
        self.simulate_and_write_data_line(community=community, number=number)
        self.report_progress(number)

    def initialize_dirs(self):
        if os.path.exists(f"{self.folder_communities}"):
            shutil.rmtree(f"{self.folder_communities}")
        os.makedirs(f"{self.folder_communities}", exist_ok=True)
        if os.path.exists(f"{self.filename_csv}"):
            os.remove(f"{self.filename_csv}")

    def write_readme(self):
        information = (
            f"parameter, value\n"
            f"filename, {self.filename_csv}\n"
            f"folder, {self.folder_communities}\n"
            f"number_of_communities, {self.number_of_communities}\n"
            f"number_of_voting_simulations, {self.number_of_voting_simulations}\n"
            f"number_of_nodes, {self.number_of_agents}\n"
            f"degree, {self.degree}\n"
            f"probability_preferential_attachment"
            f", {self.probability_preferential_attachment}\n"
            f"elite_competence_range, {self.elite_competence_range}\n"
            f"mass_competence_range, {self.mass_competence_range}\n"
            f"number_of_elites_range, {self.number_of_elites_range}\n"
            f"probability_homophilic_attachment_range, "
            f"{self.probability_homophilic_attachment_range}"
        )
        filename_readme = f"{self.folder_communities}/README.csv"
        with open(filename_readme, "w") as f:
            f.write(information)

    def generate_community(self):
        probability_homophilic_attachment: float = rd.uniform(
            *self.probability_homophilic_attachment_range
        )
        number_of_elites: int = rd.randint(*self.number_of_elites_range)

        # 1. Generate community with these parameters
        community = Community(
            number_of_agents=self.number_of_agents,
            number_of_elites=number_of_elites,
            influence_degree=self.degree,
            probability_preferential_attachment=(
                self.probability_preferential_attachment
            ),
            probability_homophilic_attachment=probability_homophilic_attachment,
        )
        return community

    def write_head_line(self):
        head_line = (
            "community_number,"
            + "collective_accuracy,"
            + "collective_accuracy_precision,"
            + "minority_competence,"
            + "majority_competence,"
            + "number_of_minority,"
            + "influence_minority_proportion,"
            + "homophily"
        )
        with open(self.filename_csv, "w") as f:
            f.write(head_line)

    def simulate_and_write_data_line(self, community: Community, number: int):
        # Determine influence_minority_proportion
        total_influence_minority = community.total_influence_elites()
        total_influence_majority = community.total_influence_mass()
        influence_minority_proportion = total_influence_minority / (
            total_influence_minority + total_influence_majority
        )
        # Run voting simulations to estimate accuracy
        result = community.estimated_community_accuracy(
            self.number_of_voting_simulations
        )
        collective_accuracy = result["accuracy"]
        collective_accuracy_precision = result["precision"]

        # Print results to line in csv folder_communities
        data_line = (
            f"{number},{collective_accuracy},{collective_accuracy_precision},"
            f"{community.number_of_elites},{influence_minority_proportion},"
            f"{community.probability_homophilic_attachment}"
        )
        with open(self.filename_csv, "a") as f:
            f.write(f"\n{data_line}")

    def report_progress(self, community_number):
        stamps_percent = [1, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90]
        stamps_numbers = [
            (percent / 100) * self.number_of_communities for percent in stamps_percent
        ]
        if community_number in stamps_numbers:
            progress = int((community_number * 100) / self.number_of_communities)
            current_time_sec = time.time()
            elapsed_time_sec = current_time_sec - self.start_time
            estimated_total_time_sec = (elapsed_time_sec / progress) * 100
            estimated_finish_time_sec = self.start_time + estimated_total_time_sec
            estimated_finish_time_clock = time.ctime(estimated_finish_time_sec)
            print(
                f"Progress: {progress}%\n"
                f"Estimated finish time: {estimated_finish_time_clock}"
            )


class SimulationTeams(Simulation):
    def __init__(
        self,
        group_size=10,
        group_types=("best", "most_diverse", "random"),
        number_of_sources=10,
        source_degree=5,
        source_reliability_range=(0.5, 0.7),
        *args,
        **kwargs,
    ):
        super(SimulationTeams, self).__init__(*args, **kwargs)
        self.group_size = group_size
        self.group_types = group_types
        self.number_of_sources = number_of_sources
        self.source_degree = source_degree
        self.source_reliability_range = source_reliability_range

    def generate_community(self):
        # 1. Generate community with these parameters
        community = Community(
            number_of_agents=self.number_of_agents,
            number_of_sources=self.number_of_sources,
            source_degree=self.source_degree,
            sources_reliability_range=self.source_reliability_range,
            edges=[],
        )
        return community

    def write_readme(self):
        information = (
            f"parameter, value\n"
            f"filename, {self.filename_csv}\n"
            f"folder, {self.folder_communities}\n"
            f"number_of_communities, {self.number_of_communities}\n"
            f"number_of_voting_simulations, {self.number_of_voting_simulations}\n"
            f"number_of_agents, {self.number_of_agents}\n"
            f"group_size, {self.group_size}\n"
            f"number_of_sources, {self.number_of_sources}\n"
            f"source_degree, {self.source_degree}\n"
            f"source_reliability_range, {self.source_reliability_range}\n"
        )
        filename_readme = f"{self.folder_communities}/README.csv"
        with open(filename_readme, "w") as f:
            f.write(information)

    def write_head_line(self):
        head_line = (
            "community_number,"
            + "group_size,"
            + "number_of_sources,"
            + "source_degree,"
            + "source_reliability_range,"
            + "number_of_voting_simulations,"
            + "number_of_agents,"
            + "difficulty"
        )
        for group_type in self.group_types:
            head_line += (
                f",{group_type}_accuracy,{group_type}_accuracy_precision"
                f",{group_type}_diversity,{group_type}_average"
            )
        with open(self.filename_csv, "w") as f:
            f.write(head_line)

    def simulate_and_write_data_line(self, community: Community, number: int):
        source_reliability_range_str = str(self.source_reliability_range).replace(
            ",", " to"
        )
        data_line = (
            f"{number},{self.group_size},{self.number_of_sources},{self.source_degree},"
            f"{source_reliability_range_str},{self.number_of_voting_simulations},"
            f"{self.number_of_agents},{community.problem_difficulty()}"
        )
        for group_type in self.group_types:
            group_params = {
                "number_of_voting_simulations": self.number_of_voting_simulations,
            }
            group = []
            community_new = copy.deepcopy(community)
            if group_type == "best":
                best_result = best_group(
                    community=community, group_size=self.group_size
                )
                group = best_result["group"]
                community_new.set_source_network(best_result["source_network"])
            if group_type == "most_diverse":
                diverse_result = most_diverse_group(
                    community=community, group_size=self.group_size
                )
                group = diverse_result["group"]
                community_new.set_source_network(diverse_result["source_network"])
            if group_type == "random":
                random_result = random_group(
                    community=community, group_size=self.group_size
                )
                group = random_result["group"]
                community_new.set_source_network(random_result["source_network"])
            # if group_type == "optimal":
            #     group = community.best_group(group_size=self.group_size)
            # if group_type == "diverse":
            #     group = community.diverse_group(
            #         group_size=self.group_size
            #     )

            group_params["group"] = group
            group_params["community"] = community

            result = group_simulations(**group_params)
            accuracy = result["accuracy"]
            accuracy_precision = result["precision"]
            diversity = result["diversity"]
            average = result["average"]
            data_line += f",{accuracy},{accuracy_precision},{diversity},{average}"

        with open(self.filename_csv, "a") as f:
            f.write(f"\n{data_line}")


def group_simulations(
    community: Community,
    group: list,
    number_of_voting_simulations: int = 10,
    alpha: float = 0.05,
    # communication: str = "unrestricted",
    # edges=None,
    # source_edges=None,
):
    """ Method for estimating the group accuracy of a group of agents in a community.
    :param community: Community
        Community
    :param group
        List of agents
    :param number_of_voting_simulations: int
        Number of voting simulations
    :param alpha
        p-value for confidence interval.
    :returns result: dict
        result["accuracy"]: estimated group accuracy,
        result["precision"]: the confidence interval associated with p-value alpha
        result["diversity"]: group diversity
    """
    # 1. Create dummy community
    net = nx.create_empty_copy(community.influence_network)
    net.remove_nodes_from([agent for agent in community.agents if agent not in group])
    net.add_edges_from(nx.DiGraph(nx.complete_graph(group)).edges)

    source_net = community.source_network.copy()
    source_net.remove_nodes_from(
        [agent for agent in community.agents if agent not in group]
    )
    sources = community.sources

    dummy_com = Community(
        number_of_agents=0, number_of_sources=0, edges=[], source_edges=[],
    )
    dummy_com.add_agents_from(group)
    dummy_com.add_sources_from(sources)
    dummy_com.influence_network = net
    dummy_com.source_network = source_net
    dummy_com.initialize_attributes()

    # 2. Determine accuracy and diversity
    vote_outcomes = [dummy_com.vote() for _ in range(number_of_voting_simulations)]
    estimate = calculate_accuracy_and_precision(vote_outcomes, alpha=alpha)
    accuracy = estimate["accuracy"]
    precision = estimate["precision"]

    diversity_edges = [
        dummy_com.influence_network.edges[edge][cfg.edge_diversity]
        # dummy_com.calculate_diversity(edge=edge)
        for edge in dummy_com.influence_network.edges
    ]
    diversity = np.mean(diversity_edges)

    average = np.mean([dummy_com.calculate_competence(agent) for agent in group])
    result = {
        "accuracy": accuracy,
        "precision": precision,
        "diversity": diversity,
        "average": average,
    }
    return result


if __name__ == "__main__":
    params = {
        "group_types": ["best", "most_diverse", "random"],
        "source_reliability_range": (0.5, 0.7),
        "number_of_agents": 20,
        "number_of_communities": 1000,
        "number_of_voting_simulations": 1000,
        "source_degree": 5,
    }
    group_sizes = [5, 11, 21]
    sources_range = [11, 21, 31]
    for number_of_sources in sources_range:
        for group_size in group_sizes:
            SimulationTeams(
                group_size=group_size, number_of_sources=number_of_sources, **params,
            ).run()
            print(f"Number of source: {number_of_sources}")
            print(f"Group size: {group_size}")
