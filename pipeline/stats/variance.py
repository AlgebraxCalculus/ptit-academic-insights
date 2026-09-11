"""One-way variance decomposition (eta squared) — docs/insight-discovery.md §1.4."""
from __future__ import annotations

import pandas as pd


def eta_squared(df: pd.DataFrame, value_col: str, group_col: str, min_n: int = 1) -> tuple[float, int]:
    """Share of variance in value_col explained by group_col.

    Descriptive only: how well a grouping SEPARATES the data, not evidence
    that the grouping CAUSES the outcome (see docs/insight-discovery.md §7.2).
    """
    sub = df.dropna(subset=[value_col, group_col])
    groups = [g[value_col].to_numpy() for _, g in sub.groupby(group_col, observed=True) if len(g) >= min_n]
    grand_mean = sub[value_col].mean()
    ssb = sum(len(g) * (g.mean() - grand_mean) ** 2 for g in groups)
    ssw = sum(((g - g.mean()) ** 2).sum() for g in groups)
    return float(ssb / (ssb + ssw)), len(groups)


def r_squared_pearson(x, y) -> float:
    import numpy as np
    from scipy import stats as sstats

    xa, ya = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    mask = ~(np.isnan(xa) | np.isnan(ya))
    r, _ = sstats.pearsonr(xa[mask], ya[mask])
    return float(r**2)
