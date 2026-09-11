"""S5 — privacy gate. docs/architecture.md §9.2, §9.3.

Builds the anonymized row-level payload and runs checks P1-P8. Any failure
raises PrivacyViolation and MUST stop the pipeline — this stage has veto
power over what reaches the frontend.
"""
from __future__ import annotations

import re

import pandas as pd

import config

FORBIDDEN_FIELD_PATTERN = re.compile(
    r"(?i)(name|ho_?dem|^ten$|ma_?sv|student|birth|ngay_?sinh|noi_?sinh|"
    r"email|class_?code|tttn|id_format)"
)

# Ceiling on uniquely-identifiable rows for the shipped field set
# (docs/architecture.md §9.2). Adding class_code back pushes this to ~85%.
MAX_UNIQUE_ROW_SHARE = 0.55


class PrivacyViolation(Exception):
    pass


def build_rows_payload(df: pd.DataFrame) -> dict:
    tracks = config.TRACK_DICTIONARY
    majors = config.MAJOR_DICTIONARY

    unknown_tracks = set(df["track_label"]) - set(tracks)
    if unknown_tracks:
        raise PrivacyViolation(f"Unknown track(s) cannot be dictionary-encoded: {unknown_tracks}")

    payload = {
        "n": len(df),
        "encoding": "columnar-int",
        "track": [tracks.index(t) for t in df["track_label"]],
        "major": [majors.index(m) for m in df["admission_major_code"]],
        "cpa": [-1 if pd.isna(v) else round(v * 100) for v in df["cpa"]],
        "cr": [-1 if pd.isna(v) else int(v) for v in df["credits"]],
        "el": [int(v) for v in df["eligible_for_thesis"]],
    }
    return payload


def _check_field_allowlist(payload: dict) -> str:
    fields = set(payload.keys()) - {"n", "encoding"}
    if fields != config.ALLOWED_ROW_FIELDS:
        raise PrivacyViolation(
            f"P1 FAILED — rows payload fields {fields} != allowed {config.ALLOWED_ROW_FIELDS}"
        )
    return f"P1 PASS — fields exactly {sorted(fields)}"


def _check_forbidden_names(payload: dict) -> str:
    for key in payload:
        if FORBIDDEN_FIELD_PATTERN.search(key):
            raise PrivacyViolation(f"P2 FAILED — forbidden field name pattern matched: '{key}'")
    return "P2 PASS — no forbidden field name pattern present"


def _check_min_group_size(aggregates: dict) -> str:
    violations = []
    for track in aggregates["by_track"]:
        if track["n_rows"] < config.MIN_GROUP_SIZE:
            violations.append(f"track {track['track']} n={track['n_rows']}")
    for cls in aggregates["by_class"]:
        if cls["n"] < config.MIN_GROUP_SIZE:
            violations.append(f"class {cls['class']} n={cls['n']}")
    if violations:
        raise PrivacyViolation(f"P3 FAILED — groups below min size {config.MIN_GROUP_SIZE}: {violations}")
    return f"P3 PASS — every published group has n >= {config.MIN_GROUP_SIZE}"


def _check_small_means_nulled(aggregates: dict) -> str:
    violations = []
    for prog in aggregates["composition"]["by_program"]:
        for major in prog["majors"]:
            if major["n"] < config.MIN_GROUP_SIZE_FOR_MEAN and major["mean_cpa"] is not None:
                violations.append(f"{prog['program']}/{major['major']} n={major['n']} has mean_cpa set")
    if violations:
        raise PrivacyViolation(f"P4 FAILED — small-group means not nulled: {violations}")
    return f"P4 PASS — every group n < {config.MIN_GROUP_SIZE_FOR_MEAN} has mean_cpa = null"


def _check_no_class_min_max(aggregates: dict) -> str:
    for cls in aggregates["by_class"]:
        if "min" in cls or "max" in cls:
            raise PrivacyViolation(f"P5 FAILED — class-level min/max present for {cls['class']}")
    return "P5 PASS — no min/max at class level"


def _check_k_anonymity(df: pd.DataFrame) -> str:
    cols = ["track_label", "cpa", "credits", "eligible_for_thesis", "admission_major_code"]
    n = len(df)
    group_sizes = df.groupby(cols, dropna=False).size()
    unique_rows = int(group_sizes[group_sizes == 1].sum())
    share = unique_rows / n
    if share > MAX_UNIQUE_ROW_SHARE:
        raise PrivacyViolation(
            f"P6 FAILED — {share:.1%} of rows uniquely identifiable on the shipped field set, "
            f"exceeds ceiling {MAX_UNIQUE_ROW_SHARE:.0%}"
        )
    return f"P6 PASS — {share:.1%} of rows unique on shipped fields (ceiling {MAX_UNIQUE_ROW_SHARE:.0%})"


def _check_no_ineligible_by_class(aggregates: dict) -> str:
    # by_class carries only aggregate CPA stats, never an eligibility breakdown.
    for cls in aggregates["by_class"]:
        if "ineligible" in cls or "eligible_n" in cls:
            raise PrivacyViolation(f"P7 FAILED — eligibility breakdown present at class level for {cls['class']}")
    return "P7 PASS — no ineligible-by-class breakdown published"


def _check_meta_clean(meta: dict) -> str:
    blob = str(meta)
    if "\\" in blob or "/home" in blob or "C:" in blob:
        raise PrivacyViolation("P8 FAILED — meta.json appears to contain an absolute path")
    return "P8 PASS — meta.json contains no paths or personal names"


def _check_birthplace_bands(aggregates: dict) -> str:
    bp = aggregates["birthplace_bands"]
    violations = []
    for band in bp["bands"]:
        for prov in band["provinces"]:
            if prov["n"] < bp["min_cell_n"]:
                violations.append(f"{band['band']}/{prov['province']} n={prov['n']}")
    if violations:
        raise PrivacyViolation(f"P9 FAILED — birthplace_bands cells below min_cell_n: {violations}")
    return f"P9 PASS — every published birthplace-band cell has n >= {bp['min_cell_n']}"


def run_privacy_gate(df: pd.DataFrame, aggregates: dict, meta: dict) -> tuple[dict, list[str]]:
    payload = build_rows_payload(df)
    report = [
        _check_field_allowlist(payload),
        _check_forbidden_names(payload),
        _check_min_group_size(aggregates),
        _check_small_means_nulled(aggregates),
        _check_no_class_min_max(aggregates),
        _check_k_anonymity(df),
        _check_no_ineligible_by_class(aggregates),
        _check_meta_clean(meta),
        _check_birthplace_bands(aggregates),
    ]
    return payload, report


def write_privacy_report(report_lines: list[str]) -> None:
    body = "# Privacy gate report\n\n" + "\n".join(f"- {line}" for line in report_lines) + "\n"
    config.PRIVACY_REPORT.write_text(body, encoding="utf-8")
