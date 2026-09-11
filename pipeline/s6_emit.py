"""S6 — validate against JSON Schema and write the anonymized artifacts that
the frontend consumes. docs/architecture.md §5.
"""
from __future__ import annotations

import json
from datetime import UTC, datetime

import jsonschema

import config

PIPELINE_VERSION = "1.0.0"


def _load_schema(name: str) -> dict:
    return json.loads((config.SCHEMA_DIR / name).read_text(encoding="utf-8"))


def build_meta(df, source_rows_total: int, source_sha256: str) -> dict:
    cohort = df["intake_year"].value_counts().sort_index().to_dict()
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "pipeline_version": PIPELINE_VERSION,
        "source_file_sha256": source_sha256,
        "source_rows_total": source_rows_total,
        "scope_regex": config.SCOPE_REGEX,
        "n_in_scope": len(df),
        "n_with_cpa": int(df["cpa"].notna().sum()),
        "n_classes": df["class_code"].nunique(),
        "n_tracks": df["track_label"].nunique(),
        "n_programs": df["program"].nunique(),
        "cohort": {str(k): int(v) for k, v in cohort.items()},
        "min_group_size": config.MIN_GROUP_SIZE,
        "bootstrap": {"iterations": config.BOOTSTRAP_ITERATIONS, "seed": config.BOOTSTRAP_SEED},
        "dictionaries": {
            "track": config.TRACK_DICTIONARY,
            "program": config.PROGRAM_DICTIONARY,
            "major": config.MAJOR_DICTIONARY,
        },
    }


def validate(payload: dict, schema_name: str) -> None:
    schema = _load_schema(schema_name)
    jsonschema.validate(instance=payload, schema=schema)


def emit(meta: dict, rows: dict, aggregates: dict, histograms: dict) -> None:
    validate(meta, "meta.schema.json")
    validate(rows, "rows.schema.json")
    validate(aggregates, "aggregates.schema.json")
    validate(histograms, "histograms.schema.json")

    config.SITE_DATA_DIR.mkdir(parents=True, exist_ok=True)
    for name, payload in [
        ("meta.json", meta),
        ("rows.json", rows),
        ("aggregates.json", aggregates),
        ("histograms.json", histograms),
    ]:
        path = config.SITE_DATA_DIR / name
        path.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
