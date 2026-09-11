/**
 * Number formatting rules — docs/website-spec.md §4.
 * All display formatting goes through here so the rules are enforced in one
 * place rather than re-implemented (and drifted) per component.
 */

/** CPA always 2 decimal places, matching the source data's precision. */
export function fmtCpa(value: number): string {
  return value.toFixed(2);
}

/** A signed CPA difference, 3 decimal places, always with a sign. */
export function fmtCpaDiff(value: number): string {
  const sign = value > 0 ? "+" : value < 0 ? "−" : "±";
  return `${sign}${Math.abs(value).toFixed(3)}`;
}

/** Percentage, 1 decimal place by default (2 allowed in detail tables). */
export function fmtPct(value: number, decimals: 1 | 2 = 1): string {
  return `${value.toFixed(decimals)}%`;
}

/** A rate that must always carry its denominator: "86.5% (186/215)". */
export function fmtRateWithN(pct: number, k: number, n: number, decimals: 1 | 2 = 1): string {
  return `${fmtPct(pct, decimals)} (${k}/${n})`;
}

/** p-values: "< 0.001" when very small, else 4 significant figures. */
export function fmtP(p: number): string {
  if (p < 0.001) return "p < 0.001";
  return `p = ${p.toFixed(4)}`;
}

export function fmtCi(ci: [number, number], fmt: (v: number) => string = fmtCpa): string {
  return `[${fmt(ci[0])}, ${fmt(ci[1])}]`;
}

export function fmtN(n: number): string {
  return `n = ${n.toLocaleString("vi-VN")}`;
}

export function fmtEffectSize(d: number): string {
  return d.toFixed(3);
}

const TRACK_LABELS: Record<string, string> = {
  D22CNPM: "D22CNPM — Công nghệ phần mềm (CNTT)",
  D22HTTT: "D22HTTT — Hệ thống thông tin (CNTT)",
  E22CNPM: "E22CNPM — Công nghệ phần mềm (CNTT CLC)",
  E22HTTT: "E22HTTT — Hệ thống thông tin (CNTT CLC)",
  E22TTNT: "E22TTNT — Trí tuệ nhân tạo (CNTT CLC)",
};

export function trackLabel(track: string): string {
  return TRACK_LABELS[track] ?? track;
}

const MAJOR_LABELS: Record<string, string> = {
  DCCN: "Công nghệ thông tin",
  DCVT: "Viễn thông",
  DCDT: "Điện tử",
  DCAT: "An toàn thông tin",
  DCKH: "Khoa học máy tính",
  DCCI: "Khác (DCCI)",
  DCDK: "Khác (DCDK)",
};

export function majorLabel(code: string): string {
  return MAJOR_LABELS[code] ?? code;
}
