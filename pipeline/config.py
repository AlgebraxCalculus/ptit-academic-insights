"""Central configuration for the PTIT Academic Insights data pipeline.

Every constant here is traceable to a decision recorded in docs/data-audit.md,
docs/insight-discovery.md or docs/architecture.md. Do not change a value here
without updating the corresponding doc first.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

RAW_XLSX = ROOT / "data" / "raw" / "DS-SV-DK-DATN-D22-KY-THUAT.xlsx"
INTERIM_DIR = ROOT / "data" / "interim"
INTERIM_PARQUET = INTERIM_DIR / "students_clean.parquet"
REFERENCE_DIR = ROOT / "data" / "reference"
BIRTHPLACE_MAP_CSV = REFERENCE_DIR / "birthplace_mapping.csv"

SITE_DATA_DIR = ROOT / "site" / "src" / "data"
SCHEMA_DIR = Path(__file__).resolve().parent / "schema"
PRIVACY_REPORT = Path(__file__).resolve().parent / "privacy-report.md"

SHEET_NAME = "Data"
RAW_COLUMNS = [
    "tt", "ma_sv", "ho_dem", "ten", "ngay_sinh", "noi_sinh",
    "ma_lop", "tttn", "so_tctl", "diem_tbctl", "ghi_chu",
]

# docs/data-audit.md §1.1
EXPECTED_RAW_ROWS = 2023

# docs/data-audit.md §1.4 (rule B1) — CNTT (D22CNPM, D22HTTT) + CNTT CLC (E22*)
SCOPE_REGEX = r"^(D22CNPM|D22HTTT|E22)"
EXPECTED_SCOPE_ROWS = 905

# docs/insight-discovery.md §Phụ lục
BOOTSTRAP_ITERATIONS = 10_000
BOOTSTRAP_SEED = 42

# docs/architecture.md §9.3 (privacy gate)
MIN_GROUP_SIZE = 10
MIN_GROUP_SIZE_FOR_MEAN = 20
ALLOWED_ROW_FIELDS = {"track", "major", "cpa", "cr", "el"}

# docs/data-audit.md §2 (evidence: full file)
NON_DOMESTIC_BIRTHPLACES = {"Lào", "Liên Bang Nga", "CHLB Đức"}

# docs/data-audit.md §2 — 9-point letter scale
TTTN_GRADE_ORDER = ["F", "D", "D+", "C", "C+", "B", "B+", "A", "A+"]

# docs/architecture.md §5.2 — fixed dictionaries so index coding is stable across builds
TRACK_DICTIONARY = ["D22CNPM", "D22HTTT", "E22CNPM", "E22HTTT", "E22TTNT"]
MAJOR_DICTIONARY = ["DCAT", "DCCI", "DCCN", "DCDK", "DCDT", "DCKH", "DCVT"]
PROGRAM_DICTIONARY = ["CNTT", "CNTT CLC"]

CPA_HISTOGRAM_BIN_WIDTH = 0.1
CPA_HISTOGRAM_DOMAIN = (1.2, 3.9)
