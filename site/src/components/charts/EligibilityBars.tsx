/**
 * V-07a — eligibility rate with 95% CI, toggle between track and program
 * grouping. Axis intentionally starts above 0 with an explicit warning
 * label (docs/website-spec.md §07).
 */
import { useState } from "preact/hooks";
import { linearScale } from "../../lib/scale";
import type { Aggregates } from "../../types/data";
import { trackColor, programColor } from "../../lib/colors";

interface Props {
  byTrack: Aggregates["by_track"];
  byProgram: Aggregates["eligibility"]["by_program"];
  labels: { track: string; program: string };
}

export default function EligibilityBars({ byTrack, byProgram, labels }: Props) {
  const [mode, setMode] = useState<"track" | "program">("track");

  const width = 600;
  const rowHeight = 42;
  const padLeft = 110;

  const trackRows = [...byTrack].sort((a, b) => b.eligible_pct - a.eligible_pct);
  const programRows = [
    { label: "CNTT", pct: byProgram.cntt.pct, n: byProgram.cntt.n, color: programColor("CNTT") },
    { label: "CNTT CLC", pct: byProgram.clc.pct, n: byProgram.clc.n, color: programColor("CNTT CLC") },
  ];

  const rows =
    mode === "track"
      ? trackRows.map((t) => ({ label: t.track, pct: t.eligible_pct, ci: t.eligible_ci, n: t.n_rows, color: trackColor(t.track) }))
      : programRows.map((p) => ({ label: p.label, pct: p.pct, ci: null as [number, number] | null, n: p.n, color: p.color }));

  const height = rows.length * rowHeight + 20;
  const domainMin = 75;
  const x = linearScale([domainMin, 100], [0, width - padLeft - 50]);

  return (
    <div class="eligibility-bars">
      <div class="toggle-buttons" role="group" aria-label="Chọn cách nhóm">
        <button type="button" class={mode === "track" ? "active" : ""} onClick={() => setMode("track")}>{labels.track}</button>
        <button type="button" class={mode === "program" ? "active" : ""} onClick={() => setMode("program")}>{labels.program}</button>
      </div>

      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Biểu đồ cột tỷ lệ đủ điều kiện làm đồ án theo 5 chuyên ngành, D22CNPM cao nhất ở 99.4%, D22HTTT thấp nhất ở 83.5%.">
        {rows.map((r, i) => {
          const y = i * rowHeight + 10;
          return (
            <g key={r.label}>
              <text x={padLeft - 10} y={y + 18} font-size="12.5" text-anchor="end" fill="var(--color-ink)">{r.label}</text>
              <rect x={padLeft} y={y} width={x(r.pct)} height={22} fill={r.color} />
              {r.ci && (
                <line x1={padLeft + x(r.ci[0])} y1={y + 11} x2={padLeft + x(r.ci[1])} y2={y + 11} stroke="var(--color-ink)" stroke-width="1.5" opacity="0.5" />
              )}
              <text x={padLeft + x(r.pct) + 8} y={y + 17} font-size="12" font-weight="600">{r.pct.toFixed(1)}% (n={r.n})</text>
            </g>
          );
        })}
        <line x1={padLeft} y1={height - 6} x2={width - 50} y2={height - 6} stroke="var(--color-line-strong)" />
      </svg>
      <p class="footnote">⚠ Trục bắt đầu từ {domainMin}%, không từ 0%, để phân biệt các nhóm ở dải cao.</p>

      <style>{`
        .toggle-buttons { display: inline-flex; border: 1px solid var(--color-line-strong); border-radius: 999px; overflow: hidden; margin-bottom: 1rem; }
        .toggle-buttons button { padding: 0.4rem 1rem; border: none; background: var(--color-surface); color: var(--color-muted); }
        .toggle-buttons button.active { background: var(--color-cntt); color: white; }
      `}</style>
    </div>
  );
}
