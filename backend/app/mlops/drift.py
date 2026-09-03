"""Deterministic feature drift calculations."""

from math import sqrt
from statistics import mean


def mean_absolute_error(predictions: list[float], actuals: list[float]) -> float:
    if len(predictions) != len(actuals) or not predictions:
        raise ValueError("predictions and actuals must have equal non-zero length")
    return mean(abs(predicted - actual) for predicted, actual in zip(predictions, actuals))


def population_drift(reference: list[float], current: list[float]) -> float:
    if not reference or not current:
        raise ValueError("drift samples cannot be empty")
    reference_mean = mean(reference)
    current_mean = mean(current)
    scale = sqrt(mean((value - reference_mean) ** 2 for value in reference)) or 1.0
    return abs(current_mean - reference_mean) / scale
