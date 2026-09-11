"""Orchestrator: raw xlsx -> validation -> cleaning -> processed dataset ->
metrics -> privacy gate -> anonymized JSON for the frontend.

docs/architecture.md §1, §4

Usage:
    uv run python run.py
"""
from __future__ import annotations

import sys

import config
import s1_ingest
import s2_clean
import s3_scope
import s4_metrics
import s5_privacy
import s6_emit


def main() -> int:
    print("=== PTIT Academic Insights — data pipeline ===\n")

    print(f"[S1] Ingesting {config.RAW_XLSX.name} ...")
    try:
        raw_df, warnings, source_sha256 = s1_ingest.ingest()
    except (FileNotFoundError, Exception) as exc:  # noqa: BLE001 — top-level CLI boundary
        print(f"  FAILED: {exc}")
        return 1
    print(f"  {len(raw_df)} rows read, sha256={source_sha256[:12]}...")
    for w in warnings:
        print(f"  WARNING: {w}")

    print("[S2] Cleaning ...")
    clean_df = s2_clean.clean(raw_df)
    print(f"  {clean_df['cpa'].notna().sum()} rows with a valid CPA (of {len(clean_df)})")

    print("[S3] Scoping + deriving fields ...")
    df = s3_scope.scope_and_derive(clean_df)
    print(f"  {len(df)} rows in scope, {df['class_code'].nunique()} classes, {df['track_label'].nunique()} tracks")

    config.INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(config.INTERIM_PARQUET, index=False)
    print(f"  wrote {config.INTERIM_PARQUET}")

    print("[S4] Computing metrics ...")
    aggregates = s4_metrics.compute_all(df)
    histograms = s4_metrics.compute_histograms(df)
    print(f"  overall mean CPA = {aggregates['overall']['mean']}, n = {aggregates['overall']['n']}")

    print("[S5] Privacy gate ...")
    meta = s6_emit.build_meta(df, len(raw_df), source_sha256)
    try:
        rows_payload, report_lines = s5_privacy.run_privacy_gate(df, aggregates, meta)
    except s5_privacy.PrivacyViolation as exc:
        print(f"  BLOCKED: {exc}")
        return 1
    for line in report_lines:
        print(f"  {line}")
    s5_privacy.write_privacy_report(report_lines)

    print("[S6] Validating + writing JSON ...")
    s6_emit.emit(meta, rows_payload, aggregates, histograms)
    print(f"  wrote meta.json, rows.json, aggregates.json, histograms.json to {config.SITE_DATA_DIR}")

    print("\n=== Pipeline completed successfully ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
