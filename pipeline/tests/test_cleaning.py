"""Cleaning rules keep the exact behaviour documented in docs/data-audit.md §6."""
from __future__ import annotations


def test_raw_row_count(raw_df):
    assert len(raw_df) == 2023


def test_cpa_is_numeric_and_in_range(clean_df):
    assert clean_df["cpa"].dtype.kind == "f"
    assert clean_df["cpa"].dropna().between(0, 4).all()


def test_empty_strings_become_missing(clean_df):
    # 3 rows have an empty-string CPA in the source file (rule D1 / C5 in the audit)
    assert clean_df["cpa"].isna().sum() == 3


def test_no_cpa_outlier_is_removed(clean_df):
    # rule E5 — outliers are flagged, never trimmed; the known minimum survives
    assert clean_df["cpa"].min() == 1.25


def test_birthplace_whitespace_collapsed(clean_df):
    assert not clean_df["birthplace"].dropna().str.contains(r"\s{2,}", regex=True).any()


def test_birthplace_mapping_applied(clean_df):
    assert "TP. Hồ Chí Minh" not in clean_df["birthplace"].dropna().values


def test_dob_implausible_flagged_not_corrected(clean_df):
    flagged = clean_df[clean_df["dob_implausible"]]
    assert len(flagged) >= 1
    assert (flagged["ma_sv"] == "B23DCDT089").any()


def test_scope_row_count(scoped_df):
    assert len(scoped_df) == 905


def test_scope_class_and_track_counts(scoped_df):
    assert scoped_df["class_code"].nunique() == 18
    assert scoped_df["track_label"].nunique() == 5


def test_program_mapping(scoped_df):
    counts = scoped_df["program"].value_counts().to_dict()
    assert counts["CNTT"] == 690
    assert counts["CNTT CLC"] == 215
