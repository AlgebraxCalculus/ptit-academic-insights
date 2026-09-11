/**
 * V-08 — self-serve filtering over the same 905 rows every static number on
 * the site comes from. Filtering, counting, and a normal-approx CI are the
 * only client-side statistics allowed here (docs/architecture.md §7.3).
 *
 * Privacy: no birthplace/birth-year filter, no student search, no
 * class_code in the filtered row data — class selection only overlays a
 * pre-computed aggregate marker (docs/architecture.md §9.2).
 */
import { useEffect, useMemo, useState } from "preact/hooks";
import { linearScale } from "../../lib/scale";
import rowsPayload from "../../data/rows.json";
import type { Aggregates, Meta, RowsPayload } from "../../types/data";
import { decodeRows, histogramCounts, histogramEdges, quickStats, type StudentRow } from "../../lib/stats";
import { isSuppressed, isSmallSample } from "../../lib/guards";
import { trackColor } from "../../lib/colors";
import { fmtCpa, fmtPct, majorLabel } from "../../lib/format";

// Same static-import trick as CpaCreditScatter.tsx: rows.json becomes one
// shared Vite chunk instead of a prop serialized into the page HTML twice.
const rows = rowsPayload as RowsPayload;

interface Props {
  meta: Meta;
  byClass: Aggregates["by_class"];
  overallHistogram: number[];
  copy: {
    filters: Record<string, string>;
    resetLabel: string;
    quickEstimateLabel: string;
    suppressedMessage: string;
    smallSampleMessage: string;
    classOverlayNote: string;
    caveat: string;
  };
}

const CREDIT_BUCKETS: { id: string; label: string; test: (c: number | null) => boolean }[] = [
  { id: "all", label: "Tất cả", test: () => true },
  { id: "146", label: "146 (trần)", test: (c) => c === 146 },
  { id: "143-145", label: "143–145", test: (c) => c !== null && c >= 143 && c <= 145 },
  { id: "131-142", label: "131–142", test: (c) => c !== null && c >= 131 && c <= 142 },
  { id: "101-130", label: "101–130", test: (c) => c !== null && c >= 101 && c <= 130 },
  { id: "le100", label: "≤ 100", test: (c) => c !== null && c <= 100 },
];

const ELIGIBLE_MAJORS = ["DCCN", "DCVT", "DCDT", "DCAT"]; // n >= 20 within scope

function readParams(): URLSearchParams {
  if (typeof window === "undefined") return new URLSearchParams();
  return new URLSearchParams(window.location.search);
}

function writeParams(params: Record<string, string>) {
  if (typeof window === "undefined") return;
  const usp = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v && v !== "all") usp.set(k, v);
  }
  const qs = usp.toString();
  const url = qs ? `${window.location.pathname}?${qs}` : window.location.pathname;
  window.history.replaceState(null, "", url + "#explore");
}

