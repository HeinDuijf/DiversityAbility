from models.sources import Sources
from utils.basic_functions import calculate_competence, majority_winner


class Agent:
    """
    A class representing an agent.

    Attributes
    ----------
        heuristic:
            The agent’s heuristic, which is represented by the set of sources she has
            access to.
        sources (Sources):
            The sources that the agent could access.
        score:
            The agent’s score.
    """

    def __init__(self, no, heuristic, sources: Sources):
        self.no = no
        self.heuristic = heuristic
        self.sources = sources
        self.score = self.competence()
        self.update_opinion()

    def update_opinion(self) -> None:
        self.opinion = majority_winner(
            [self.sources.valences[source] for source in self.heuristic]
        )

    def competence(self) -> float:
        return calculate_competence(
            [
                self.sources.reliabilities[source] for source in self.heuristic
            ]  # type: ignore
        )
