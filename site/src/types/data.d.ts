/**
 * Shapes of the four JSON artifacts emitted by pipeline/s6_emit.py
 * (docs/architecture.md §5). Hand-written to mirror the pipeline's actual
 * output exactly — see pipeline/s4_metrics.py and pipeline/s5_privacy.py for
 * the source of truth. If a field here doesn't match what the pipeline
 * emits, the pipeline is right and this file is stale.
 */

export interface Meta {
  generated_at: string;
  pipeline_version: string;
  source_file_sha256: string;
  source_rows_total: number;
  scope_regex: string;
  n_in_scope: number;
  n_with_cpa: number;
  n_classes: number;
  n_tracks: number;
  n_programs: number;
  cohort: Record<string, number>;
  min_group_size: number;
  bootstrap: { iterations: number; seed: number };
  dictionaries: {
    track: string[];
    program: string[];
    major: string[];
    /** track_program[i] = index into `program` for `track[i]` — derived from
     * the actual data, not a name-prefix rule re-typed on the frontend. */
    track_program: number[];
  };
}

/** Row-level anonymized payload — only these 5 fields ever leave the pipeline
 * (docs/architecture.md §9.2). track/major are indices into meta.dictionaries.
 * cpa is x100 (279 = 2.79); cpa/cr use -1 as the "missing" sentinel. */
export interface RowsPayload {
  n: number;
  encoding: "columnar-int";
  track: number[];
  major: number[];
  cpa: number[];
  cr: number[];
  el: number[];
}

export interface Percentiles {
  p1: number; p5: number; p10: number; p20: number; p25: number; p30: number;
  p40: number; p50: number; p60: number; p70: number; p75: number; p80: number;
  p90: number; p95: number; p99: number;
}

export interface OverallStats {
  n: number;
  mean: number; mean_ci: number[];
  median: number; median_ci: number[];
  sd: number; variance: number;
  iqr: number; q1: number; q3: number;
  min: number; max: number;
  skew: number; kurtosis: number;
  gini: number; sarle_bc: number;
  percentiles: Percentiles;
}

export interface Band {
  label: string;
  min: number;
  max: number;
  n: number;
  pct: number;
  ci: number[];
}

export interface CumulativeThreshold {
  threshold: number;
  n: number;
  pct: number;
}

export interface ByTrack {
  track: string;
  program: string;
  n_rows: number;
  n_cpa: number;
  mean: number;
  ci: number[];
  median: number;
  sd: number;
  q1: number;
  q3: number;
  min: number;
  max: number;
  eligible_n: number;
  eligible_pct: number;
  eligible_ci: number[];
  credit_ceiling_pct: number;
}

/** No min/max, no eligibility breakdown — enforced by pipeline/s5_privacy.py P5/P7. */
export interface ByClass {
  class: string;
  track: string;
  n: number;
  mean: number;
  sd: number;
  se: number;
  ci: number[];
}

export interface GroupSummary {
  n: number;
  mean: number;
  median: number;
  sd: number;
}

export interface TwoGroupComparison {
  clc: GroupSummary;
  cntt: GroupSummary;
  diff: number;
  ci: number[];
  p_mannwhitney: number;
  p_welch: number;
  cohens_d: number;
  cliffs_delta: number;
  survives_bonferroni: boolean;
  pair?: string;
}

export interface QuantileDiffPoint {
  q: number;
  cntt: number;
  clc: number;
  diff: number;
}

export interface ProgramComparison {
  aggregate: TwoGroupComparison;
  paired: TwoGroupComparison[];
  unpaired_note: { track: string; n: number; pct_of_clc: number };
  quantile_diff: QuantileDiffPoint[];
  band_share: { cntt: Record<string, number>; clc: Record<string, number> };
}

export interface VarianceEntry {
  var: string;
  metric: "eta2" | "r2";
  k: number | null;
  value: number;
}

export interface ClassHomogeneity {
  track: string;
  k: number;
  H: number;
  p: number;
  mean_spread: number;
}

export interface TrackContrast {
  cnpm_vs_httt: {
    diff: number;
    cohens_d: number;
    cliffs_delta: number;
    p_superiority: number;
    p_mannwhitney: number;
    truncation: {
      cnpm_min: number;
      cnpm_below_min: number;
      cnpm_below_httt_median: number;
      httt_above_cnpm_min_pct: number;
    };
    eta2_within_cntt: number;
  };
  class_homogeneity: ClassHomogeneity[];
}

export interface Eligibility {
  overall: { n: number; eligible: number; pct: number };
  by_program: {
    cntt: { n: number; eligible: number; pct: number };
    clc: { n: number; eligible: number; pct: number };
    chi2_p: number;
    significant: boolean;
  };
  by_track_chi2: { chi2: number; p: number; cramers_v: number };
  pairwise: {
    cnpm_vs_httt: { cnpm_pct: number; httt_pct: number; diff_pp: number; fisher_p: number };
  };
  cpa_contrast: {
    ineligible: { n: number; mean: number };
    eligible: { n: number; mean: number };
    cohens_d: number;
  };
  cpa_not_determinant: {
    ineligible_ge_2_5: number;
    ineligible_ge_3_0: number;
    ineligible_max_cpa: number;
    ineligible_max_pctile: number;
  };
  credit_overlap: { lo: number; hi: number; n_in_band: number; eligible: number; ineligible: number };
}

export interface MajorEntry {
  major: string;
  n: number;
  pct: number;
  mean_cpa: number | null;
}

export interface CompositionByProgram {
  program: string;
  total: number;
  majors: MajorEntry[];
  non_cntt_n?: number;
  non_cntt_pct?: number;
}

export interface Composition {
  by_program: CompositionByProgram[];
  it_vs_telecom: {
    it: { n: number; mean: number };
    telecom: { n: number; mean: number };
    diff: number;
    cohens_d: number;
    p: number;
  };
}

export interface BirthplaceBandProvince {
  province: string;
  n: number;
  pct_of_band: number;
  pct_of_province: number;
}

export interface BirthplaceBand {
  band: string;
  n: number;
  provinces: BirthplaceBandProvince[];
  other_n: number;
  other_pct: number;
}

export interface BirthplaceBands {
  bands: BirthplaceBand[];
  min_province_n: number;
  min_cell_n: number;
}

export interface Aggregates {
  overall: OverallStats;
  bands: { classification: Band[]; cumulative: CumulativeThreshold[] };
  by_track: ByTrack[];
  by_class: ByClass[];
  program_comparison: ProgramComparison;
  variance_explained: VarianceEntry[];
  track_contrast: TrackContrast;
  eligibility: Eligibility;
  composition: Composition;
  birthplace_bands: BirthplaceBands;
}

export interface Histograms {
  bin_width: number;
  domain: number[];
  edges: number[];
  overall: number[];
  by_program: Record<string, number[]>;
  by_track: Record<string, number[]>;
}
