"""S4 — compute every statistic that appears in docs/insight-discovery.md.

This module only composes the reusable functions in stats/*.py against the
905-row in-scope DataFrame. It does not introduce any new analysis beyond
what Phase 2 (insight-discovery.md) already established — per the brief for
this phase, the analytical concept is not revisited here.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import config
from stats import comparison, distribution, thresholds, variance
from stats import overall as overall_stats
from stats.helpers import normal_ci_from_series, percentile_rank

MIN_N_FOR_GROUP_MEAN = config.MIN_GROUP_SIZE_FOR_MEAN


def _series(df: pd.DataFrame, col: str = "cpa") -> np.ndarray:
    return df[col].dropna().to_numpy()


def compute_overall(df: pd.DataFrame) -> dict:
    return overall_stats.overall_statistics(_series(df))


def compute_bands(df: pd.DataFrame) -> dict:
    return {
        "classification": thresholds.threshold_bands(_series(df)),
        "cumulative": thresholds.cumulative_thresholds(_series(df)),
    }


def compute_by_track(df: pd.DataFrame) -> list[dict]:
    out = []
    for track in config.TRACK_DICTIONARY:
        g = df[df["track_label"] == track]
        cpa = g["cpa"].dropna().to_numpy()
        elig_n = int(g["eligible_for_thesis"].sum())
        out.append(
            {
                "track": track,
                "program": g["program"].iloc[0],
                "n_rows": len(g),
                "n_cpa": len(cpa),
                "mean": round(float(cpa.mean()), 4),
                "ci": normal_ci_from_series(cpa),
                "median": round(float(np.median(cpa)), 4),
                "sd": round(float(cpa.std(ddof=1)), 4),
                "q1": round(float(np.quantile(cpa, 0.25)), 4),
                "q3": round(float(np.quantile(cpa, 0.75)), 4),
                "min": round(float(cpa.min()), 4),
                "max": round(float(cpa.max()), 4),
                "eligible_n": elig_n,
                "eligible_pct": round(100 * elig_n / len(g), 2),
                "eligible_ci": thresholds.proportion_ci(elig_n, len(g)),
                "credit_ceiling_pct": round(100 * float((g["credits"] == 146).mean()), 2),
            }
        )
    return out


def compute_by_class(df: pd.DataFrame) -> list[dict]:
    """Aggregate only — no min/max at class level (docs/data-audit.md rule F4)."""
    out = []
    for class_code, g in df.groupby("class_code", observed=True):
        cpa = g["cpa"].dropna().to_numpy()
        n = len(cpa)
        se = round(float(cpa.std(ddof=1) / np.sqrt(n)), 4)
        out.append(
            {
                "class": class_code,
                "track": g["track_label"].iloc[0],
                "n": n,
                "mean": round(float(cpa.mean()), 4),
                "sd": round(float(cpa.std(ddof=1)), 4),
                "se": se,
                "ci": normal_ci_from_series(cpa),
            }
        )
    out.sort(key=lambda r: (r["track"], r["class"]))
    return out


def compute_program_comparison(df: pd.DataFrame) -> dict:
    cntt = df.loc[df["program"] == "CNTT", "cpa"].dropna().to_numpy()
    clc = df.loc[df["program"] == "CNTT CLC", "cpa"].dropna().to_numpy()

    aggregate = comparison.compare_two_groups(clc, cntt, "clc", "cntt")
    aggregate["survives_bonferroni"] = comparison.survives_bonferroni(aggregate["p_mannwhitney"])

    pairs = []
    for pair_name, std_track, clc_track in [("CNPM", "D22CNPM", "E22CNPM"), ("HTTT", "D22HTTT", "E22HTTT")]:
        a = df.loc[df["track_label"] == clc_track, "cpa"].dropna().to_numpy()
        b = df.loc[df["track_label"] == std_track, "cpa"].dropna().to_numpy()
        result = comparison.compare_two_groups(a, b, "clc", "cntt")
        result["pair"] = pair_name
        result["survives_bonferroni"] = comparison.survives_bonferroni(result["p_mannwhitney"])
        pairs.append(result)

    ttnt_n = int((df["track_label"] == "E22TTNT").sum())
    clc_total = int((df["program"] == "CNTT CLC").sum())

    quantile_diff = []
    for q in range(0, 101, 10):
        c_val = float(np.percentile(cntt, q))
        l_val = float(np.percentile(clc, q))
        quantile_diff.append({"q": q, "cntt": round(c_val, 3), "clc": round(l_val, 3), "diff": round(l_val - c_val, 3)})

    band_share = {}
    for label, series in [("cntt", cntt), ("clc", clc)]:
        bands = thresholds.threshold_bands(series)
        band_share[label] = {b["label"]: b["pct"] for b in bands}

    return {
        "aggregate": aggregate,
        "paired": pairs,
        "unpaired_note": {"track": "E22TTNT", "n": ttnt_n, "pct_of_clc": round(100 * ttnt_n / clc_total, 1)},
        "quantile_diff": quantile_diff,
        "band_share": band_share,
    }


def compute_variance_explained(df: pd.DataFrame) -> list[dict]:
    entries = []
    for var in ["class_code", "track_label", "tttn_grade", "eligible_for_thesis", "admission_major_code", "program", "is_off_cohort"]:
        eta2, k = variance.eta_squared(df, "cpa", var)
        entries.append({"var": var, "metric": "eta2", "k": k, "value": round(eta2, 4)})

    big_birthplaces = df["birthplace"].value_counts()
    big_birthplaces = big_birthplaces[big_birthplaces >= MIN_N_FOR_GROUP_MEAN].index
    sub = df[df["birthplace"].isin(big_birthplaces)]
    eta2, k = variance.eta_squared(sub, "cpa", "birthplace")
    entries.append({"var": "birthplace_n20plus", "metric": "eta2", "k": k, "value": round(eta2, 4)})

    r2_all = variance.r_squared_pearson(df["cpa"], df["credits"])
    entries.append({"var": "credits", "metric": "r2", "k": None, "value": round(r2_all, 4)})

    elig = df[df["eligible_for_thesis"]]
    r2_elig = variance.r_squared_pearson(elig["cpa"], elig["credits"])
    entries.append({"var": "credits_eligible_only", "metric": "r2", "k": None, "value": round(r2_elig, 4)})

    entries.sort(key=lambda e: e["value"], reverse=True)
    return entries


def compute_track_contrast(df: pd.DataFrame) -> dict:
    cnpm = df.loc[df["track_label"] == "D22CNPM", "cpa"].dropna().to_numpy()
    httt = df.loc[df["track_label"] == "D22HTTT", "cpa"].dropna().to_numpy()

    cmp = comparison.compare_two_groups(cnpm, httt, "cnpm", "httt")
    cliffs_delta = cmp["cliffs_delta"]
    cnpm_min = float(cnpm.min())
    httt_median = float(np.median(httt))

    cntt_only = df[df["program"] == "CNTT"]
    eta2_within, _ = variance.eta_squared(cntt_only, "cpa", "track_label")

    truncation = {
        "cnpm_min": round(cnpm_min, 2),
        "cnpm_below_min": 0,
        "cnpm_below_httt_median": int((cnpm < httt_median).sum()),
        "httt_above_cnpm_min_pct": round(100 * float((httt > cnpm_min).mean()), 1),
    }

    class_homogeneity = []
    for track, g in df.groupby("track_label", observed=True):
        classes = g["class_code"].unique()
        if len(classes) < 2:
            continue
        class_groups = [g.loc[g["class_code"] == c, "cpa"].dropna().to_numpy() for c in classes]
        kw = comparison.kruskal_groups(class_groups)
        means = [float(np.mean(cg)) for cg in class_groups if len(cg)]
        class_homogeneity.append(
            {
                "track": track,
                "k": len(classes),
                "H": kw["H"],
                "p": kw["p"],
                "mean_spread": round(max(means) - min(means), 4),
            }
        )

    return {
        "cnpm_vs_httt": {
            "diff": cmp["diff"],
            "cohens_d": cmp["cohens_d"],
            "cliffs_delta": cliffs_delta,
            "p_superiority": round(0.5 * (cliffs_delta + 1), 4),
            "p_mannwhitney": cmp["p_mannwhitney"],
            "truncation": truncation,
            "eta2_within_cntt": round(eta2_within, 4),
        },
        "class_homogeneity": class_homogeneity,
    }


def compute_eligibility(df: pd.DataFrame) -> dict:
    n = len(df)
    eligible_n = int(df["eligible_for_thesis"].sum())

    by_program = {}
    for prog in config.PROGRAM_DICTIONARY:
        g = df[df["program"] == prog]
        e = int(g["eligible_for_thesis"].sum())
        key = "cntt" if prog == "CNTT" else "clc"
        by_program[key] = {"n": len(g), "eligible": e, "pct": round(100 * e / len(g), 2)}

    prog_table = pd.crosstab(df["program"], df["eligible_for_thesis"]).to_numpy()
    prog_chi2 = comparison.chi2_independence(prog_table)

    track_table = pd.crosstab(df["track_label"], df["eligible_for_thesis"]).to_numpy()
    track_chi2 = comparison.chi2_independence(track_table)

    cnpm_elig = df.loc[df["track_label"] == "D22CNPM", "eligible_for_thesis"]
    httt_elig = df.loc[df["track_label"] == "D22HTTT", "eligible_for_thesis"]
    cnpm_table = pd.crosstab(
        pd.concat([cnpm_elig, httt_elig]).reset_index(drop=True),
        pd.Series(["cnpm"] * len(cnpm_elig) + ["httt"] * len(httt_elig)),
    ).to_numpy()
    cnpm_httt_fisher_p = comparison.fisher_exact_2x2(cnpm_table)
    cnpm_pct = round(100 * float(cnpm_elig.mean()), 2)
    httt_pct = round(100 * float(httt_elig.mean()), 2)

    ineligible = df.loc[~df["eligible_for_thesis"], "cpa"].dropna().to_numpy()
    eligible = df.loc[df["eligible_for_thesis"], "cpa"].dropna().to_numpy()
    all_cpa = df["cpa"].dropna().to_numpy()

    ineligible_max = float(ineligible.max())

    eligible_credits_min = float(df.loc[df["eligible_for_thesis"], "credits"].min())
    ineligible_credits_max = float(df.loc[~df["eligible_for_thesis"], "credits"].max())
    lo, hi = eligible_credits_min, ineligible_credits_max
    band = df[(df["credits"] >= lo) & (df["credits"] <= hi)]

    return {
        "overall": {"n": n, "eligible": eligible_n, "pct": round(100 * eligible_n / n, 2)},
        "by_program": {
            **by_program,
            "chi2_p": prog_chi2["p"],
            "significant": prog_chi2["p"] < 0.05,
        },
        "by_track_chi2": track_chi2,
        "pairwise": {
            "cnpm_vs_httt": {
                "cnpm_pct": cnpm_pct,
                "httt_pct": httt_pct,
                "diff_pp": round(cnpm_pct - httt_pct, 2),
                "fisher_p": cnpm_httt_fisher_p,
            }
        },
        "cpa_contrast": {
            "ineligible": {"n": len(ineligible), "mean": round(float(ineligible.mean()), 4)},
            "eligible": {"n": len(eligible), "mean": round(float(eligible.mean()), 4)},
            "cohens_d": round(comparison.cohens_d(eligible, ineligible), 4),
        },
        "cpa_not_determinant": {
            "ineligible_ge_2_5": int((ineligible >= 2.5).sum()),
            "ineligible_ge_3_0": int((ineligible >= 3.0).sum()),
            "ineligible_max_cpa": round(ineligible_max, 2),
            "ineligible_max_pctile": percentile_rank(ineligible_max, all_cpa),
        },
        "credit_overlap": {
            "lo": lo,
            "hi": hi,
            "n_in_band": len(band),
            "eligible": int(band["eligible_for_thesis"].sum()),
            "ineligible": int((~band["eligible_for_thesis"]).sum()),
        },
    }


def compute_composition(df: pd.DataFrame) -> dict:
    by_program = []
    for prog in config.PROGRAM_DICTIONARY:
        g = df[df["program"] == prog]
        total = len(g)
        majors = []
        for major, mg in g.groupby("admission_major_code", observed=True):
            mn = len(mg)
            mean_cpa = None
            if mn >= MIN_N_FOR_GROUP_MEAN:
                mean_cpa = round(float(mg["cpa"].dropna().mean()), 4)
            majors.append({"major": major, "n": mn, "pct": round(100 * mn / total, 1), "mean_cpa": mean_cpa})
        majors.sort(key=lambda m: m["n"], reverse=True)

        entry = {"program": prog, "total": total, "majors": majors}
        if prog == "CNTT CLC":
            non_cntt_n = int((g["admission_major_code"] != "DCCN").sum())
            entry["non_cntt_n"] = non_cntt_n
            entry["non_cntt_pct"] = round(100 * non_cntt_n / total, 1)
        by_program.append(entry)

    clc = df[df["program"] == "CNTT CLC"]
    it_family = clc[clc["admission_major_code"].isin(["DCCN", "DCAT"])]["cpa"].dropna().to_numpy()
    telecom_family = clc[clc["admission_major_code"].isin(["DCVT", "DCDT"])]["cpa"].dropna().to_numpy()
    mw = comparison.compare_two_groups(it_family, telecom_family, "it", "telecom")

    return {
        "by_program": by_program,
        "it_vs_telecom": {
            "it": {"n": len(it_family), "mean": round(float(it_family.mean()), 4)},
            "telecom": {"n": len(telecom_family), "mean": round(float(telecom_family.mean()), 4)},
            "diff": mw["diff"],
            "cohens_d": mw["cohens_d"],
            "p": mw["p_mannwhitney"],
        },
    }


def compute_histograms(df: pd.DataFrame) -> dict:
    edges, overall_counts = distribution.histogram(df["cpa"])
    by_program = {}
    for prog in config.PROGRAM_DICTIONARY:
        _, counts = distribution.histogram(df.loc[df["program"] == prog, "cpa"])
        by_program[prog] = counts
    by_track = {}
    for track in config.TRACK_DICTIONARY:
        _, counts = distribution.histogram(df.loc[df["track_label"] == track, "cpa"])
        by_track[track] = counts
    return {
        "bin_width": config.CPA_HISTOGRAM_BIN_WIDTH,
        "domain": list(config.CPA_HISTOGRAM_DOMAIN),
        "edges": edges,
        "overall": overall_counts,
        "by_program": by_program,
        "by_track": by_track,
    }


def compute_all(df: pd.DataFrame) -> dict:
    return {
        "overall": compute_overall(df),
        "bands": compute_bands(df),
        "by_track": compute_by_track(df),
        "by_class": compute_by_class(df),
        "program_comparison": compute_program_comparison(df),
        "variance_explained": compute_variance_explained(df),
        "track_contrast": compute_track_contrast(df),
        "eligibility": compute_eligibility(df),
        "composition": compute_composition(df),
    }
