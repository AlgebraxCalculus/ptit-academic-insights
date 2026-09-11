"""S3 — scope filter (rule B1) and derived analytical fields (rules C1-C7).

docs/data-audit.md §1.4, §6, §10
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import config


def scope_and_derive(df: pd.DataFrame) -> pd.DataFrame:
    df = df[df["ma_lop"].str.match(config.SCOPE_REGEX, na=False)].copy()
    assert len(df) == config.EXPECTED_SCOPE_ROWS, (
        f"In-scope row count is {len(df)}, expected {config.EXPECTED_SCOPE_ROWS}. "
        "The source file's class composition may have changed — "
        "update docs/data-audit.md before proceeding."
    )

    df["class_code"] = df["ma_lop"]
    df["track_label"] = df["ma_lop"].str.replace(r"\d{2}$", "", regex=True)
    df["class_prefix"] = df["ma_lop"].str[0]
    df["admission_major_code"] = df["ma_sv"].str[3:7]
    df["intake_year"] = 2000 + df["ma_sv"].str[1:3].astype(int)

    # program mapping confirmed by the school's convention — insight-discovery.md §0
    df["program"] = np.where(df["class_prefix"] == "E", "CNTT CLC", "CNTT")

    df["is_off_cohort"] = df["intake_year"] != 2022
    df["id_format_anomaly"] = df["ma_sv"].str.len() != 10
    df["eligible_for_thesis"] = df["ghi_chu"].eq("Làm ĐATN")

    df["tttn_grade"] = pd.Categorical(df["tttn"], categories=config.TTTN_GRADE_ORDER, ordered=True)

    unknown_tracks = set(df["track_label"]) - set(config.TRACK_DICTIONARY)
    assert not unknown_tracks, f"Unknown track(s) in scope: {unknown_tracks}"
    unknown_majors = set(df["admission_major_code"].dropna()) - set(config.MAJOR_DICTIONARY)
    assert not unknown_majors, f"Unknown admission major code(s) in scope: {unknown_majors}"

    return df.reset_index(drop=True)
