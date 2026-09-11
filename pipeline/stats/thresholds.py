"""Threshold / classification-band analysis — docs/insight-discovery.md §1.2."""
from __future__ import annotations

import numpy as np
from scipy import stats as sstats

# (label, inclusive lower bound, exclusive upper bound) on the 4.0-point scale
CLASSIFICATION_BANDS = [
    ("Xuất sắc", 3.60, 4.01),
    ("Giỏi", 3.20, 3.60),
    ("Khá", 2.50, 3.20),
    ("Trung bình", 2.00, 2.50),
    ("Yếu", 0.0, 2.00),
]

DEFAULT_CUMULATIVE_THRESHOLDS = (2.0, 2.5, 3.0, 3.2, 3.5, 3.6)


def threshold_bands(values, bands=CLASSIFICATION_BANDS) -> list[dict]:
    x = np.asarray(values, dtype=float)
    x = x[~np.isnan(x)]
    n = len(x)
    out = []
    for label, lo, hi in bands:
        mask = (x >= lo) & (x < hi)
        k = int(mask.sum())
        ci = sstats.binomtest(k, n).proportion_ci(0.95)
        out.append(
            {
                "label": label,
                "min": lo,
                "max": min(hi, 4.0),
                "n": k,
                "pct": round(100 * k / n, 2),
                "ci": [round(100 * ci.low, 2), round(100 * ci.high, 2)],
            }
        )
    return out


def cumulative_thresholds(values, thresholds=DEFAULT_CUMULATIVE_THRESHOLDS) -> list[dict]:
    x = np.asarray(values, dtype=float)
    x = x[~np.isnan(x)]
    return [
        {"threshold": t, "n": int((x >= t).sum()), "pct": round(100 * float((x >= t).mean()), 2)}
        for t in thresholds
    ]


def proportion_ci(k: int, n: int) -> list[float]:
    ci = sstats.binomtest(k, n).proportion_ci(0.95)
    return [round(100 * ci.low, 2), round(100 * ci.high, 2)]
