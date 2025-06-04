import itertools as it
import random as rd

import numpy as np
from statsmodels.stats.proportion import proportion_confint

import utils.config as cfg


def majority_winner(values: list, return_value: bool = True):
    """Basic function to determine the majority winner in a binary decision context.
    Returns a single value when return_value is True, otherwise a list of value(s).
    """
    options = sorted(set(values))
    threshold = len(values) / 2
    for option in options:
        if values.count(option) > threshold:
            if return_value:
                return option
            return [option]
    if return_value:
        return rd.choice(options)
    return options


def powerset(iterable: np.ndarray) -> it.chain:
    """Copied from http://docs.python.org/2.7/library/itertools.html#recipes
    powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"""
    s = np.array(iterable)
    return it.chain.from_iterable(it.combinations(s, r) for r in range(len(s) + 1))


def calculate_accuracy_precision_proportion(
    list_of_items: list | np.ndarray, alpha: float = 0.05
) -> tuple:
    """Basic function to calculate the accuracy and precision of a list of items.
    :param list_of_items
        a list of items of successes and failures
    :param alpha
        p-value for confidence interval
    :returns tuple
        accuracy, precision, proportion
    """
    number_of_items = len(list_of_items)
    number_of_success = 0
    if isinstance(list_of_items, list):
        number_of_success = list_of_items.count(cfg.vote_for_positive)
    if isinstance(list_of_items, np.ndarray):
        number_of_success = np.count_nonzero(list_of_items == cfg.vote_for_positive)
    accuracy = number_of_success / number_of_items
    confidence_interval_low, confidence_interval_high = proportion_confint(
        number_of_success, number_of_items, alpha=alpha
    )
    precision = confidence_interval_high - confidence_interval_low
    return accuracy, precision


def calculate_diversity(list1: list, list2: list) -> float:
    novel_items1 = [item for item in list1 if item not in list2]
    novelty1 = len(novel_items1) / len(list1)
    novel_items2 = [item for item in list2 if item not in list1]
    novelty2 = len(novel_items2) / len(list2)
    diversity = (novelty1 + novelty2) / 2
    return diversity


def calculate_competence(reliabilities: list | np.ndarray) -> float:
    competence: float = 0
    number_of_sources = len(reliabilities)
    sources = np.array(range(len(reliabilities)))
    if number_of_sources == 0:
        return 0
    threshold = number_of_sources / 2

    for sources_positive in powerset(sources):
        if len(sources_positive) >= threshold:
            probabilities_list = [
                reliabilities[source] for source in sources_positive
            ] + [
                1 - reliabilities[source]
                for source in sources
                if source not in sources_positive
            ]
            probability_subset: float = float(np.prod(probabilities_list))
            if len(sources_positive) > threshold:
                competence += probability_subset
            elif len(sources_positive) == threshold:
                competence += probability_subset / 2
    return competence


def calculate_competence_with_duplicates(
    reliabilities: list | np.ndarray, weights: list | np.ndarray | None = None
) -> float:
    competence: float = 0
    n_sources = len(reliabilities)
    sources = np.array(range(len(reliabilities)))
    if n_sources == 0:
        return 0
    if weights is None:
        weights = np.ones(n_sources)
    total_weight = sum(weights)
    threshold = total_weight / 2

    for sources_positive in powerset(sources):
        sources_positive = np.array(sources_positive)
        weight_sources_positive = 0
        if len(sources_positive) != 0:
            weight_sources_positive = np.sum(weights[sources_positive])
        if weight_sources_positive >= threshold:
            probabilities_list = [
                reliabilities[source] for source in sources_positive
            ] + [
                1 - reliabilities[source]
                for source in sources
                if source not in sources_positive
            ]
            probability_subset: float = float(np.prod(probabilities_list))
            if weight_sources_positive > threshold:
                competence += probability_subset
            elif weight_sources_positive == threshold:
                competence += probability_subset / 2
    return competence
