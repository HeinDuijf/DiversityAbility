from models.sources import Sources
from utils.basic_functions import calculate_competence, majority_winner


class Agent:
    def __init__(self, no, heuristic, sources: Sources):
        self.no = no
        self.heuristic = heuristic
        self.sources = sources
        self.score = self.competence()
        self.opinion = self.update_opinion()

    def update_opinion(self):
        self.opinion = majority_winner(
            [self.sources.valences[source] for source in self.heuristic]
        )

    def competence(self):
        return calculate_competence(
            [self.sources.reliabilities[source] for source in self.heuristic]
        )
