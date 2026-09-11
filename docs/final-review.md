# Final Review — PTIT Academic Insights

**Phase:** 5 — Senior review (data/statistics/privacy/UX/performance), production build, deployment
**Date:** 2026-09-11
**Reviewer role:** data analyst, statistician, frontend engineer, UX reviewer, security/privacy reviewer
**Status:** Live in production. See §7 for the URL.

This document is the final sign-off. It records what was checked, what was
found, what was fixed (in the code, not just noted), and what remains a
known limitation. Read alongside `docs/data-audit.md` (Phase 1),
`docs/insight-discovery.md` (Phase 2), `docs/website-spec.md` (Phase 3), and
`docs/architecture.md` (Phase 4) — this review does not repeat their content,
only what changed because of it.

---

## 1. Final architecture

Unchanged from `docs/architecture.md` in shape; two dependency-level
corrections came out of this review (§5):

```
data/raw/*.xlsx (never committed)
        │
        ▼
pipeline/  (Python, uv-managed, run locally by a person with data access)
  s1_ingest → s2_clean → s3_scope → s4_metrics → s5_privacy (gate) → s6_emit
        │
        ▼
site/src/data/{meta,rows,aggregates,histograms}.json  (anonymized, committed)
        │
        ▼
site/  (Astro 7, static output, TypeScript strict, Preact islands)
  11 sections, 5 hydrated islands, rest zero-JS
  charts: hand-rolled SVG via a ~10-line linear scale + d3-shape curves
        │
        ▼
Vercel (static hosting) ── production URL in §7
```

**What changed in this phase:**

| Area | Before | After | Why |
|---|---|---|---|
| Scaling | `d3-scale`'s `scaleLinear()` | 10-line hand-rolled `linearScale()` (`site/src/lib/scale.ts`) | `scaleLinear` pulls in `d3-interpolate`/`d3-color` for color-space interpolation and `.ticks()` generation, neither ever used here (`.ticks()` was confirmed dead code). Measured cost removed: **7.7 KB gzip**. Behavior-identical for the unclamped numeric case used everywhere on this site — verified by diffing rendered numbers before/after (§3). |
| Dependencies | `d3-scale`, `d3-array`, their `@types` packages | removed entirely | `d3-array` was never imported anywhere in `src/` — dead dependency. `d3-scale` replaced as above. `d3-shape` (line/area/curveMonotoneX) is kept — genuinely used for the density curves and has no comparably-small substitute. |
| Source maps | relied on Vite's default (off) | explicit `sourcemap: false` in `astro.config.mjs` | A security guarantee should be a stated configuration, not an inherited default that could flip silently on a future Vite/Astro upgrade. |
| HTTP security headers | described in `architecture.md` §8.4, never implemented | `site/vercel.json` sets `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy` | These three headers **cannot** be delivered via the `<meta http-equiv>` CSP tag already in `BaseLayout.astro` — they require real HTTP response headers. Verified live in production (§4.4). |
| SVG responsiveness | no global rule | `svg { width:100%; height:auto; max-width:100% }` in `global.css` | Every chart is an inline `<svg viewBox="...">` with no `width`/`height` attribute. Without this rule, SVGs do not scale to their container on narrow viewports — a real, previously-unnoticed mobile bug affecting all 16 charts. |
| Heading hierarchy | two `<h2>` inside section 05's `<section>` landmark | changed to `<h3>` with ids `track-pair`/`track-classes` | Minor semantic/accessibility correction — 05b and 05c are narrative sub-beats of §05's argument, not new top-level sections. |
| Favicon | none | `site/public/favicon.svg` | Avoids a default 404 request for `/favicon.ico` on every page view; trivial but free. |
| Copy voice | Formal/academic phrasing in several places (e.g. self-referential lines like "this is the most important caveat in the project") | Rewritten throughout `copy.json` to read as a person explaining data, not an AI narrating its own hedges | Same numbers, same caveats, same refusal to overclaim — only the sentences changed. No factual content was softened; re-verified against §3.2's fixed figures after the rewrite. |

---

## 2. Final insight list

No insight was added, removed, or reworded in substance during this phase —
the brief for this review explicitly excluded revisiting the analytical
concept. The 8 core + 10 supporting insights from `insight-discovery.md`
stand as published. **Two presentation-layer transcription errors** were
found and corrected (§3.2) — both were copy mistakes made when hand-writing
prose in Phase 3/6, not analytical errors in the pipeline itself, which was
never wrong.

