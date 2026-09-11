# PTIT Academic Insights

A public data story about academic outcomes for 905 Information Technology
students (CNTT and CNTT CLC, 2022 intake) at PTIT, as of one thesis-eligibility
snapshot. Static site, no backend, no database — every number on the page is
precomputed by a Python pipeline from one Excel file and shipped as
anonymized JSON.

**Live:** https://site-theta-brown-88.vercel.app (unclaimed temporary Vercel
deployment — see `docs/final-review.md` §7 for deployment details and how to
claim permanent ownership)
**Repository:** https://github.com/AlgebraxCalculus/ptit-academic-insights

**Read these first, in order — they are the source of truth this
implementation follows exactly:**

1. [`docs/data-audit.md`](docs/data-audit.md) — what the raw data is, its quality issues, cleaning rules
2. [`docs/insight-discovery.md`](docs/insight-discovery.md) — every statistic, with evidence, that the site is allowed to state
3. [`docs/website-spec.md`](docs/website-spec.md) — the page's content structure, headlines, copy, interactions
4. [`docs/architecture.md`](docs/architecture.md) — the technical design this code implements
5. [`docs/final-review.md`](docs/final-review.md) — senior review: validation, statistical/privacy/UX/performance audit, production build and deployment sign-off

If a number on the site and a number in `docs/insight-discovery.md` ever
disagree, the document is right and the code is wrong — fix the code (see
[Updating the data](#updating-the-data)).

## Repository layout

```
data/
  raw/            source .xlsx — NEVER committed (.gitignore), contains PII
  interim/        cleaned parquet with quasi-identifiers — NEVER committed
  reference/      versioned lookup tables (birthplace normalization)
pipeline/         Python: raw xlsx -> validated -> cleaned -> metrics -> anonymized JSON
site/             Astro static site consuming pipeline/'s JSON output
docs/             the four specification documents above
```

## Data pipeline

```
raw xlsx → validate → clean → scope + derive → metrics → privacy gate → JSON
```

| Stage | File | What it does |
|---|---|---|
| S1 | `pipeline/s1_ingest.py` | Reads the workbook, checks it still matches the audited shape |
| S2 | `pipeline/s2_clean.py` | Cleaning rules A3/A4/D1/E1/E2/E4 from the audit — never imputes CPA or TTTN |
| S3 | `pipeline/s3_scope.py` | Filters to the 905 in-scope rows, derives track/program/eligibility fields |
| S4 | `pipeline/s4_metrics.py` | Every statistic in `insight-discovery.md`, built from `pipeline/stats/` |
| S5 | `pipeline/s5_privacy.py` | 8 automated checks (P1–P8) — **can fail the build** |
| S6 | `pipeline/s6_emit.py` | Validates against JSON Schema, writes to `site/src/data/` |

`pipeline/stats/` is the reusable analytical layer requested for this phase:
`overall.py` (descriptives, percentiles, Gini, bimodality), `thresholds.py`
(classification bands), `comparison.py` (Mann-Whitney, Cohen's d, Cliff's
delta, chi-square, Kruskal-Wallis), `variance.py` (eta-squared, r²),
`bootstrap.py` (seeded resampling), `distribution.py` (histogram binning).
`s4_metrics.py` only composes these — it introduces no new analysis beyond
what `insight-discovery.md` already established.

### Running it

```bash
cd pipeline
uv sync
uv run python run.py       # requires data/raw/DS-SV-DK-DATN-D22-KY-THUAT.xlsx to exist locally
uv run pytest -q            # 39 tests: cleaning behavior, metrics vs. insight-discovery.md, privacy gate
uv run ruff check .
```

The pipeline never runs in CI — only a person with access to the raw
workbook runs it locally, then commits the resulting JSON.

### Privacy gate (`pipeline/s5_privacy.py`)

The client-shipped row payload (`site/src/data/rows.json`) carries exactly
five fields: `track`, `major`, `cpa`, `cr` (credits), `el` (eligibility) — no
`class_code`, no `tttn`, no identifier of any kind. This isn't a stylistic
choice: measured directly on the data, adding `class_code` back pushes
uniquely-identifiable rows from **49.5% to 85.1%**, and 9 of the 11 classes
with ineligible students have fewer than 10 such students — exactly the
suppression threshold `data-audit.md` sets. Eight checks enforce this and
related rules (minimum group size, nulled small-group means, no class-level
min/max, no ineligible-by-class breakdown) every time the pipeline runs, and
`pipeline/tests/test_privacy.py` enforces the same in CI-style testing
independent of a live run.

## Site

Astro (static output) + TypeScript (strict) + Preact islands + hand-rolled
SVG charts built with `d3-scale`/`d3-shape`. Rationale for this stack (and
why not React/Next.js/a chart library/a database) is in
`docs/architecture.md` §0–§2.

```bash
cd site
npm install
npm run dev         # http://localhost:4321
npm run build        # -> site/dist/
npm run typecheck    # astro check — 0 errors
npm run lint          # eslint — 0 errors
```

Both `npm run typecheck` and `npm run lint` currently pass with zero errors
and zero warnings (two harmless informational hints remain: an upstream
`typescript-eslint` deprecation notice, and Astro's standard `Props`
interface pattern, which is expected in every `.astro` component).

### Structure

11 sections (`site/src/sections/`), assembled in `site/src/pages/index.astro`,
matching `website-spec.md` §2 exactly — including the two changes that spec
made to the brief's suggested outline: no standalone "Cohort patterns"
section (899/905 students share one intake; there is no time axis in the
data — this is stated as a finding, not silently omitted), and no separate
"Insights" section (insights are load-bearing content inside sections 02–07,
not a repeated summary).

Only 5 components hydrate JavaScript (`client:visible`/`client:idle`):
`ProgramReveal` (§04's three-step reveal), `ColorByToggle` (§05's
color-by-program/track histogram), `EligibilityBars` and `CpaCreditScatter`
(§07), and `ExplorePanel` (§08). Every other section — including the
methodology accordion and the classification-band toggle in §03 — ships as
plain HTML/CSS with zero client JS (the band toggle uses a checkbox +
`:checked ~` CSS selector, no script).

`site/src/data/copy.json` holds every headline, deck, body paragraph, and
caveat as data, separate from component code, so content can be reviewed
without reading TSX/Astro. `site/src/data/{meta,rows,aggregates,histograms}.json`
are pipeline output — regenerated by `pipeline/run.py`, never hand-edited.

### Privacy in the UI

- Explore (§08) has no birthplace/birth-year filter and no student search.
- Selecting a class in Explore overlays a **pre-computed mean ± CI marker**
  from `aggregates.json` — it never touches row-level data for that class.
- Any filtered subgroup under **n = 10** is hidden with an explanatory
  message (`site/src/lib/guards.ts`), independent of the pipeline's own gate.
- The one individual-level chart (§07's CPA × credits scatter) shows only
  CPA, credits, and eligibility in its tooltip — no track, no major.
- `rows.json` (~12 KB raw, **2.2 KB gzip**) is imported as a static ES module
  inside the two components that need it (`ExplorePanel`, `CpaCreditScatter`)
  rather than passed as a prop from their parent `.astro` files — this makes
  Vite bundle it as one shared, cached chunk instead of serializing it twice
  into the page HTML.
- A `Content-Security-Policy` meta tag sets `connect-src 'none'`: the page
  makes no network call after it loads, which is a checkable claim, not a
  design aspiration.

### Client-side statistics boundary

Per `architecture.md` §7.3, the browser is only ever allowed to filter,
count, compute a mean/SD/normal-approximation CI, and re-bin a histogram
(`site/src/lib/stats.ts`). Every bootstrap CI, hypothesis test, effect size,
and eta-squared value comes from the pipeline and is read from
`aggregates.json` — Explore labels its own mean/CI as an "ước lượng nhanh"
(quick estimate) precisely so it's never mistaken for those numbers.

## Deviations from the specs, and why

These are implementation-level pragmatic choices, not changes to the
analytical concept, the site's content, or its privacy guarantees:

- **Package versions**: `docs/architecture.md` named specific pinned
  versions (Astro 5.x, `@astrojs/preact` 4.x) current when it was written.
  At implementation time the real npm registry's latest Astro (7.3.2) fixed
  several published critical/high-severity CVEs that the originally-named
  major version had — `npm audit` reported 0 vulnerabilities only after
  upgrading. The stack (static Astro + Preact islands + hand-rolled D3 SVG)
  is unchanged; only the exact version numbers moved to the current patched
  release.
- **JSON Schema generation**: `architecture.md` §3 describes generating
  `site/src/types/data.d.ts` from the JSON Schemas. It is hand-written
  instead, kept in sync manually against the pipeline's actual output
  (verified by inspecting real generated JSON during implementation). For a
  4-file, stable schema this avoids a code-generation step for negligible
  benefit; if the schemas grow, generating the types becomes worthwhile.
- **CSP `style-src`**: includes `'unsafe-inline'` because Astro inlines
  component-scoped `<style>` blocks directly into the page by default.
  `script-src` and `connect-src` — the higher-risk directives — remain
  strict (`'self'` and `'none'`). Removing `unsafe-inline` would require
  nonce-based CSP middleware, out of scope for a static-output build.
- **Fonts**: the design tokens specify a system font stack
  (`Inter`/`Helvetica`/system-ui, `Source Serif 4`/Georgia) rather than
  self-hosted font files, since no brand font asset was supplied. This still
  satisfies the "no external font CDN" privacy rule — it just doesn't invent
  a font file that wasn't given.
- **KDE**: the distribution chart (§03) and the track ridgeline (§05b) use a
  monotone curve through the pipeline's own histogram bin midpoints rather
  than a fitted Gaussian KDE. This plots the same numbers `insight-discovery.md`
  already reports, without introducing a new statistical model on the client.
- **Numbers vs. `insight-discovery.md`**: bootstrap confidence intervals
  reproduce to 2–3 decimal places, not bit-for-bit — the analysis doc was
  written against numpy 2.4.2/scipy 1.17.1; the pipeline's `uv sync` resolved
  numpy 2.5.3/scipy 1.18.1 (newer patch releases available at implementation
  time). Every point estimate, band count, p-value significance call, and
  the Simpson's-paradox sign reversal are exact matches — see
  `pipeline/tests/test_metrics.py`, which pins tolerances explicitly rather
  than asserting bit-identity.
- **Browser console verification**: typecheck, lint, and production build
  are all clean, and the built site was smoke-tested by serving it and
  inspecting the rendered HTML (correct section markup, correct numbers, no
  forbidden fields present — see the privacy scan in
  `pipeline/privacy-report.md` and the equivalent checks run against
  `site/dist/`). No headless-browser console-error check was run in this
  environment; if one is available in yours, `npx astro preview` plus any
  browser automation tool is the natural way to add it.

## Updating the data

1. Place the new `.xlsx` at `data/raw/` (it stays out of git).
2. `cd pipeline && uv run python run.py` — read its diff report.
3. If any number changed, update `docs/insight-discovery.md` **first**.
4. `uv run pytest -q` — `test_metrics.py` will fail if the JSON and the doc disagree.
5. `cd ../site && npm run build` to confirm the site still builds.
6. Commit the updated JSON and the updated doc in the same PR.
