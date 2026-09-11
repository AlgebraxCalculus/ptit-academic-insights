/**
 * V-07b — the ONE individual-level chart on the site. Tooltip is
 * deliberately limited to CPA, credits, and eligibility status — no track,
 * no major, no identifier of any kind (docs/architecture.md §9.2, §7.5).
 */
import { useMemo, useState } from "preact/hooks";
import { linearScale } from "../../lib/scale";
import rowsPayload from "../../data/rows.json";
import type { RowsPayload } from "../../types/data";
import { decodeRows } from "../../lib/stats";

// Imported as a static module (not an Astro prop) so Vite emits rows.json as
// ONE shared chunk fetched once, instead of serializing it separately into
// every island's HTML (docs/architecture.md §7.2, §9.2 — payload stays 2.2 KB
// gzip either way, but this avoids paying for it twice).
const rows = rowsPayload as RowsPayload;

interface Props {
  overlapBand: { lo: number; hi: number };
}

export default function CpaCreditScatter({ overlapBand }: Props) {
  const students = useMemo(() => decodeRows(rows), []);
  const [hover, setHover] = useState<{ cpa: number; credits: number; eligible: boolean; x: number; y: number } | null>(null);

  const width = 640;
  const height = 320;
  const pad = 34;

  const x = linearScale([0, 146], [pad, width - 10]);
  const y = linearScale([1.2, 3.9], [height - pad, 10]);

  const points = students.filter((s) => s.cpa !== null && s.credits !== null);

  return (
    <div class="scatter-wrap">
      <svg
        viewBox={`0 0 ${width} ${height}`}
        role="img"
        aria-label="Biểu đồ phân tán CPA theo số tín chỉ tích lũy, hai màu cho trạng thái đủ/không đủ điều kiện; vùng chồng lấn tín chỉ giữa hai nhóm được tô nổi bật."
      >
        <rect
          x={x(overlapBand.lo)}
          y={10}
          width={x(overlapBand.hi) - x(overlapBand.lo)}
          height={height - pad - 10}
          fill="var(--color-caveat-border)"
          opacity="0.12"
        />
        {points.map((s, i) => (
          <circle
            key={i}
            cx={x(s.credits!)}
            cy={y(s.cpa!)}
            r="2.6"
            fill={s.eligible ? "var(--color-cntt)" : "var(--color-cntt-clc)"}
            opacity="0.55"
            onMouseEnter={() => setHover({ cpa: s.cpa!, credits: s.credits!, eligible: s.eligible, x: x(s.credits!), y: y(s.cpa!) })}
            onMouseLeave={() => setHover(null)}
          />
        ))}
        <line x1={pad} y1={height - pad} x2={width - 10} y2={height - pad} stroke="var(--color-line-strong)" />
        <line x1={pad} y1={10} x2={pad} y2={height - pad} stroke="var(--color-line-strong)" />
        {[0, 50, 100, 146].map((t) => (
          <text key={t} x={x(t)} y={height - pad + 16} font-size="11" class="axis-label" text-anchor="middle">{t}</text>
        ))}
        {[1.5, 2.0, 2.5, 3.0, 3.5].map((t) => (
          <text key={t} x={pad - 8} y={y(t) + 4} font-size="11" class="axis-label" text-anchor="end">{t.toFixed(1)}</text>
        ))}
        {hover && (
          <g transform={`translate(${Math.min(hover.x + 10, width - 150)}, ${Math.max(hover.y - 34, 10)})`}>
            <rect width="140" height="40" fill="var(--color-surface)" stroke="var(--color-line-strong)" rx="4" />
            <text x="8" y="16" font-size="11.5" fill="var(--color-ink)">CPA {hover.cpa.toFixed(2)} · {hover.credits} TC</text>
            <text x="8" y="31" font-size="11.5" fill="var(--color-ink)">{hover.eligible ? "Đủ điều kiện" : "Không đủ điều kiện"}</text>
          </g>
        )}
      </svg>
      <div class="legend">
        <span class="legend-item"><span class="legend-swatch" style={{ background: "var(--color-cntt)" }}></span>Đủ điều kiện</span>
        <span class="legend-item"><span class="legend-swatch" style={{ background: "var(--color-cntt-clc)" }}></span>Không đủ điều kiện</span>
        <span class="legend-item"><span class="legend-swatch" style={{ background: "var(--color-caveat-border)", opacity: 0.3 }}></span>Vùng chồng lấn tín chỉ ({overlapBand.lo}–{overlapBand.hi})</span>
      </div>
    </div>
  );
}
