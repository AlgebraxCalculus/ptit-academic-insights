/**
 * Shared color tokens — docs/website-spec.md §5.1: one color per program,
 * five distinguishable shades for tracks, gray for context/background.
 * Kept as a single source so charts and CSS agree. Values also declared as
 * CSS custom properties in styles/tokens.css; this module exists for
 * server-rendered SVG (Astro components run in Node, not the browser, so
 * they cannot read CSS variables at build time).
 */

export const PROGRAM_COLOR: Record<string, string> = {
  CNTT: "#3b6ea5",
  "CNTT CLC": "#c0703c",
};

export const TRACK_COLOR: Record<string, string> = {
  D22CNPM: "#3b6ea5",
  D22HTTT: "#7fa8d1",
  E22CNPM: "#c0703c",
  E22HTTT: "#d99b6f",
  E22TTNT: "#8a4a2a",
};

export const NEUTRAL = {
  ink: "#1f2933",
  muted: "#6b7785",
  line: "#d7dce1",
  bg: "#f7f5f2",
};

export function trackColor(track: string): string {
  return TRACK_COLOR[track] ?? NEUTRAL.muted;
}

export function programColor(program: string): string {
  return PROGRAM_COLOR[program] ?? NEUTRAL.muted;
}