export default function ExplorePanel({ meta, byClass, overallHistogram, copy }: Props) {
  const students = useMemo(() => decodeRows(rows), [rows]);
  const trackNames = meta.dictionaries.track;
  const majorNames = meta.dictionaries.major;

  const initial = readParams();
  const [program, setProgram] = useState(initial.get("program") ?? "all");
  const [track, setTrack] = useState(initial.get("track") ?? "all");
  const [eligibility, setEligibility] = useState(initial.get("elig") ?? "all");
  const [creditBucket, setCreditBucket] = useState(initial.get("credits") ?? "all");
  const [selectedMajors, setSelectedMajors] = useState<Set<string>>(new Set(ELIGIBLE_MAJORS));
  const [cpaMin, setCpaMin] = useState(1.4);
  const [cpaMax, setCpaMax] = useState(3.8);
  const [overlayClass, setOverlayClass] = useState("none");

  useEffect(() => {
    writeParams({ program, track, elig: eligibility, credits: creditBucket });
  }, [program, track, eligibility, creditBucket]);

  const filtered: StudentRow[] = useMemo(() => {
    const bucket = CREDIT_BUCKETS.find((b) => b.id === creditBucket) ?? CREDIT_BUCKETS[0];
    return students.filter((s) => {
      const tName = trackNames[s.track];
      const mName = majorNames[s.major];
      const isClc = tName.startsWith("E22");
      if (program === "CNTT" && isClc) return false;
      if (program === "CNTT CLC" && !isClc) return false;
      if (track !== "all" && tName !== track) return false;
      if (eligibility === "eligible" && !s.eligible) return false;
      if (eligibility === "ineligible" && s.eligible) return false;
      if (!bucket.test(s.credits)) return false;
      if (ELIGIBLE_MAJORS.includes(mName) && !selectedMajors.has(mName)) return false;
      if (s.cpa !== null && (s.cpa < cpaMin || s.cpa > cpaMax)) return false;
      return true;
    });
  }, [students, program, track, eligibility, creditBucket, selectedMajors, cpaMin, cpaMax, trackNames, majorNames]);

  const stats = quickStats(filtered);
  const suppressed = isSuppressed(stats.n);
  const small = isSmallSample(stats.n);

  const cpaValues = filtered.map((s) => s.cpa).filter((v): v is number => v !== null);
  const counts = suppressed ? [] : histogramCounts(cpaValues);
  const edges = histogramEdges();

  const width = 640;
  const height = 240;
  const padBottom = 26;
  const x = linearScale([edges[0], edges[edges.length - 1]], [0, width]);
  const maxOverall = Math.max(...overallHistogram);
  const y = linearScale([0, maxOverall * 1.1], [height - padBottom, 10]);

  const overlay = byClass.find((c) => c.class === overlayClass);

  function reset() {
    setProgram("all");
    setTrack("all");
    setEligibility("all");
    setCreditBucket("all");
    setSelectedMajors(new Set(ELIGIBLE_MAJORS));
    setCpaMin(1.4);
    setCpaMax(3.8);
    setOverlayClass("none");
  }

  return (
    <div class="explore-panel">
      <div class="caveat" role="note">
        <p>{copy.caveat}</p>
      </div>

      <div class="filters">
        <label>
          {copy.filters.program}
          <select value={program} onChange={(e) => setProgram((e.target as HTMLSelectElement).value)}>
            <option value="all">Tất cả</option>
            <option value="CNTT">CNTT</option>
            <option value="CNTT CLC">CNTT CLC</option>
          </select>
        </label>

        <label>
          {copy.filters.track}
          <select value={track} onChange={(e) => setTrack((e.target as HTMLSelectElement).value)}>
            <option value="all">Tất cả</option>
            {trackNames.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </label>

        <label>
          {copy.filters.eligibility}
          <select value={eligibility} onChange={(e) => setEligibility((e.target as HTMLSelectElement).value)}>
            <option value="all">Tất cả</option>
            <option value="eligible">Đủ điều kiện</option>
            <option value="ineligible">Không đủ điều kiện</option>
          </select>
        </label>

        <label>
          {copy.filters.creditBucket}
          <select value={creditBucket} onChange={(e) => setCreditBucket((e.target as HTMLSelectElement).value)}>
            {CREDIT_BUCKETS.map((b) => (
              <option key={b.id} value={b.id}>{b.label}</option>
            ))}
          </select>
        </label>

        <fieldset class="major-filter">
          <legend>{copy.filters.major}</legend>
          {ELIGIBLE_MAJORS.map((m) => (
            <label class="checkbox-label" key={m}>
              <input
                type="checkbox"
                checked={selectedMajors.has(m)}
                onChange={(e) => {
                  const next = new Set(selectedMajors);
                  if ((e.target as HTMLInputElement).checked) next.add(m);
                  else next.delete(m);
                  setSelectedMajors(next);
                }}
              />
              {majorLabel(m)}
            </label>
          ))}
        </fieldset>

        <div class="cpa-range">
          <span>{copy.filters.cpaRange}: {fmtCpa(cpaMin)} – {fmtCpa(cpaMax)}</span>
          <input type="range" min="1.4" max="3.8" step="0.05" value={cpaMin} onInput={(e) => setCpaMin(Math.min(Number((e.target as HTMLInputElement).value), cpaMax - 0.05))} />
          <input type="range" min="1.4" max="3.8" step="0.05" value={cpaMax} onInput={(e) => setCpaMax(Math.max(Number((e.target as HTMLInputElement).value), cpaMin + 0.05))} />
        </div>

        <label>
          Xem lớp của bạn (chỉ hiển thị điểm trung bình)
          <select value={overlayClass} onChange={(e) => setOverlayClass((e.target as HTMLSelectElement).value)}>
            <option value="none">— không chọn —</option>
            {byClass.map((c) => (
              <option key={c.class} value={c.class}>{c.class}</option>
            ))}
          </select>
        </label>

        <button type="button" class="link-toggle" onClick={reset}>{copy.resetLabel}</button>
      </div>

      {overlayClass !== "none" && <p class="footnote">{copy.classOverlayNote}</p>}

      {suppressed ? (
        <div class="caveat caveat--critical" role="status">
          <p>{copy.suppressedMessage.replace("{n}", String(stats.n))}</p>
        </div>
      ) : (
        <>
          <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Histogram CPA của nhóm đã lọc, so với toàn bộ 903 sinh viên làm nền.">
            {overallHistogram.map((c, i) => {
              const x0 = x(edges[i]);
              const x1 = x(edges[i + 1]);
              const yy = y(c);
              return <rect key={`bg-${i}`} x={x0 + 0.5} y={yy} width={Math.max(0, x1 - x0 - 1)} height={height - padBottom - yy} fill="var(--color-line)" />;
            })}
            {counts.map((c, i) => {
              const x0 = x(edges[i]);
              const x1 = x(edges[i + 1]);
              const yy = y(c);
              return <rect key={`fg-${i}`} x={x0 + 0.5} y={yy} width={Math.max(0, x1 - x0 - 1)} height={height - padBottom - yy} fill="var(--color-cntt-clc)" opacity="0.85" />;
            })}
            {overlay && (
              <g>
                <rect x={x(overlay.ci[0])} y={10} width={x(overlay.ci[1]) - x(overlay.ci[0])} height={height - padBottom - 10} fill={trackColor(overlay.track)} opacity="0.15" />
                <line x1={x(overlay.mean)} y1={10} x2={x(overlay.mean)} y2={height - padBottom} stroke={trackColor(overlay.track)} stroke-width="2" />
                <text x={x(overlay.mean) + 4} y={20} font-size="11" fill={trackColor(overlay.track)} font-weight="600">
                  {overlay.class} · {overlay.mean.toFixed(2)}
                </text>
              </g>
            )}
            <line x1={0} y1={height - padBottom} x2={width} y2={height - padBottom} stroke="var(--color-line-strong)" />
            {[1.5, 2.0, 2.5, 3.0, 3.5].map((t) => (
              <text key={t} x={x(t)} y={height - 8} font-size="11" class="axis-label" text-anchor="middle">{t.toFixed(1)}</text>
            ))}
          </svg>

          <dl class="summary-row">
            <div><dt>n</dt><dd>{stats.n}</dd></div>
            <div><dt>Mean ({copy.quickEstimateLabel})</dt><dd>{stats.mean !== null ? fmtCpa(stats.mean) : "—"}</dd></div>
            <div><dt>CI 95% ({copy.quickEstimateLabel})</dt><dd>{stats.ci ? `[${fmtCpa(stats.ci[0])}, ${fmtCpa(stats.ci[1])}]` : "—"}</dd></div>
            <div><dt>Median</dt><dd>{stats.median !== null ? fmtCpa(stats.median) : "—"}</dd></div>
            <div><dt>SD</dt><dd>{stats.sd !== null ? stats.sd.toFixed(3) : "—"}</dd></div>
            <div><dt>Đủ điều kiện</dt><dd>{stats.eligiblePct !== null ? fmtPct(stats.eligiblePct) : "—"}</dd></div>
          </dl>
          {small && <p class="footnote">{copy.smallSampleMessage}</p>}
        </>
      )}

      <style>{`
        .explore-panel { display: flex; flex-direction: column; gap: 1rem; }
        .filters { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 1rem; align-items: end; }
        .filters label { display: flex; flex-direction: column; gap: 0.3rem; font-size: 0.85rem; color: var(--color-muted); }
        .filters select { padding: 0.4rem; border-radius: 4px; border: 1px solid var(--color-line-strong); background: var(--color-surface); color: var(--color-ink); }
        .major-filter { border: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 0.2rem; }
        .major-filter legend { font-size: 0.85rem; color: var(--color-muted); padding: 0; }
        .checkbox-label { flex-direction: row !important; align-items: center; gap: 0.4rem !important; font-size: 0.85rem; }
        .cpa-range { display: flex; flex-direction: column; gap: 0.2rem; font-size: 0.85rem; color: var(--color-muted); grid-column: span 2; }
        .summary-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(110px, 1fr)); gap: 1rem; margin: 0; }
        .summary-row dt { font-size: 0.78rem; color: var(--color-muted); }
        .summary-row dd { margin: 0.15rem 0 0; font-size: 1.05rem; font-weight: 600; font-variant-numeric: tabular-nums; }
      `}</style>
    </div>
  );
}
