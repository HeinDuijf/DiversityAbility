import concurrent.futures as cf
import copy
import os
import shutil
import time
from statistics import mean

import utils.config as cfg
from community import Community
from determine_teams import best_team, diverse_team, random_team
from utils.basic_functions import calculate_accuracy_and_precision, calculate_diversity
from utils.save_read_community import save_community_to_file


class Simulation:
    def __init__(
        self,
        number_of_communities: int,
        number_of_voting_simulations: int,
        folder_communities: str = None,
        filename_csv: str = None,
        number_of_agents: int = 100,
        influence_degree: int = 6,
        group_size=10,
        team_types=("best", "most_diverse", "random"),
        number_of_sources=10,
        source_degree=5,
        sources_reliability_distribution=(0.5, 0.7),
    ):
        self.start_time = time.time()
        time_str = time.strftime("%Y%m%d_%H%M%S")
        self.folder_communities = folder_communities
        if filename_csv is None:
            self.filename_csv = f"data/simulation_{time_str}.csv"
        self.number_of_communities = number_of_communities
        self.number_of_voting_simulations = number_of_voting_simulations
        self.number_of_agents = number_of_agents
        self.influence_degree = influence_degree

        self.group_size = group_size
        self.team_types = team_types
        self.number_of_sources = number_of_sources
        self.source_degree = source_degree
        self.sources_reliability_distribution = sources_reliability_distribution

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
        if self.folder_communities is not None:
            save_community_to_file(
                filename=f"{self.folder_communities}/communities/{number}",
                community=community,
            )
        self.simulate_and_write_data_line(community=community, number=number)
        self.report_progress(number)

    def initialize_dirs(self):
        if self.folder_communities is not None:
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
            f"number_of_agents, {self.number_of_agents}\n"
            f"group_size, {self.group_size}\n"
            f"number_of_sources, {self.number_of_sources}\n"
            f"source_degree, {self.source_degree}\n"
            f"sources_reliability_distribution, {self.sources_reliability_distribution}\n"
        )
        filename = self.filename_csv.replace(".csv", "")
        filename_readme = f"{filename}_README.csv"
        with open(filename_readme, "w") as f:
            f.write(information)

    def generate_community(self):
        # 1. Generate community with these parameters
        community = Community(
            number_of_agents=self.number_of_agents,
            number_of_sources=self.number_of_sources,
            influence_degree=self.influence_degree,
            source_degree=self.source_degree,
            sources_reliability_distribution=self.sources_reliability_distribution,
            edges=[],
        )
        return community

    def write_head_line(self):
        head_line = (
            "community_number,"
            + "group_size,"
            + "number_of_sources,"
            + "source_degree,"
            + "sources_reliability_distribution,"
            + "number_of_voting_simulations,"
            + "number_of_agents,"
            + "difficulty"
        )
        for team_type in self.team_types:
            head_line += (
                f",{team_type}_accuracy,{team_type}_precision"
                f",{team_type}_diversity,{team_type}_average"
            )
        with open(self.filename_csv, "w") as f:
            f.write(head_line)

    def simulate_and_write_data_line(self, community: Community, number: int):
        sources_reliability_distribution_str = str(
            self.sources_reliability_distribution
        ).replace(",", " to")
        data_line = (
            f"{number},{self.group_size},{self.number_of_sources},{self.source_degree},"
            f"{sources_reliability_distribution_str},{self.number_of_voting_simulations},"
            f"{self.number_of_agents},{community.problem_difficulty()}"
        )

        for team_type in self.team_types:
            team: Community = community

            if team_type == "best":
                team = best_team(community=community, group_size=self.group_size)
            if team_type == "most_diverse":
                team = diverse_team(community=community, group_size=self.group_size)
            if team_type == "random":
                team = random_team(community=community, group_size=self.group_size)

            accuracy, precision = team.estimated_community_accuracy(
                number_of_voting_simulations=self.number_of_voting_simulations
            )
            diversity: float = team.diversity(unrestricted=True)
            average: float = team.average_competence()
            data_line += f",{accuracy},{precision},{diversity},{average}"

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


def team_simulation(
    community: Community,
    group: list = None,
    number_of_voting_simulations: int = 10,
    alpha: float = 0.05,
):
    """Method for estimating the team accuracy of a group of agents in a community.
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
    # 1. Create community restricted to the group
    com = copy.deepcopy(community)
    if group is not None:
        com.remove_agents_from(
            [agent for agent in community.agents if agent not in group]
        )
    com.remove_influence_edges_from(com.influence_network.edges())

    # 2. Determine accuracy and diversity
    vote_outcomes = [com.vote() for _ in range(number_of_voting_simulations)]
    estimate = calculate_accuracy_and_precision(vote_outcomes, alpha=alpha)
    accuracy = estimate["accuracy"]
    precision = estimate["precision"]

    # diversity_edges = [
    #     com.influence_network.edges[edge][cfg.edge_diversity]
    #     for edge in com.influence_network.edges
    # ]
    # diversity = mean(diversity_edges)

    diversity_list = [
        calculate_diversity(com.source_network[agent1], com.source_network[agent2])
        for agent1 in com.agents
        for agent2 in com.agents
        if agent1 < agent2
    ]
    diversity = mean(diversity_list)

    average = mean([com.source_network[agent][cfg.agent_competence] for agent in group])
    result = {
        "accuracy": accuracy,
        "precision": precision,
        "diversity": diversity,
        "average": average,
    }
    return result
