"""Bootstrap resampling utilities.

Seeded (default seed 42, 10,000 iterations — docs/insight-discovery.md
Phụ lục) so a rebuild from unchanged input data reproduces the same
confidence intervals bit-for-bit.
"""
from __future__ import annotations

import numpy as np

import config


def _clean(values) -> np.ndarray:
    x = np.asarray(values, dtype=float)
    return x[~np.isnan(x)]


def bootstrap_ci(
    values,
    statistic=np.mean,
    iterations: int = config.BOOTSTRAP_ITERATIONS,
    seed: int = config.BOOTSTRAP_SEED,
    alpha: float = 0.05,
) -> tuple[float, float]:
    """Bootstrap confidence interval for a statistic of a single sample."""
    x = _clean(values)
    rng = np.random.default_rng(seed)
    resamples = rng.choice(x, size=(iterations, len(x)), replace=True)
    stat_values = statistic(resamples, axis=1)
    lo, hi = np.quantile(stat_values, [alpha / 2, 1 - alpha / 2])
    return float(lo), float(hi)


def bootstrap_diff_ci(
    x,
    y,
    iterations: int = config.BOOTSTRAP_ITERATIONS,
    seed: int = config.BOOTSTRAP_SEED,
    alpha: float = 0.05,
) -> tuple[float, float]:
    """CI for mean(x) - mean(y), resampling x then y each iteration.

    x is the "foreground" group (e.g. CNTT CLC), y the reference group
    (e.g. CNTT) — the sign of the returned interval follows x - y.
    """
    xa, ya = _clean(x), _clean(y)
    rng = np.random.default_rng(seed)
    diffs = np.empty(iterations)
    for i in range(iterations):
        diffs[i] = rng.choice(xa, len(xa)).mean() - rng.choice(ya, len(ya)).mean()
    lo, hi = np.quantile(diffs, [alpha / 2, 1 - alpha / 2])
    return float(lo), float(hi)
