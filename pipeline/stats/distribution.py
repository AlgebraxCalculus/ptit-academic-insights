"""Histogram binning shared between the static charts and Explore's own
re-binning of filtered subsets — docs/insight-discovery.md §O."""
from __future__ import annotations

import numpy as np

import config


def histogram(
    values,
    bin_width: float = config.CPA_HISTOGRAM_BIN_WIDTH,
    domain: tuple[float, float] = config.CPA_HISTOGRAM_DOMAIN,
) -> tuple[list[float], list[int]]:
    x = np.asarray(values, dtype=float)
    x = x[~np.isnan(x)]
    edges = np.arange(domain[0], domain[1] + bin_width / 2, bin_width)
    counts, edges = np.histogram(x, bins=edges)
    return [round(float(e), 2) for e in edges], [int(c) for c in counts]
