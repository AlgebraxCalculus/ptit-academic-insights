"""S2 — cleaning rules per docs/data-audit.md §6 (rules A3, A4, D1, E1, E2, E4).

Nothing here removes or imputes a value. Rows D2/D3 of the audit (never
impute CPA or TTTN — both are missing-not-at-random) are honoured by simply
not touching them beyond type coercion.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import config


def load_birthplace_map() -> dict[str, str]:
    if not config.BIRTHPLACE_MAP_CSV.exists():
        return {}
    m = pd.read_csv(config.BIRTHPLACE_MAP_CSV)
    return dict(zip(m["raw"], m["normalized"]))


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    text_cols = ["ma_sv", "ho_dem", "ten", "ngay_sinh", "noi_sinh", "ma_lop", "tttn", "diem_tbctl", "ghi_chu"]
    for c in text_cols:
        df[c] = df[c].apply(lambda v: v.strip() if isinstance(v, str) else v)
        df[c] = df[c].replace("", np.nan)  # rule D1 — empty string is a missing value, not a value

    # rule A3 — CPA text -> float, with a hard scale assertion
    df["cpa"] = pd.to_numeric(df["diem_tbctl"], errors="coerce")
    valid_cpa = df["cpa"].dropna()
    assert valid_cpa.between(0, 4).all(), "CPA outside the [0, 4] scale — stop and investigate."

    # rule A4 — explicit day-first date parsing (never rely on locale inference)
    dob = pd.to_datetime(df["ngay_sinh"], format="%d/%m/%Y", errors="coerce")
    df["birth_year"] = dob.dt.year

    # rule E1 — collapse repeated whitespace in birthplace
    df["birthplace"] = df["noi_sinh"].str.replace(r"\s+", " ", regex=True)
    # rule E2 — apply the versioned, reviewable birthplace mapping
    bp_map = load_birthplace_map()
    if bp_map:
        df["birthplace"] = df["birthplace"].replace(bp_map)

    df["birthplace_is_domestic"] = ~df["birthplace"].isin(config.NON_DOMESTIC_BIRTHPLACES)

    # rule E4 — flag implausible birth years; never silently correct or drop
    df["dob_implausible"] = ~df["birth_year"].between(1990, 2010)

    df["credits"] = pd.to_numeric(df["so_tctl"], errors="coerce")

    # rules D2/D3 — TTTN and CPA missingness is MNAR; flagged, never imputed
    df["tttn_missing"] = df["tttn"].isna()
    df["cpa_missing"] = df["cpa"].isna()

    return df
