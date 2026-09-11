/**
 * Client-side data access and the ONLY statistics allowed to run in the
 * browser (docs/architecture.md §7.3): filtering, counting, mean/sd, a
 * normal-approximation CI, and re-binning a histogram. No bootstrap, no
 * hypothesis test, no effect size, no eta-squared — those live exclusively
 * in the pipeline and are read from aggregates.json.
 */
import type { RowsPayload } from "../types/data";

export interface StudentRow {
  track: number;
  major: number;
  cpa: number | null; // real CPA value (already /100), or null
  credits: number | null;
  eligible: boolean;
}

export function decodeRows(payload: RowsPayload): StudentRow[] {
  const out: StudentRow[] = [];
  for (let i = 0; i < payload.n; i++) {
    out.push({
      track: payload.track[i],
      major: payload.major[i],
      cpa: payload.cpa[i] === -1 ? null : payload.cpa[i] / 100,
      credits: payload.cr[i] === -1 ? null : payload.cr[i],
      eligible: payload.el[i] === 1,
    });
  }
  return out;
}

export interface QuickStats {
  n: number;
  mean: number | null;
  sd: number | null;
  ci: [number, number] | null;
  median: number | null;
  eligiblePct: number | null;
}

/** Mean/SD/normal-approx CI of a filtered subset. Explicitly an
 * approximation — the UI must label it as such, distinct from the
 * bootstrap CIs shown in the static sections. */
export function quickStats(rows: StudentRow[]): QuickStats {
  const withCpa = rows.map((r) => r.cpa).filter((v): v is number => v !== null);
  const n = rows.length;
  if (withCpa.length === 0) {
    return { n, mean: null, sd: null, ci: null, median: null, eligiblePct: null };
  }
  const mean = withCpa.reduce((a, b) => a + b, 0) / withCpa.length;
  const variance =
    withCpa.length > 1
      ? withCpa.reduce((a, b) => a + (b - mean) ** 2, 0) / (withCpa.length - 1)
      : 0;
  const sd = Math.sqrt(variance);
  const se = sd / Math.sqrt(withCpa.length);
  const sorted = [...withCpa].sort((a, b) => a - b);
  const median = sorted[Math.floor(sorted.length / 2)];
  const eligibleCount = rows.filter((r) => r.eligible).length;

  return {
    n,
    mean,
    sd,
    ci: [mean - 1.96 * se, mean + 1.96 * se],
    median,
    eligiblePct: n > 0 ? (100 * eligibleCount) / n : null,
  };
}

const BIN_WIDTH = 0.1;
const DOMAIN: [number, number] = [1.2, 3.9];

export function histogramEdges(): number[] {
  const edges: number[] = [];
  for (let x = DOMAIN[0]; x <= DOMAIN[1] + 1e-9; x += BIN_WIDTH) {
    edges.push(Math.round(x * 100) / 100);
  }
  return edges;
}

export function histogramCounts(cpaValues: number[]): number[] {
  const edges = histogramEdges();
  const counts = new Array(edges.length - 1).fill(0) as number[];
  for (const v of cpaValues) {
    for (let i = 0; i < edges.length - 1; i++) {
      if (v >= edges[i] && v < edges[i + 1]) {
        counts[i]++;
        break;
      }
    }
  }
  return counts;
}
