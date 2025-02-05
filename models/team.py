import numpy as np

import utils.config as cfg
from models.agent import Agent
from models.sources import Sources
from utils.basic_functions import (
    calculate_accuracy_precision_proportion,
    calculate_competence,
    calculate_competence_with_duplicates,
    calculate_diversity,
    majority_winner,
    powerset,
)


class Team:
    """
    A class representing a team.

    Attributes
    ----------
        members (list[Agent]):
            A list containing the members of the team.
        sources (Sources):
            The sources that the team could access.
        size (int):
            The size of the team.

    Methods
    -------
        accuracy:
            Returns the accuracy for the opinion-based dynamics.
        pool_accuracy:
            Returns the accuracy for the evidence-based dynamics.
        bounded_pool_accuracy:
            Returns the accuracy for the boundedly rational evidence-based dynamics.
    """

    def __init__(self, members: list[Agent], sources: Sources):
        self.members = members
        self.sources = sources
        self.size = len(self.members)

    def aggregate(self):
        return majority_winner([agent.opinion for agent in self.members])

    def update_opinions(self) -> None:
        for agent in self.members:
            agent.update_opinion()

    def pool_accuracy(self):
        sources_accessed = np.unique(
            np.array([agent.heuristic for agent in self.members]).flatten()
        )
        reliabilities = self.sources.reliabilities[sources_accessed]
        return calculate_competence(reliabilities)

    def bounded_pool_accuracy(self):
        sources_accessed = np.array(
            [agent.heuristic for agent in self.members]
        ).flatten()
        sources_accessed, weights = np.unique(sources_accessed, return_counts=True)
        reliabilities = self.sources.reliabilities[sources_accessed]
        return calculate_competence_with_duplicates(reliabilities, weights)

    def accuracy(self, estimate_sample_size: int = None) -> tuple:
        # 1. Estimate by sampling if estimate_sample_size is integer
        if isinstance(estimate_sample_size, int):
            outcomes = np.array([], dtype=float)
            for _ in range(estimate_sample_size):
                self.sources.update_valences()
                self.update_opinions()
                result = self.aggregate()
                outcomes = np.append(outcomes, result)
            estimated_accuracy, precision = calculate_accuracy_precision_proportion(
                outcomes
            )
            return estimated_accuracy, precision

        # 2. Else calculate
        heuristics = np.array([agent.heuristic for agent in self.members])
        sources_relevant = np.unique(heuristics.flatten())

        accuracy = 0
        for sources_positive in powerset(sources_relevant):
            for source in self.sources.sources:
                if source in sources_positive:
                    self.sources.set_valence(source, cfg.vote_for_positive)
                else:
                    self.sources.set_valence(source, cfg.vote_for_negative)

            self.update_opinions()
            team_decision = majority_winner(
                [agent.opinion for agent in self.members], return_value=False
            )

            if len(team_decision) == 1 and cfg.vote_for_positive in team_decision:
                probabilities_list = [
                    self.sources.reliabilities[source] for source in sources_positive
                ] + [
                    1 - self.sources.reliabilities[source]
                    for source in sources_relevant
                    if source not in sources_positive
                ]
                probability_subset = np.prod(probabilities_list)
                accuracy += probability_subset
            elif len(team_decision) == 2:
                probabilities_list = [
                    self.sources.reliabilities[source] for source in sources_positive
                ] + [
                    1 - self.sources.reliabilities[source]
                    for source in sources_relevant
                    if source not in sources_positive
                ]
                probability_subset = np.prod(probabilities_list)
                accuracy += probability_subset / 2
        return accuracy, None

    def average(self) -> float:
        return np.mean([agent.competence() for agent in self.members])

    def diversity(self) -> float:
        diversity_scores = [
            calculate_diversity(agent1.heuristic, agent2.heuristic)
            for agent1 in self.members
            for agent2 in self.members
            if agent1 != agent2
        ]
        return sum(diversity_scores) / (self.size * (self.size - 1))

    def problem_difficulty(self) -> float:
        return self.sources.problem_difficulty()