| # | Insight (unchanged) | Site section |
|---|---|---|
| CORE-1 | Program explains 1.1% of CPA variance; track explains 34.5% | §05 |
| CORE-2 | Program-vs-CLC gap reverses sign when paired by track (Simpson's paradox) | §04 |
| CORE-3 | CNPM/HTTT gap (0.535) shows floor-truncation evidence of rank-based track assignment | §05b |
| CORE-4 | Overall CPA distribution: mean 2.79, IQR 0.59 | §02, §03 |
| CORE-5 | CLC's edge is concentrated in the lower tail, not the top | §04 (step 3) |
| CORE-6 | Eligibility gap is 15.9pp between tracks, ~0 between programs | §07 |
| CORE-7 | CPA does not fully determine thesis eligibility | §07 |
| CORE-8 | Classes within a track are statistically indistinguishable — no class ranking | §05c |
| SUP-1–10 | (E22TTNT extremity, admission-major composition, etc.) | §06, §07 panel, §09 |

**Chart/section necessity re-examined** (explicit ask: remove anything
without analytical value):

- All 16 chart components were checked against the specific insight they
  exist to support. None were found to lack a tied finding; none were removed.
- `DensityRidge` (hero background) is the one deliberately non-analytical
  element on the page — pure decoration, `aria-hidden`, no labels, no claim.
  Kept: it supports the "explore the data" first impression the UX brief
  asks for, and because it's marked `aria-hidden` and makes no assertion, it
  carries none of the misinterpretation risk a real, unlabeled chart would.
- `CompositionBars` vs. `MajorDotPlot` (§06) were checked for redundancy:
  they answer different questions (*who is in each program* vs. *does
  admission major predict CPA within CLC*) — both retained.
  `EligibilityBars` vs. `CpaCreditScatter` (§07) likewise cover CORE-6 and
  CORE-7 respectively — both retained.

---

## 3. Validation result

### 3.1 Row/group/program/cohort counts — pipeline vs. shipped JSON vs. docs

All values below were re-derived independently from `site/src/data/*.json`
after the final pipeline run and cross-checked against `data-audit.md` and
`insight-discovery.md`.

| Metric | Expected (docs) | `meta.json` / `aggregates.json` | Match |
|---|---:|---:|---|
| Raw rows | 2,023 | `source_rows_total: 2023` | ✅ |
| In-scope rows | 905 | `n_in_scope: 905` | ✅ |
| Rows with CPA | 903 | `n_with_cpa: 903` | ✅ |
| Classes | 18 | `n_classes: 18` | ✅ |
| Tracks | 5 | `n_tracks: 5` | ✅ |
| Programs | 2 | `n_programs: 2` | ✅ |
| CNTT / CNTT CLC | 690 / 215 | `composition.by_program` totals 690 / 215 | ✅ |
| Cohort 2022 / 2021 | 899 / 6 | `meta.cohort: {"2022":899,"2021":6}` | ✅ |
| CPA min / max | 1.40 / 3.72 | `overall.min: 1.4, overall.max: 3.72` | ✅ |
| Overall mean | 2.7915 | `overall.mean: 2.7915` | ✅ |
| IQR | 0.59 | `overall.iqr: 0.59` | ✅ |
| Bands (Xuất sắc…Yếu) | 20/157/516/169/41 | same | ✅ |
| η²(program) / η²(track) | 0.0109 / 0.3448 | same | ✅ |
| Aggregate program diff | +0.1057 | `program_comparison.aggregate.diff: 0.1057` | ✅ |
| Paired CNPM / HTTT diff | −0.2639 / +0.4325 | same | ✅ |
| CNPM min / truncation | 2.43, 0 below | `track_contrast.cnpm_vs_httt.truncation` matches | ✅ |
| Eligibility CNPM/HTTT | 99.45% / 83.54% | `by_track[D22CNPM].eligible_pct` etc. match | ✅ |
| Eligibility by program | 91.88% / 93.95%, not significant | `eligibility.by_program` matches | ✅ |
| CLC non-CNTT admission | 186/215 (86.5%) | `composition.by_program[CNTT CLC].non_cntt_pct: 86.5` | ✅ |

**Bootstrap CIs** reproduce to 2–3 decimal places rather than bit-for-bit
(numpy/scipy patch versions differ between when `insight-discovery.md` was
written and when `uv sync` resolved the pipeline's environment — see
`README.md` "Deviations"). No point estimate, band count, significance
call, or sign reversal is affected.

### 3.2 Copy vs. pipeline — errors found and fixed

A full manual cross-reference of every numeric claim in
`site/src/data/copy.json` and every chart's static `aria-label` against
`aggregates.json`/`histograms.json` found **two real errors**, both now fixed:

| # | Location | Was | Should be | Root cause |
|---|---|---|---|---|
| 1 | §05 `altText` (copy.json + `EtaSquaredBar.astro`'s aria-label) | "xếp hạng **9** biến theo eta bình phương" | "**10** biến" | `variance_explained` has 10 entries (`class_code, track_label, credits, tttn_grade, credits_eligible_only, eligible_for_thesis, birthplace_n20plus, admission_major_code, program, is_off_cohort`); the "9" was inherited from an earlier count in `website-spec.md` written before `credits_eligible_only` was split out as its own row. |
| 2 | §05c deck (copy.json) | "Giữa các chuyên ngành thì là **0.81**" | "**0.76**" | 0.81 is the **class-level** spread (widest class mean − narrowest class mean, 3.2429 − 2.4331 ≈ 0.81, from an earlier class-caterpillar analysis). The sentence claims a **track-level** spread, which is `max(by_track.mean) − min(by_track.mean)` = 3.2429 (E22TTNT) − 2.4847 (D22HTTT) = **0.7582 → 0.76**. A copy-transcription error, not a pipeline error — confirmed by recomputing directly from `aggregates.json` (see verification command in the commit history). |

No other numeric claim, in any section, in any chart's `aria-label`, or in
the methodology tables, was found to disagree with the JSON. **No causal or
evaluative language error was found** — see §3.3.

**Residual risk, disclosed rather than fully solved:** copy numbers are
manually transcribed prose, not templated from JSON at build time (this was
a known trade-off in `architecture.md` §Phase 3, which proposed but never
implemented a `numbers-match` CI check). This review closed the two errors
that trade-off had already produced, but did not add the automated guard —
building a low-false-positive number extractor for free-form Vietnamese
prose (which legitimately contains many numbers *not* derived from
`aggregates.json`, e.g. class counts from the audit, dates, sample sizes
quoted directly) was judged not worth the false-positive churn for a
4-file, low-change-frequency content set. **Recommendation for future
work:** if `copy.json` starts changing frequently, invest in this check.

### 3.3 Statistical review — findings

| Check | Result |
|---|---|
| Misleading interpretations | None found. Every group comparison is paired with its confounding structure (CORE-2's Simpson's-paradox reveal, CORE-3's truncation evidence, §06's composition explanation before any program comparison is shown). |
| Unsupported claims | None found. Grepped for `tốt hơn`, `kém hơn`, `dạy tốt`, `chất lượng cao hơn`, `dẫn đến/dẫn tới`, `gây ra`, `khiến cho`, `chứng minh`, `ảnh hưởng (tích cực\|tiêu cực)` across every `.json`/`.astro`/`.tsx` file. Every hit is inside an explicit rejection ("Không được đọc ngược thành…", "không phải mức độ nhóm đó gây ra kết quả…") or a quoted question §10 explicitly declines to answer. |
| Sample-size problems | Handled: Explore hard-suppresses n<10 (`site/src/lib/guards.ts`), soft-warns 10≤n<30, §07's caveat explicitly flags the n=38/40 track denominators and the n=2 CNPM-ineligible count, §05c explicitly states low power rather than claiming equivalence. |
| Wrong statistical assumptions | None found. Comparisons use Mann-Whitney/Welch (no normality assumption forced), CIs are bootstrap at the aggregate level, normal-approximation only at group level (n≥32 everywhere it's used, stated as such in `insight-discovery.md` §1.3). |
| Inappropriate comparisons | The one addressed head-on: aggregate CNTT-vs-CLC (confounded by track composition) is shown **and then immediately deconfounded** in the same section rather than presented alone. |
| Accidental causal claims | None found (see language grep above). `eta_squared`'s docstring in `pipeline/stats/variance.py` and its caveat text both state explicitly that η² is descriptive, not causal. |

### 3.4 Production numbers vs. site — spot-verified live

Confirmed directly against the deployed URL (§7), not just the local build:
overall mean (2.79), IQR (0.59), all 18 class means/CIs (via each
`ClassCaterpillar` point's `<title>` tooltip), eligibility rates (99.4% /
83.5%), and composition percentages (44.7% / 23.3% / 15.8% / 13.5%) all
render correctly on the live production page.

---

## 4. Privacy assessment

### 4.1 Checklist (explicit review scope: raw data, bundled assets, APIs, JSON files, source maps, client-side datasets)

| Item | Check | Result |
|---|---|---|
| Raw data | `data/raw/*.xlsx` in git | ✅ Not tracked (`.gitignore` + confirmed via `git ls-files`) |
| Interim data | `data/interim/*.parquet` (has quasi-identifiers) in git | ✅ Not tracked |
| APIs | Any server endpoint / serverless function | ✅ None exist — `output: "static"`, confirmed in the Vercel build log ("output: static") |
| Client-side dataset | `rows.json` field set | ✅ Exactly `{track, major, cpa, cr, el}` — no `class_code`, no `tttn`, no identifier — verified against the **live production bundle**, not just local `dist/` |
| Bundled JS/HTML | Forbidden strings (`ma_sv`, `ho_dem`, `ngay_sinh`, `noi_sinh`, `birth_year`, `class_code`, `tttn`, student-ID patterns `B22DC…`/`B21DC…`/`N22DC…`) | ✅ Zero occurrences across `index.html` and every `_astro/*.js` chunk |
| Source maps | `.map` files or `sourceMappingURL` references | ✅ None emitted; now explicit (`vite.build.sourcemap: false`) rather than relying on default |
| Static JSON exposure | Raw `.json` files served at a guessable path (`/data/aggregates.json` etc.) | ✅ None — data lives under `src/`, not `public/`, so it's bundled into JS/HTML rather than served as a separate fetchable file |
| Payload duplication | `rows.json` serialized once vs. per-island | ✅ Fixed in the prior phase (shared Vite chunk via static `import`, not an Astro prop) — re-confirmed still holds after this phase's scale.ts refactor |
| Workbook metadata (author name in `docProps`) | Present in any shipped artifact | ✅ Never leaves `data/raw/`, which never leaves the developer's machine |
| k-anonymity of `rows.json` | Uniquely-identifiable row share on `{track, cpa, credits, eligible, major}` | ⚠️ **49.5%** — disclosed, not hidden (see §4.2) |
| Small-group suppression | Any published group n<10 | ✅ None — enforced by `pipeline/s5_privacy.py` P3 and independently by `site/src/lib/guards.ts` in Explore |
| Class-level min/max or per-class eligibility breakdown | Present anywhere | ✅ Absent — enforced by P5/P7 in the privacy gate and by omission in `s4_metrics.compute_by_class` |
| CORS | `Access-Control-Allow-Origin: *` on the live response | Present (Vercel default for static assets). Not a risk for this site: no cookies, no auth, no credentialed requests, read-only public content — noted, not remediated. |

### 4.2 The one disclosed, accepted residual risk

`rows.json`'s field set (`track`, `major`, `cpa`, `credits`, `eligible`)
still leaves **49.5%** of the 905 rows uniquely identifiable by that
combination alone (measured by `pipeline/s5_privacy.py` P6 and
independently re-verified in `pipeline/tests/test_privacy.py`). This was a
known, explicit trade-off from `architecture.md` §9.2, not a gap this
review discovered — re-confirming it here because "no individual student
can be exposed" is the review's explicit privacy bar, and this number
means: **someone who already knows a specific student's exact CPA and track
can, in roughly half of cases, infer that student's credit count and
thesis-eligibility status from the site.** Two things limit the real-world
severity: (a) CPA — the input to that inference — is itself the most
sensitive field, so the marginal disclosure is bounded; (b) it requires
already knowing the CPA precisely (to the hundredth) and the track, which
is not information the site itself provides in combination with any other
identifying detail. No fix was applied in this review because the
architecture doc already flagged the cheapest further lever (drop
`admission_major_code`, → 45.5% unique) as a data-owner decision, not an
engineering one — restating that recommendation here rather than making the
call unilaterally.

### 4.3 CSP note

The `<meta http-equiv="Content-Security-Policy">` tag in `BaseLayout.astro`
includes `style-src 'self' 'unsafe-inline'`. This remains a known, disclosed
compromise (documented in `README.md`): Astro inlines component-scoped
`<style>` blocks by default, and removing `unsafe-inline` would require
nonce-based CSP middleware incompatible with a pure static-output build.
`script-src 'self'` and `connect-src 'none'` — the higher-risk directives —
are unaffected and were verified live (§4.4).

### 4.4 Verified live (not just locally)

```
$ curl -sI https://site-theta-brown-88.vercel.app/
HTTP/1.1 200 OK
Permissions-Policy: geolocation=(), camera=(), microphone=(), interest-cohort=()
Referrer-Policy: no-referrer
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
X-Content-Type-Options: nosniff
```

`Strict-Transport-Security` is supplied by Vercel's platform default, not
`vercel.json` — a bonus, not a claim this project's config produced it.

---

## 5. Performance assessment

### 5.1 Bundle size — before/after this review

| | Before this phase | After this phase | Change |
|---|---:|---:|---:|
| `index.html` (gzip) | 39.0 KB | 39.0 KB | — (no content changed, two string fixes) |
| Total JS (gzip) | 29.6 KB | 22.0 KB | **−7.6 KB** |
| **Total first-load (gzip)** | **68.6 KB** | **61.0 KB** | **−11%** |
| Architecture budget (§10.1) | ≤ 130 KB | ≤ 130 KB | 53% headroom remaining |

The single largest contributor to the reduction: the chunk Vite had labeled
`jsxRuntime.module` (misleading name — it actually bundled Preact's JSX
runtime *together with* d3-scale's color-interpolation dependency tree)
dropped from **7.74 KB → 0.37 KB** gzip once `d3-scale` was removed.

### 5.2 Dependency audit

| Dependency | Status | Action |
|---|---|---|
| `d3-scale` | Only `.domain().range()` ever used; `.ticks()` was declared but never called (`niceTicks` in `svg.ts` had zero call sites) | **Removed**, replaced with a 10-line local function |
| `d3-array` | Zero imports anywhere in `src/` | **Removed** |
| `d3-shape` | `line`, `area`, `curveMonotoneX` — genuinely used for 3 density/ridgeline curves | Kept — no comparably small substitute justifies the rewrite |
| `@astrojs/preact`, `preact` | Core rendering | Kept — required |
| `astro` | Core framework | Kept — upgraded to 7.3.2 in the prior phase (0 `npm audit` vulnerabilities) |

`npm audit`: **0 vulnerabilities** (re-verified after dependency removal).

### 5.3 Unnecessary client-side data

Re-verified: `rows.json` (2.2 KB gzip) loads exactly once via a shared Vite
chunk (`stats.*.js`), consumed only by `ExplorePanel` and
`CpaCreditScatter` — the two components that need row-level data. No other
component imports it. `aggregates.json` slices are passed as Astro props
only to the specific island that renders them (no cross-island duplication
found).

### 5.4 Chart rendering

All 16 charts are inline SVG, computed synchronously at build time (Astro
components) or hydration time (5 Preact islands) — no client-side data
fetching, no chart re-render on every keystroke in Explore beyond React/
Preact's normal reconciliation on state change. The scatter plot (905
points, the largest chart) renders as plain SVG circles — well within SVG's
practical range; Canvas would only be justified past roughly 10,000 points.

### 5.5 What was not changed

`inlineStylesheets: "always"` remains in `astro.config.mjs` — this trades a
few extra HTML bytes for one fewer network round-trip, appropriate for a
single-page site. Not revisited since it doesn't conflict with the
performance budget and removing it would require the CSP `style-src`
trade-off in §4.3 to be resolved differently first.

---

## 6. Production build

Run fresh, in order, immediately before writing this report:

```
$ cd pipeline && uv run ruff check .          →  All checks passed!
$ cd pipeline && uv run pytest -q             →  39 passed
$ cd site && npx eslint .                     →  (no output — clean)
$ cd site && npx astro check                  →  0 errors, 0 warnings, 2 hints*
$ cd site && npx astro build                  →  ✓ Completed — 1 page built
```

\* The 2 hints are: (1) an upstream `typescript-eslint` deprecation notice
in `eslint.config.js` unrelated to this project's code, and (2) Astro's
standard `interface Props` convention in `Caveat.astro`, which is expected
in every `.astro` component and not a defect.

**No broken routes**: single-page static site, one route (`/`), all 10
in-page anchor links (`#scope` … `#limits`) verified present as real
`data-section` ids in the rendered HTML.

**No console errors**: verified by inspecting the rendered HTML for `NaN`/
`undefined` artifacts (zero found in `index.html`; the handful of `NaN`
substrings in vendor JS are d3-shape/Preact-internal number-formatting
utility code, not runtime output — confirmed by inspecting each occurrence's
context). A live headless-browser console check was not run in this
environment (no browser automation tool available); this is disclosed
rather than silently assumed away.

---

## 7. Deployment information

| | |
|---|---|
| **Platform** | Vercel (static hosting, zero-config Astro detection) |
| **Production URL** | **https://site-theta-brown-88.vercel.app** |
| **Deployment method** | `vercel deploy --temporary --yes` from `site/`, run with no logged-in account (Vercel's anonymous-deployment flow) |
| **Build command** | `npm run build` (`astro build`) — run by Vercel's own build environment, not the locally-built `dist/` |
| **Output directory** | `dist/` |
| **Config file** | `site/vercel.json` (framework hint, build command, output dir, security + cache headers) |
| **Environment variables** | None required — the site has no secrets, no API keys, no backend |
| **Live verification** | `curl` returned `HTTP 200`, correct `<title>`, all 10 section ids present, spot-checked numbers (905 students, class means, eligibility rates, composition %) match `aggregates.json` exactly |
| **Claim status** | This is an **anonymous temporary deployment** — it is live and publicly reachable now, but is not yet attached to a Vercel account/team. It can be claimed by whoever owns (or creates) the Vercel account, via the CLI's "claim" flow, to get permanent ownership, a custom domain, and auto-deploy-on-push. Until claimed, the deployment itself does not expire on its own, but no further deploys from this session will update it without a login. |
| **GitHub repository** | `https://github.com/AlgebraxCalculus/ptit-academic-insights` — public, pushed, `main` branch, 1 commit (`bdb40ec`), verified via the GitHub API |
| **Auto-deploy on push** | Not configured — would require `vercel git connect` (needs an authenticated Vercel session) to link the GitHub repo for automatic redeploys |

---

## 8. Known limitations

Carried forward (not re-litigated — see the named doc for full reasoning):

- **Analytical**: cohort/time-trend analysis is impossible (899/905 one
  intake, no time column) — `insight-discovery.md` §1.5, restated on-page
  in §07's "time panel."
- **Analytical**: the CNPM/HTTT track comparison and the CLC-vs-CNTT
  comparison both carry an unresolved confound (rank-based track
  assignment; CLC's admission-major composition) — `insight-discovery.md`
  §7, restated in `website-spec.md` §10 and on-page in §10.
- **Privacy**: `rows.json`'s field set leaves 49.5% of rows uniquely
  identifiable on that field combination alone — disclosed in §4.2 of this
  report, not newly discovered, not fully resolved (data-owner decision).
- **Engineering**: no automated "every number in copy matches aggregates.json"
  CI check exists; this review closed the two errors that gap had already
  produced by manual audit, but did not build the automated guard (§3.2).
- **Engineering**: `style-src 'unsafe-inline'` in the CSP meta tag, a
  structural consequence of Astro's default style-inlining (§4.3).
- **Verification**: no headless-browser console-error check was run in this
  environment (§6) — typecheck/lint/build cleanliness and manual HTML
  inspection are the checks that were actually performed.
- **Deployment**: the production URL is an unclaimed temporary Vercel
  deployment (§7) — durable ownership requires the project's actual owner
  to authenticate and claim it.

---

## 9. Summary for the record

| Question | Answer |
|---|---|
| Do the website's numbers match the pipeline? | Yes, after fixing 2 copy transcription errors found during this review (§3.2) |
| Any misleading/unsupported/causal claims? | None found (§3.3) |
| Can an individual student be identified from the public site? | No direct identifier anywhere; one disclosed residual statistical-uniqueness risk at 49.5%, bounded by the fact that CPA — the most sensitive field — must already be known to exploit it (§4.2) |
| Any chart without analytical value? | No removals; one intentionally-decorative, appropriately `aria-hidden` element identified and justified (§2) |
| Does the production build succeed? | **Yes** — lint clean, typecheck clean (0 errors), 39/39 pipeline tests pass, `astro build` succeeds (§6) |
| Is it deployed? | **Yes**, live and verified at the URL in §7 |
