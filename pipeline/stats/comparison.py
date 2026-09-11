"""Two-group and multi-group comparison utilities — used throughout
docs/insight-discovery.md (program comparison, track contrast, eligibility).
"""
from __future__ import annotations

import numpy as np
from scipy import stats as sstats

from stats.bootstrap import bootstrap_diff_ci


def cohens_d(x, y) -> float:
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    n1, n2 = len(x), len(y)
    pooled_sd = np.sqrt(((n1 - 1) * x.var(ddof=1) + (n2 - 1) * y.var(ddof=1)) / (n1 + n2 - 2))
    return float((x.mean() - y.mean()) / pooled_sd)


def cliffs_delta(x, y) -> float:
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    gt = int((x[:, None] > y[None, :]).sum())
    lt = int((x[:, None] < y[None, :]).sum())
    return (gt - lt) / (len(x) * len(y))


def compare_two_groups(x, y, x_label: str, y_label: str) -> dict:
    """Compare a foreground group x against a reference group y.

    Returns diff = mean(x) - mean(y), with a bootstrap CI in that direction,
    plus Mann-Whitney U, Welch's t, Cohen's d and Cliff's delta.
    """
    xa = np.asarray(x, dtype=float)
    xa = xa[~np.isnan(xa)]
    ya = np.asarray(y, dtype=float)
    ya = ya[~np.isnan(ya)]

    mw = sstats.mannwhitneyu(xa, ya, alternative="two-sided")
    welch = sstats.ttest_ind(xa, ya, equal_var=False)
    ci = bootstrap_diff_ci(xa, ya)

    def describe(a):
        return {
            "n": len(a),
            "mean": round(float(a.mean()), 4),
            "median": round(float(np.median(a)), 4),
            "sd": round(float(a.std(ddof=1)), 4),
        }

    return {
        x_label: describe(xa),
        y_label: describe(ya),
        "diff": round(float(xa.mean() - ya.mean()), 4),
        "ci": [round(v, 4) for v in ci],
        "p_mannwhitney": float(mw.pvalue),
        "p_welch": float(welch.pvalue),
        "cohens_d": round(cohens_d(xa, ya), 4),
        "cliffs_delta": round(cliffs_delta(xa, ya), 4),
    }


def kruskal_groups(groups: list) -> dict:
    cleaned = []
    for g in groups:
        a = np.asarray(g, dtype=float)
        cleaned.append(a[~np.isnan(a)])
    h, p = sstats.kruskal(*cleaned)
    return {"H": round(float(h), 4), "p": float(p), "k": len(cleaned)}


def chi2_independence(contingency: np.ndarray) -> dict:
    result = sstats.chi2_contingency(contingency)
    n = contingency.sum()
    cramers_v = float(np.sqrt(result.statistic / n))
    return {"chi2": round(float(result.statistic), 4), "p": float(result.pvalue), "cramers_v": round(cramers_v, 4)}


def fisher_exact_2x2(table: np.ndarray) -> float:
    _, p = sstats.fisher_exact(table)
    return float(p)


BONFERRONI_ALPHA_20_TESTS = 0.05 / 20


def survives_bonferroni(p: float, alpha: float = BONFERRONI_ALPHA_20_TESTS) -> bool:
    return p < alpha
