"""Structural validation for the raw workbook (docs/architecture.md §4.2).
Plain assertions rather than a schema-validation dependency — the checks
are few and fixed enough that explicit code is easier to audit than a DSL.
"""
from __future__ import annotations

import re

import pandas as pd


class ValidationError(Exception):
    """Raised when the raw workbook no longer matches the audited shape."""


# docs/data-audit.md §1.1 — header row, cols A-K (D has no header: merged C1:D1)
EXPECTED_HEADER = [
    "TT", "Mã SV", "Họ tên", None, "Ngày sinh", "Nơi sinh",
    "Mã lớp", "TTTN", "Số TCTL", "Điểm TBCTL", "Ghi chú",
]

MASV_RE = re.compile(r"^[A-Z]\d{2}DC[A-Z]{2,3}\d{3}B?$")
CPA_RE = re.compile(r"^\d\.\d{2}$")
KNOWN_GHICHU = {"Làm ĐATN", "Không đủ đk"}


def validate_sheet_name(sheetnames: list[str]) -> None:
    if sheetnames != ["Data"]:
        raise ValidationError(f"Expected a single sheet named 'Data', found {sheetnames}")


def validate_header(header_row: list) -> None:
    got = list(header_row[:11])
    if got != EXPECTED_HEADER:
        raise ValidationError(
            "Header row does not match the audited schema (docs/data-audit.md §1.1).\n"
            f"Expected: {EXPECTED_HEADER}\nGot:      {got}"
        )


def validate_raw_frame(df: pd.DataFrame, expected_rows: int) -> list[str]:
    """Return non-fatal warnings; raise ValidationError on fatal structural issues."""
    warnings: list[str] = []

    if len(df) != expected_rows:
        warnings.append(
            f"Row count is {len(df)}, expected {expected_rows} "
            "(source file may have changed since docs/data-audit.md was written)."
        )

    if df["ma_sv"].isna().any():
        raise ValidationError("Column 'Mã SV' contains null values; expected fully populated.")

    if df["ma_sv"].duplicated().any():
        dupes = df.loc[df["ma_sv"].duplicated(), "ma_sv"].tolist()
        raise ValidationError(f"Duplicate 'Mã SV' values found: {dupes}")

    bad_ids = df.loc[~df["ma_sv"].str.match(MASV_RE), "ma_sv"].tolist()
    if bad_ids:
        raise ValidationError(f"'Mã SV' values with unexpected format: {bad_ids}")

    bad_ghichu = set(df["ghi_chu"].dropna().unique()) - KNOWN_GHICHU
    if bad_ghichu:
        raise ValidationError(f"Unexpected 'Ghi chú' values: {bad_ghichu}")

    cpa_raw = df["diem_tbctl"].dropna()
    cpa_raw = cpa_raw[cpa_raw.astype(str).str.strip() != ""]
    bad_cpa = cpa_raw[~cpa_raw.astype(str).str.match(CPA_RE)].tolist()
    if bad_cpa:
        raise ValidationError(f"'Điểm TBCTL' values with unexpected format: {bad_cpa}")

    credits = pd.to_numeric(df["so_tctl"], errors="coerce").dropna()
    if len(credits) and not credits.between(0, 146).all():
        raise ValidationError("'Số TCTL' contains values outside the expected 0-146 range.")

    return warnings
