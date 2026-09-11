"""Privacy gate tests — docs/architecture.md §9.2, §9.3.

These tests exist to make an unsafe change to the client payload fail CI,
not just fail at pipeline-run time.
"""
from __future__ import annotations

import pytest

import config
import s4_metrics
import s5_privacy


@pytest.fixture(scope="module")
def aggregates(scoped_df):
    return s4_metrics.compute_all(scoped_df)


@pytest.fixture(scope="module")
def meta(scoped_df):
    return {"generated_at": "test", "n_in_scope": len(scoped_df)}


def test_rows_payload_field_allowlist(scoped_df):
    payload = s5_privacy.build_rows_payload(scoped_df)
    fields = set(payload.keys()) - {"n", "encoding"}
    assert fields == config.ALLOWED_ROW_FIELDS


def test_rows_payload_excludes_class_code(scoped_df):
    payload = s5_privacy.build_rows_payload(scoped_df)
    assert "class_code" not in payload
    assert "class" not in payload


def test_rows_payload_excludes_tttn(scoped_df):
    payload = s5_privacy.build_rows_payload(scoped_df)
    assert "tttn" not in payload


def test_rows_payload_excludes_identifiers(scoped_df):
    payload = s5_privacy.build_rows_payload(scoped_df)
    blob = str(payload.keys())
    for forbidden in ["ma_sv", "name", "ho_dem", "ten", "birth", "email"]:
        assert forbidden not in blob


def test_full_gate_passes_on_current_data(scoped_df, aggregates, meta):
    payload, report = s5_privacy.run_privacy_gate(scoped_df, aggregates, meta)
    assert len(report) == 9
    assert all("PASS" in line for line in report)
    assert payload["n"] == 905


def test_adding_class_code_would_fail_k_anonymity(scoped_df):
    """Reproduces the measurement in docs/architecture.md §9.2: shipping
    class_code alongside cpa/credits/eligibility/major pushes uniqueness to
    ~85%, far past the approved ceiling."""
    cols = ["class_code", "cpa", "credits", "eligible_for_thesis", "tttn", "admission_major_code"]
    group_sizes = scoped_df.groupby(cols, dropna=False).size()
    unique_share = group_sizes[group_sizes == 1].sum() / len(scoped_df)
    assert unique_share > 0.55, "expected the rejected field set to exceed the ceiling"


def test_small_group_means_are_nulled(aggregates):
    for prog in aggregates["composition"]["by_program"]:
        for m in prog["majors"]:
            if m["n"] < config.MIN_GROUP_SIZE_FOR_MEAN:
                assert m["mean_cpa"] is None, f"{prog['program']}/{m['major']} should be nulled"


def test_by_class_has_no_min_max_keys(aggregates):
    for cls in aggregates["by_class"]:
        assert "min" not in cls
        assert "max" not in cls


def test_by_class_has_no_eligibility_breakdown(aggregates):
    for cls in aggregates["by_class"]:
        assert "eligible_n" not in cls
        assert "ineligible" not in cls


def test_no_group_below_min_size_in_published_aggregates(aggregates):
    assert all(t["n_rows"] >= config.MIN_GROUP_SIZE for t in aggregates["by_track"])
    assert all(c["n"] >= config.MIN_GROUP_SIZE for c in aggregates["by_class"])
