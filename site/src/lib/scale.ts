/**
 * A minimal linear scale — the only scale behavior this project ever uses:
 * a domain -> range mapping, called as a function. No color interpolation,
 * no .nice(), no .ticks() (every axis tick set on this site is a fixed,
 * hand-chosen array, not dynamically generated).
 *
 * Replaces d3-scale's scaleLinear(), which pulls in d3-interpolate and
 * d3-color internally even for plain numeric domains — a measured ~7.7 KB
 * gzip of functionality this project never exercises. This function is
 * behavior-identical to `scaleLinear().domain(domain).range(range)` for the
 * unclamped, non-nice()'d numeric case used everywhere on this site.
 */
export type Scale = (value: number) => number;

// Domain/range are typed as number[] rather than a strict [number, number]
// tuple because callers often pass an array parsed from JSON (e.g.
// histograms.json's `domain` field), which TypeScript infers as number[],
// not a tuple. Only indices 0 and 1 are ever read.
export function linearScale(domain: number[], range: number[]): Scale {
  const [d0, d1] = domain;
  const [r0, r1] = range;
  const span = d1 - d0;
  return (value: number) => (span === 0 ? r0 : r0 + ((value - d0) / span) * (r1 - r0));
}
