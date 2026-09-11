"""Every assertion here pins a number back to docs/insight-discovery.md.

If a metric changes, this test changes ONLY after the analytical document is
updated first (docs/architecture.md §8.5) — it exists to catch silent drift
between the pipeline and the analysis it is supposed to reproduce, not to be
edited to match whatever the code currently outputs.

Bootstrap confidence intervals are compared with a wider tolerance since they
depend on the exact numpy/scipy version's random stream; every other figure
is compared tightly.
"""
from __future__ import annotations

import pytest

import s4_metrics


@pytest.fixture(scope="module")
def aggregates(scoped_df):
    return s4_metrics.compute_all(scoped_df)


# --- §1.1 overall CPA distribution ------------------------------------------------

def test_overall_n(aggregates):
    assert aggregates["overall"]["n"] == 903


def test_overall_central_tendency(aggregates):
    o = aggregates["overall"]
    assert o["mean"] == pytest.approx(2.7915, abs=1e-3)
    assert o["median"] == pytest.approx(2.79, abs=1e-3)
    assert o["sd"] == pytest.approx(0.4322, abs=1e-3)
    assert o["iqr"] == pytest.approx(0.59, abs=1e-3)
    assert o["min"] == pytest.approx(1.40, abs=1e-3)
    assert o["max"] == pytest.approx(3.72, abs=1e-3)


def test_overall_mean_ci_reasonable(aggregates):
    lo, hi = aggregates["overall"]["mean_ci"]
    assert lo == pytest.approx(2.763, abs=0.01)
    assert hi == pytest.approx(2.820, abs=0.01)


# --- §1.2 threshold proportions ----------------------------------------------------

def test_bands_sum_to_n(aggregates):
    bands = aggregates["bands"]["classification"]
    assert sum(b["n"] for b in bands) == 903


def test_band_counts(aggregates):
    by_label = {b["label"]: b["n"] for b in aggregates["bands"]["classification"]}
    assert by_label["Xuất sắc"] == 20
    assert by_label["Giỏi"] == 157
    assert by_label["Khá"] == 516
    assert by_label["Trung bình"] == 169
    assert by_label["Yếu"] == 41


# --- §1.4 variance explained (CORE-1) ----------------------------------------------

def test_program_explains_almost_nothing(aggregates):
    by_var = {v["var"]: v["value"] for v in aggregates["variance_explained"]}
    assert by_var["program"] == pytest.approx(0.0109, abs=0.002)


def test_track_explains_far_more_than_program(aggregates):
    by_var = {v["var"]: v["value"] for v in aggregates["variance_explained"]}
    assert by_var["track_label"] == pytest.approx(0.3448, abs=0.005)
    assert by_var["track_label"] > 20 * by_var["program"]


# --- program comparison / Simpson's paradox (CORE-2) --------------------------------

def test_aggregate_program_diff_is_positive(aggregates):
    diff = aggregates["program_comparison"]["aggregate"]["diff"]
    assert diff == pytest.approx(0.1057, abs=0.01)


def test_paired_comparison_reverses_sign(aggregates):
    pairs = {p["pair"]: p["diff"] for p in aggregates["program_comparison"]["paired"]}
    assert pairs["CNPM"] < 0
    assert pairs["HTTT"] > 0
    assert pairs["CNPM"] == pytest.approx(-0.2639, abs=0.01)
    assert pairs["HTTT"] == pytest.approx(0.4325, abs=0.02)


# --- track truncation (CORE-3) -------------------------------------------------------

def test_cnpm_floor_truncation(aggregates):
    truncation = aggregates["track_contrast"]["cnpm_vs_httt"]["truncation"]
    assert truncation["cnpm_min"] == pytest.approx(2.43, abs=0.01)
    assert truncation["cnpm_below_min"] == 0
    assert truncation["cnpm_below_httt_median"] == 1


def test_cnpm_httt_effect_size(aggregates):
    tc = aggregates["track_contrast"]["cnpm_vs_httt"]
    assert tc["diff"] == pytest.approx(0.5352, abs=0.01)
    assert tc["cohens_d"] == pytest.approx(1.538, abs=0.02)


# --- eligibility (CORE-6, CORE-7) ----------------------------------------------------

def test_eligibility_by_program_not_significant(aggregates):
    by_prog = aggregates["eligibility"]["by_program"]
    assert by_prog["cntt"]["pct"] == pytest.approx(91.88, abs=0.1)
    assert by_prog["clc"]["pct"] == pytest.approx(93.95, abs=0.1)
    assert by_prog["significant"] is False


def test_eligibility_by_track_gap(aggregates):
    pairwise = aggregates["eligibility"]["pairwise"]["cnpm_vs_httt"]
    assert pairwise["cnpm_pct"] == pytest.approx(99.45, abs=0.1)
    assert pairwise["httt_pct"] == pytest.approx(83.54, abs=0.1)


def test_ineligible_cpa_not_fully_determined_by_cpa(aggregates):
    nd = aggregates["eligibility"]["cpa_not_determinant"]
    assert nd["ineligible_ge_2_5"] == 9
    assert nd["ineligible_max_cpa"] == pytest.approx(3.37, abs=0.01)


# --- composition (SUP-3) --------------------------------------------------------------

def test_clc_non_cntt_majority(aggregates):
    clc = next(p for p in aggregates["composition"]["by_program"] if p["program"] == "CNTT CLC")
    assert clc["non_cntt_pct"] == pytest.approx(86.5, abs=0.2)


def test_cntt_is_entirely_cntt_admission_code(aggregates):
    cntt = next(p for p in aggregates["composition"]["by_program"] if p["program"] == "CNTT")
    majors = {m["major"]: m["n"] for m in cntt["majors"]}
    assert majors == {"DCCN": cntt["total"]}


# --- small-group suppression (privacy correctness, not just the gate) ---------------

def test_small_admission_majors_have_no_mean(aggregates):
    for prog in aggregates["composition"]["by_program"]:
        for m in prog["majors"]:
            if m["n"] < 20:
                assert m["mean_cpa"] is None


def test_no_class_falls_below_min_group_size(aggregates):
    assert all(c["n"] >= 10 for c in aggregates["by_class"])
    assert all(t["n_rows"] >= 10 for t in aggregates["by_track"])
