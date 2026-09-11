/**
 * Small SVG-building helpers shared by the static chart components. These
 * run at build time inside Astro's Node renderer, not in the browser — the
 * output is plain markup, so static charts ship with zero client JS
 * (docs/architecture.md §7.1, §7.2).
 *
 * These functions only ever reshape numbers the pipeline already computed
 * (histogram counts, group means, CIs) into screen coordinates. They never
 * derive a new statistic — that boundary belongs to the pipeline.
 */
import { line, curveMonotoneX, area } from "d3-shape";
import { linearScale, type Scale } from "./scale";

export function xScale(domain: number[], width: number, padding = 0): Scale {
  return linearScale(domain, [padding, width - padding]);
}

export function yScale(domain: number[], height: number, padding = 0): Scale {
  return linearScale(domain, [height - padding, padding]);
}

export interface Point {
  x: number;
  y: number;
}

export function smoothLinePath(points: Point[]): string {
  const gen = line<Point>()
    .x((d) => d.x)
    .y((d) => d.y)
    .curve(curveMonotoneX);
  return gen(points) ?? "";
}

export function smoothAreaPath(points: Point[], baseline: number): string {
  const gen = area<Point>()
    .x((d) => d.x)
    .y0(baseline)
    .y1((d) => d.y)
    .curve(curveMonotoneX);
  return gen(points) ?? "";
}

export interface HistBar {
  x: number;
  y: number;
  width: number;
  height: number;
  count: number;
  binLabel: string;
}

/** Turn (edges, counts) — exactly the shape histograms.json stores — into
 * screen-space bar rectangles. */
export function histogramBars(
  edges: number[],
  counts: number[],
  xs: (v: number) => number,
  ys: (v: number) => number,
  chartHeight: number,
  gap = 1
): HistBar[] {
  const bars: HistBar[] = [];
  for (let i = 0; i < counts.length; i++) {
    const x0 = xs(edges[i]);
    const x1 = xs(edges[i + 1]);
    const y = ys(counts[i]);
    bars.push({
      x: x0 + gap / 2,
      y,
      width: Math.max(0, x1 - x0 - gap),
      height: chartHeight - y,
      count: counts[i],
      binLabel: `${edges[i].toFixed(1)}–${edges[i + 1].toFixed(1)}`,
    });
  }
  return bars;
}

/** Density curve points from raw bin counts (normalized so the area sums to
 * 1), smoothed with a monotone curve through bin midpoints. This is a
 * frequency-polygon smoothing of the pipeline's own histogram bins, not a
 * newly-fit statistical model. */
export function densityPoints(
  edges: number[],
  counts: number[],
  xs: (v: number) => number,
  ys: (v: number) => number
): Point[] {
  const n = counts.reduce((a, b) => a + b, 0);
  const binWidth = edges[1] - edges[0];
  return counts.map((c, i) => {
    const mid = (edges[i] + edges[i + 1]) / 2;
    const density = n > 0 ? c / (n * binWidth) : 0;
    return { x: xs(mid), y: ys(density) };
  });
}
