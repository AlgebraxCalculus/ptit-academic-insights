/**
 * V-05d — 18 classes as mean +/- 95% CI, grouped by track and ordered by
 * class name (never by mean — docs/website-spec.md §05c, CORE-8).
 *
 * A Preact island (not a static .astro component) so each point gets a real
 * hover tooltip instead of a native SVG <title> — title tooltips are
 * inconsistent across browsers, have a mandatory OS delay, and don't work
 * on touch at all.
 */
import { useState } from "preact/hooks";
import type { Aggregates } from "../../types/data";
import { trackColor } from "../../lib/colors";
import { xScale } from "../../lib/svg";

interface Props {
  rows: Aggregates["by_class"];
}

export default function ClassCaterpillar({ rows }: Props) {
  const [hover, setHover] = useState<number | null>(null);

  const width = 640;
  const rowHeight = 22;
  const height = rows.length * rowHeight + 30;
  const labelWidth = 100;

  const allValues = rows.flatMap((r) => r.ci);
  const domain = [Math.floor(Math.min(...allValues) * 10) / 10, Math.ceil(Math.max(...allValues) * 10) / 10];
  const xs = xScale(domain, width - labelWidth - 10, 0);

  const hovered = hover !== null ? rows[hover] : null;
  const hoveredCx = hovered ? labelWidth + xs(hovered.mean) : 0;
  const hoveredCy = hover !== null ? hover * rowHeight + 14 : 0;

  return (
    <figure>
      <svg
        viewBox={`0 0 ${width} ${height}`}
        role="img"
        aria-label="Biểu đồ caterpillar 18 lớp với khoảng tin cậy 95%, sắp theo chuyên ngành; các khoảng tin cậy trong cùng chuyên ngành chồng lên nhau, còn giữa các chuyên ngành thì tách rời rõ rệt."
      >
        {rows.map((r, i) => {
          const y = i * rowHeight + 14;
          const color = trackColor(r.track);
          const cx = labelWidth + xs(r.mean);
          return (
            <g key={r.class}>
              <text x={labelWidth - 8} y={y + 4} font-size="11" text-anchor="end" fill="var(--color-muted)">{r.class}</text>
              <line x1={labelWidth + xs(r.ci[0])} y1={y} x2={labelWidth + xs(r.ci[1])} y2={y} stroke={color} stroke-width="2" />
              <circle cx={cx} cy={y} r="3.5" fill={color} pointer-events="none" />
              <circle
                cx={cx}
                cy={y}
                r="9"
                fill="transparent"
                onMouseEnter={() => setHover(i)}
                onMouseLeave={() => setHover(null)}
              />
            </g>
          );
        })}
        <line x1={labelWidth} y1={height - 16} x2={width} y2={height - 16} stroke="var(--color-line-strong)" />
        {[2.0, 2.5, 3.0, 3.5]
          .filter((t) => t >= domain[0] && t <= domain[1])
          .map((t) => (
            <text key={t} x={labelWidth + xs(t)} y={height - 4} font-size="10.5" class="axis-label" text-anchor="middle">{t.toFixed(1)}</text>
          ))}

        {hovered && (
          <g transform={`translate(${Math.min(hoveredCx + 10, width - 160)}, ${Math.max(hoveredCy - 32, 4)})`}>
            <rect width="150" height="40" fill="var(--color-surface)" stroke="var(--color-line-strong)" rx="4" />
            <text x="8" y="16" font-size="11.5" fill="var(--color-ink)" font-weight="600">{hovered.class} · {hovered.mean.toFixed(2)} (n={hovered.n})</text>
            <text x="8" y="31" font-size="11.5" fill="var(--color-ink)">CI [{hovered.ci[0].toFixed(2)}, {hovered.ci[1].toFixed(2)}]</text>
          </g>
        )}
      </svg>
      <figcaption>
        Sắp theo chuyên ngành rồi theo tên lớp — không sắp theo điểm trung bình. Di chuột qua từng điểm để xem chi tiết.
      </figcaption>
    </figure>
  );
}
