import numpy as np

import utils.config as cfg
from models.sources import Sources
from utils.basic_functions import (
    calculate_accuracy_precision_proportion,
    calculate_diversity,
    majority_winner,
    powerset,
)


class Team:
    def __init__(self, members, sources: Sources):
        self.members = members
        self.sources = sources
        self.size = len(self.members)

    def aggregate(self):
        return majority_winner([agent.opinion for agent in self.members])

    def update_opinions(self) -> None:
        for agent in self.members:
            agent.update_opinion()

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
            team_decision = self.aggregate()
            if team_decision == cfg.vote_for_positive:
                probabilities_list = [
                    self.sources.reliabilities[source] for source in sources_positive
                ] + [
                    1 - self.sources.reliabilities[source]
                    for source in sources_relevant
                    if source not in sources_positive
                ]
                probability_subset = np.prod(probabilities_list)
                accuracy += probability_subset
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
