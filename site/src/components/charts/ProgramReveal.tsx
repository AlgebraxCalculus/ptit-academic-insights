/**
 * V-04a/b/c — the three-step reveal at the heart of the site
 * (docs/website-spec.md §04): aggregate bar -> paired slope chart with CI
 * -> quantile-difference curve. Each step is its own scroll-revealed block
 * (not a pinned scrollytelling stage) so it degrades gracefully on mobile
 * and under prefers-reduced-motion.
 */
import { useEffect, useRef, useState } from "preact/hooks";
import { linearScale } from "../../lib/scale";
import type { Aggregates } from "../../types/data";

interface Props {
  aggregate: Aggregates["program_comparison"]["aggregate"];
  paired: Aggregates["program_comparison"]["paired"];
  quantileDiff: Aggregates["program_comparison"]["quantile_diff"];
  unpairedNote: Aggregates["program_comparison"]["unpaired_note"];
  copy: {
    steps: { body: string }[];
    resetLabel: string;
    caveat: string;
    footnote: string;
  };
}

function useReveal() {
  const ref = useRef<HTMLDivElement>(null);
  // Visible by default — content must never depend on JS to become visible.
  // The scroll-triggered fade is a progressive enhancement only.
  const [visible, setVisible] = useState(true);
  useEffect(() => {
    const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const el = ref.current;
    if (prefersReduced || !el || !("IntersectionObserver" in window)) return;
    setVisible(false);
    const obs = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          setVisible(true);
          obs.disconnect();
        }
      },
      { threshold: 0.3 }
    );
    obs.observe(el);
    // Safety net: never leave content permanently hidden if the observer
    // never fires for some reason.
    const fallback = window.setTimeout(() => setVisible(true), 2500);
    return () => {
      obs.disconnect();
      window.clearTimeout(fallback);
    };
  }, []);
  return { ref, visible };
}

function BarStep({ aggregate }: { aggregate: Props["aggregate"] }) {
  const width = 480;
  const height = 140;
  const x = linearScale([2.4, 3.1], [0, width - 100]);
  const bars = [
    { label: "CNTT", value: aggregate.cntt.mean, n: aggregate.cntt.n, color: "var(--color-cntt)" },
    { label: "CNTT CLC", value: aggregate.clc.mean, n: aggregate.clc.n, color: "var(--color-cntt-clc)" },
  ];
  return (
    <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Hai thanh: CNTT 2.77 và CNTT CLC 2.87.">
      {bars.map((b, i) => (
        <g key={b.label} transform={`translate(80, ${i * 55 + 20})`}>
          <text x={-8} y={16} font-size="13" text-anchor="end" fill="var(--color-ink)">{b.label}</text>
          <rect x={0} y={0} width={x(b.value)} height={28} fill={b.color} />
          <text x={x(b.value) + 8} y={19} font-size="13" font-weight="600">{b.value.toFixed(3)} (n={b.n})</text>
        </g>
      ))}
      <text x={80} y={height - 6} font-size="13" font-weight="600" fill="var(--color-ink)">
        Chênh lệch gộp: {aggregate.diff > 0 ? "+" : ""}{aggregate.diff.toFixed(3)}
      </text>
    </svg>
  );
}

function SlopeStep({ paired }: { paired: Props["paired"] }) {
  const width = 480;
  const height = 220;
  const y = linearScale([2.3, 3.15], [height - 30, 20]);
  const colX = { cntt: 90, clc: width - 90 };

  return (
    <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Biểu đồ đường dốc hai đường: cặp CNPM dốc xuống từ 3.02 xuống 2.76; cặp HTTT dốc lên từ 2.48 lên 2.92.">
      <text x={colX.cntt} y={12} font-size="11.5" text-anchor="middle" fill="var(--color-muted)">CNTT</text>
      <text x={colX.clc} y={12} font-size="11.5" text-anchor="middle" fill="var(--color-muted)">CNTT CLC</text>
      {paired.map((p) => {
        const color = p.diff < 0 ? "var(--color-cntt)" : "var(--color-cntt-clc)";
        const y0 = y(p.cntt.mean);
        const y1 = y(p.clc.mean);
        return (
          <g key={p.pair}>
            <line x1={colX.cntt} y1={y0} x2={colX.clc} y2={y1} stroke={color} stroke-width="2.5" />
            <line x1={colX.cntt} y1={y(p.cntt.mean - 1.96 * (p.cntt.sd / Math.sqrt(p.cntt.n)))} x2={colX.cntt} y2={y(p.cntt.mean + 1.96 * (p.cntt.sd / Math.sqrt(p.cntt.n)))} stroke={color} stroke-width="4" opacity="0.35" />
            <line x1={colX.clc} y1={y(p.clc.mean - 1.96 * (p.clc.sd / Math.sqrt(p.clc.n)))} x2={colX.clc} y2={y(p.clc.mean + 1.96 * (p.clc.sd / Math.sqrt(p.clc.n)))} stroke={color} stroke-width="4" opacity="0.35" />
            <circle cx={colX.cntt} cy={y0} r="4" fill={color} />
            <circle cx={colX.clc} cy={y1} r="4" fill={color} />
            <text x={colX.cntt - 8} y={y0 + 4} font-size="12" text-anchor="end" fill="var(--color-ink)">{p.cntt.mean.toFixed(2)}</text>
            <text x={colX.clc + 8} y={y1 + 4} font-size="12" fill="var(--color-ink)">{p.clc.mean.toFixed(2)}</text>
            <text x={width / 2} y={(y0 + y1) / 2 - 6} font-size="12" font-weight="600" text-anchor="middle" fill={color}>
              {p.pair}: {p.diff > 0 ? "+" : ""}{p.diff.toFixed(3)}
            </text>
          </g>
        );
      })}
    </svg>
  );
}

