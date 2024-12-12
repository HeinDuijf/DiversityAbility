from itertools import combinations

import numpy as np

import utils.config as cfg
from utils.basic_functions import calculate_competence


class Sources:
    def __init__(self, n_sources, reliability_distribution=("equi", (0.5, 0.7))):
        self.n_sources = n_sources
        self.sources = np.arange(n_sources, dtype=int)
        self.reliability_distribution = reliability_distribution
        self.reliabilities = self.initialize_reliabilities()
        self.valences = []
        self.update_valences()

    def initialize_reliabilities(self) -> np.array:
        if "equi" in self.reliability_distribution[0]:
            reliability_range = self.reliability_distribution[1]
            reliability_distance = reliability_range[1] - reliability_range[0]
            step = reliability_distance / (self.n_sources - 1)
            reliabilities = reliability_range[0] + step * np.arange(
                0, self.n_sources, dtype=int
            )
            return reliabilities

    def update_valences(self) -> None:
        random_list = np.random.rand(self.n_sources)
        valences = random_list < self.reliabilities

        def translation(x: bool) -> int:
            if x:
                return cfg.vote_for_positive
            else:
                return cfg.vote_for_negative

        self.valences = np.array(
            [translation(valences[k]) for k in range(len(valences))]
        )

    def set_valence(self, source, valence) -> None:
        self.valences[source] = valence

    def all_heuristics(self, heuristic_size: int):
        """Returns iterable"""
        return combinations(self.sources, heuristic_size)

    def problem_difficulty(self) -> float:
        return calculate_competence(self.reliabilities)
