/**
 * V-05b — the same CPA histogram colored two ways: by program (looks
 * almost uniform) vs by track (visibly separates). docs/website-spec.md §05.
 * Uses only the per-bin counts the pipeline already computed
 * (histograms.by_program / by_track) — no new statistic is derived here.
 */
import { useState } from "preact/hooks";
import { linearScale } from "../../lib/scale";
import type { Histograms } from "../../types/data";
import { trackColor, programColor } from "../../lib/colors";

interface Props {
  histograms: Histograms;
  labels: { program: string; track: string };
}

const TRACKS = ["D22CNPM", "D22HTTT", "E22CNPM", "E22HTTT", "E22TTNT"];
const PROGRAMS = ["CNTT", "CNTT CLC"];

export default function ColorByToggle({ histograms, labels }: Props) {
  const [mode, setMode] = useState<"program" | "track">("program");

  const width = 640;
  const height = 220;
  const padBottom = 28;
  const x = linearScale(histograms.domain, [0, width]);
  const series = mode === "program" ? PROGRAMS : TRACKS;
  const source = mode === "program" ? histograms.by_program : histograms.by_track;
  const colorFor = mode === "program" ? programColor : trackColor;

  const nBins = histograms.overall.length;
  const maxTotal = Math.max(...histograms.overall);
  const y = linearScale([0, maxTotal * 1.08], [height - padBottom, 10]);

  return (
    <div class="color-by-toggle">
      <div class="toggle-buttons" role="group" aria-label="Chọn cách tô màu">
        <button type="button" class={mode === "program" ? "active" : ""} onClick={() => setMode("program")}>
          {labels.program}
        </button>
        <button type="button" class={mode === "track" ? "active" : ""} onClick={() => setMode("track")}>
          {labels.track}
        </button>
      </div>

      <svg
        viewBox={`0 0 ${width} ${height}`}
        role="img"
        aria-label={
          mode === "program"
            ? "Histogram CPA tô theo chương trình: hai màu trộn gần như đều nhau qua toàn bộ phân phối."
            : "Histogram CPA tô theo chuyên ngành: các màu tách thành từng vùng rõ rệt theo vị trí trên trục CPA."
        }
      >
        {Array.from({ length: nBins }).map((_, i) => {
          const x0 = x(histograms.edges[i]);
          const x1 = x(histograms.edges[i + 1]);
          let cursor = height - padBottom;
          return (
            <g key={i}>
              {series.map((key) => {
                const count = source[key]?.[i] ?? 0;
                const h = (height - padBottom - 10) === 0 ? 0 : y(0) - y(count);
                if (h <= 0) return null;
                const rectY = cursor - h;
                cursor -= h;
                return (
                  <rect key={key} x={x0 + 0.5} y={rectY} width={Math.max(0, x1 - x0 - 1)} height={h} fill={colorFor(key)} opacity="0.9" />
                );
              })}
            </g>
          );
        })}
        <line x1={0} y1={height - padBottom} x2={width} y2={height - padBottom} stroke="var(--color-line-strong)" />
        {[1.5, 2.0, 2.5, 3.0, 3.5].map((t) => (
          <text key={t} x={x(t)} y={height - 8} font-size="11" class="axis-label" text-anchor="middle">{t.toFixed(1)}</text>
        ))}
      </svg>

      <div class="legend">
        {series.map((s) => (
          <span key={s} class="legend-item">
            <span class="legend-swatch" style={{ background: colorFor(s) }}></span>
            {s}
          </span>
        ))}
      </div>

      <style>{`
        .toggle-buttons { display: inline-flex; gap: 0; border: 1px solid var(--color-line-strong); border-radius: 999px; overflow: hidden; margin-bottom: 1rem; }
        .toggle-buttons button {
          padding: 0.4rem 1rem; border: none; background: var(--color-surface); color: var(--color-muted);
        }
        .toggle-buttons button.active { background: var(--color-cntt); color: white; }
      `}</style>
    </div>
  );
}
