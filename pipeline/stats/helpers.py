"""Small shared helpers that don't belong to a single analytical concern."""
from __future__ import annotations

import math

import numpy as np


def normal_ci_from_series(x: np.ndarray) -> list[float]:
    """Mean +/- 1.96*SE. Used for group-level tables (by track, by class) where
    bootstrapping every group would be expensive and the normal approximation
    is standard practice with n >= ~30 per group (docs/insight-discovery.md §1.3).
    """
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    n = len(x)
    mean = x.mean()
    se = x.std(ddof=1) / math.sqrt(n)
    return [round(float(mean - 1.96 * se), 4), round(float(mean + 1.96 * se), 4)]


def percentile_rank(value: float, population: np.ndarray) -> float:
    population = np.asarray(population, dtype=float)
    population = population[~np.isnan(population)]
    return round(100 * float((population < value).mean()), 1)
