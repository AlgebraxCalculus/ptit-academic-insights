"""Overall distribution statistics — docs/insight-discovery.md §1.1, §1.2."""
from __future__ import annotations

import numpy as np
from scipy import stats as sstats

from stats.bootstrap import bootstrap_ci

PERCENTILE_POINTS = [1, 5, 10, 20, 25, 30, 40, 50, 60, 70, 75, 80, 90, 95, 99]


def gini(x: np.ndarray) -> float:
    x = np.sort(np.asarray(x, dtype=float))
    n = len(x)
    return float((2 * np.sum(np.arange(1, n + 1) * x) / (n * np.sum(x))) - (n + 1) / n)


def sarle_bimodality(x: np.ndarray) -> float:
    """Sarle's bimodality coefficient. > 0.555 suggests bimodality (rule of thumb)."""
    skew = sstats.skew(x)
    kurt = sstats.kurtosis(x)
    return float((skew**2 + 1) / (kurt + 3))


def percentile_profile(values, points: list[int] = PERCENTILE_POINTS) -> dict[str, float]:
    x = np.asarray(values, dtype=float)
    x = x[~np.isnan(x)]
    return {f"p{p}": round(float(np.quantile(x, p / 100)), 4) for p in points}


def overall_statistics(values) -> dict:
    """Full descriptive profile of a numeric series (used for CPA)."""
    x = np.asarray(values, dtype=float)
    x = x[~np.isnan(x)]
    n = len(x)
    q1, q3 = float(np.quantile(x, 0.25)), float(np.quantile(x, 0.75))

    return {
        "n": n,
        "mean": round(float(x.mean()), 4),
        "mean_ci": [round(v, 4) for v in bootstrap_ci(x, np.mean)],
        "median": round(float(np.median(x)), 4),
        "median_ci": [round(v, 4) for v in bootstrap_ci(x, np.median)],
        "sd": round(float(x.std(ddof=1)), 4),
        "variance": round(float(x.var(ddof=1)), 4),
        "iqr": round(q3 - q1, 4),
        "q1": round(q1, 4),
        "q3": round(q3, 4),
        "min": round(float(x.min()), 4),
        "max": round(float(x.max()), 4),
        "skew": round(float(sstats.skew(x)), 4),
        "kurtosis": round(float(sstats.kurtosis(x)), 4),
        "gini": round(gini(x), 4),
        "sarle_bc": round(sarle_bimodality(x), 4),
        "percentiles": percentile_profile(x),
    }
