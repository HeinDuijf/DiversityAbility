import random as rd

from statsmodels.stats.proportion import proportion_confint

import scripts.config as cfg


def majority_winner(values: list):
    """ Basic function to determine the majority winner in a binary decision context."""
    options = sorted(set(values))
    threshold = len(values) / 2
    for option in options:
        if values.count(option) > threshold:
            return option
    return rd.choice(options)


def calculate_accuracy_and_precision(list_of_items, alpha: float = 0.05):
    number_of_items = len(list_of_items)
    number_of_success = len(
        [outcome for outcome in list_of_items if outcome == cfg.vote_for_positive]
    )
    estimated_accuracy = number_of_success / number_of_items
    confidence_interval = proportion_confint(
        number_of_success, number_of_items, alpha=alpha
    )
    result = {
        "accuracy": estimated_accuracy,
        "precision": max(confidence_interval) - min(confidence_interval),
    }
    return result


def convert_math_to_text(string: str):
    """ Converts math to text.
    For example, "p_e" is converted to "minority_competence"."""
    words = string.replace("+", " ").split(" ")
    words = [word for word in words if word != ""]
    convert: dict = {
        "p_e": "minority_competence",
        "p_m": "majority_competence",
        "E": "number_of_minority",
        "I_e": "influence_minority_proportion",
        "h": "homophily",
    }
    if len(words) == 1:
        return convert[words[0]]
    return [convert[word] for word in words]
