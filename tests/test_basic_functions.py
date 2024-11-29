import numpy as np

from utils import config as cfg
from utils.basic_functions import (
    calculate_accuracy_precision_proportion,
    calculate_competence,
    calculate_diversity,
    majority_winner,
    powerset,
)


def test_majority_winner():
    values = [
        cfg.vote_for_positive,
        cfg.vote_for_negative,
        cfg.vote_for_negative,
        cfg.vote_for_positive,
        cfg.vote_for_negative,
    ]
    assert majority_winner(values) == cfg.vote_for_negative

    values = [
        cfg.vote_for_positive,
        cfg.vote_for_negative,
        cfg.vote_for_negative,
        cfg.vote_for_positive,
    ]
    result = majority_winner(values)
    assert result == cfg.vote_for_negative or result == cfg.vote_for_positive


def test_powerset():
    test_list = [0, 1, 5]
    powerset_list = [(), (0,), (1,), (5,), (0, 1), (0, 5), (1, 5), (0, 1, 5)]
    assert all([item in powerset_list for item in powerset(test_list)])
    assert all([item in powerset(test_list) for item in powerset_list])


def test_calculate_diversity():
    assert calculate_diversity([0, 1, 2], [0, 3, 4]) == 2 / 3
    assert calculate_diversity([0], [0]) == 0
    assert calculate_diversity(["a", "b", "c"], ["a", 1, "b"]) == 1 / 3


def test_calculate_competence():
    assert calculate_competence([0.5, 0.5, 0.5]) == 0.5
    assert calculate_competence([1, 1, 1]) == 1
    assert calculate_competence([0, 0, 0]) == 0
    assert (
        calculate_competence([0.6, 0.6, 0.6]) - (3 * 0.4 * 0.6**2 + 0.6**3)
    ) < 10 ** (-5)
    assert calculate_competence([0.6, 0.7, 0.8]) - (
        0.6 * 0.7 * 0.2 + 0.6 * 0.3 * 0.8 + 0.4 * 0.7 * 0.8 + 0.6 * 0.7 * 0.8
    ) < 10 ** (-5)


def test_calculate_accuracy_precision_proportion():
    list_of_items = [cfg.vote_for_negative for _ in range(3)] + [
        cfg.vote_for_positive for _ in range(5)
    ]
    accuracy, _, _ = calculate_accuracy_precision_proportion(list_of_items)
    assert accuracy > 0.5
    array_of_items = np.array(list_of_items)
    accuracy_new, _, _ = calculate_accuracy_precision_proportion(array_of_items)
    assert accuracy == accuracy_new