function QuantileStep({ quantileDiff }: { quantileDiff: Props["quantileDiff"] }) {
  const width = 480;
  const height = 180;
  const x = linearScale([0, 100], [30, width - 10]);
  const maxAbs = Math.max(...quantileDiff.map((q) => Math.abs(q.diff)));
  const y = linearScale([-maxAbs * 1.1, maxAbs * 1.1], [height - 20, 15]);
  const points = quantileDiff.map((q) => `${x(q.q)},${y(q.diff)}`).join(" ");
  return (
    <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Biểu đồ chênh lệch theo phân vị: đường cong cao ở hai đầu, gần bằng 0 ở giữa phân phối.">
      <line x1={30} y1={y(0)} x2={width - 10} y2={y(0)} stroke="var(--color-line-strong)" />
      <polyline points={points} fill="none" stroke="var(--color-cntt-clc)" stroke-width="2.5" />
      {quantileDiff.map((q) => (
        <circle key={q.q} cx={x(q.q)} cy={y(q.diff)} r="2.5" fill="var(--color-cntt-clc)" />
      ))}
      <text x={30} y={height - 4} font-size="10.5" fill="var(--color-muted)">p0</text>
      <text x={width - 10} y={height - 4} font-size="10.5" text-anchor="end" fill="var(--color-muted)">p100</text>
      <text x={x(50)} y={y(0) - 8} font-size="10.5" text-anchor="middle" fill="var(--color-muted)">CLC = CNTT</text>
    </svg>
  );
}

export default function ProgramReveal({ aggregate, paired, quantileDiff, copy }: Props) {
  const step1 = useReveal();
  const step2 = useReveal();
  const step3 = useReveal();
  const containerRef = useRef<HTMLDivElement>(null);

  return (
    <div ref={containerRef} class="program-reveal">
      <div ref={step1.ref} class={`reveal-step ${step1.visible ? "is-visible" : ""}`}>
        <BarStep aggregate={aggregate} />
        <p>{copy.steps[0].body}</p>
      </div>

      <div ref={step2.ref} class={`reveal-step ${step2.visible ? "is-visible" : ""}`}>
        <SlopeStep paired={paired} />
        <p>{copy.steps[1].body}</p>
        <div class="caveat caveat--critical" role="note">
          <p>{copy.caveat}</p>
        </div>
      </div>

      <div ref={step3.ref} class={`reveal-step ${step3.visible ? "is-visible" : ""}`}>
        <QuantileStep quantileDiff={quantileDiff} />
        <p>{copy.steps[2].body}</p>
        <p class="footnote">{copy.footnote}</p>
      </div>

      <button
        type="button"
        class="link-toggle"
        onClick={() => containerRef.current?.scrollIntoView({ behavior: "smooth", block: "start" })}
      >
        {copy.resetLabel}
      </button>

      <style>{`
        .program-reveal { display: flex; flex-direction: column; gap: 3rem; }
        .reveal-step {
          opacity: 0;
          transform: translateY(16px);
          transition: opacity 0.5s ease, transform 0.5s ease;
        }
        .reveal-step.is-visible { opacity: 1; transform: translateY(0); }
        @media (prefers-reduced-motion: reduce) {
          .reveal-step { transition: none; transform: none; opacity: 1; }
        }
      `}</style>
    </div>
  );
}
