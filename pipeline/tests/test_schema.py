"""The four emitted JSON files validate against their JSON Schemas."""
from __future__ import annotations

import s4_metrics
import s5_privacy
import s6_emit


def test_emitted_artifacts_validate(scoped_df):
    aggregates = s4_metrics.compute_all(scoped_df)
    histograms = s4_metrics.compute_histograms(scoped_df)
    meta = s6_emit.build_meta(scoped_df, 2023, "0" * 64)
    rows, _report = s5_privacy.run_privacy_gate(scoped_df, aggregates, meta)

    # raises jsonschema.ValidationError on failure
    s6_emit.validate(meta, "meta.schema.json")
    s6_emit.validate(rows, "rows.schema.json")
    s6_emit.validate(aggregates, "aggregates.schema.json")
    s6_emit.validate(histograms, "histograms.schema.json")
