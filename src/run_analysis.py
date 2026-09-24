"""Run the full analysis: headline index, sensitivity specifications, Monte Carlo, jackknife, PCA,
external comparisons. Writes tables/ (CSV) and data/processed/results.json (for the dashboard).
"""
import json, pathlib, numpy as np, pandas as pd
from frindex import (COMPONENTS, ORDER, composite, domain_weights, monte_carlo, jackknife, pca,
                     normalise, raw_matrix, spearman)

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROC, TAB = ROOT / "data" / "processed", ROOT / "tables"
TAB.mkdir(exist_ok=True)
df = pd.read_csv(PROC / "countries.csv", index_col="iso3")
NONUS = [c for c in df.index if c != "USA"]

# ---------------------------------------------------------------- Table 1: raw components
t1 = raw_matrix(df).copy()
t1.insert(0, "country", df["country"])
t1["gdp_pc_ppp_usd"] = df["gdp_pc_ppp_usd"]
t1["pharma_berd_year"] = df["pharma_berd_year"]
t1.to_csv(TAB / "table1_raw_components.csv")

# ---------------------------------------------------------------- Headline specification
base = composite(df)                                   # equal weights, min-max, arithmetic, 10 countries
base.insert(0, "country", df["country"])
base.sort_values("FRI", ascending=False).to_csv(TAB / "table2_headline_index.csv")

# ---------------------------------------------------------------- Alternative specifications
specs = {
    "S0 Equal weights (headline)":               dict(),
    "S1 Domain weights (1/3 each domain)":       dict(weights=domain_weights()),
    "S2 Payment-only (P,R)":                     dict(comps=["P", "R"]),
    "S3 Access-only (A,D)":                      dict(comps=["A", "D"]),
    "S4 Price only (P)":                         dict(comps=["P"]),
    "S5 Geometric aggregation":                  dict(agg="geometric"),
    "S6 z-score normalisation":                  dict(norm="zscore"),
    "S7 Rank normalisation":                     dict(norm="rank"),
    "S8 Income-adjusted price":                  dict(overrides={"P": "price_index_income_adj"}),
    "S9 New-drug revenue ratio":                 dict(overrides={"R": "rev_to_gdp_ratio_new_innov"}),
    "S10 Excluding United States (rescaled)":    dict(subset=NONUS),
    "S11 Association-basis pharma R&D":          dict(overrides={"I": "pharma_rd_pct_gdp_assoc"}),
}
spec_scores = pd.DataFrame({k: composite(df, **v)["FRI"] for k, v in specs.items()})
spec_ranks = spec_scores.rank(ascending=False, method="min")
jk = jackknife(df); jk_ranks = jk.rank(ascending=False, method="min")
allranks = pd.concat([spec_ranks, jk_ranks], axis=1)
allranks.insert(0, "country", df["country"])
allranks.to_csv(TAB / "table3_rank_by_specification.csv")
allscores = pd.concat([spec_scores, jk], axis=1); allscores.insert(0, "country", df["country"])
allscores.to_csv(TAB / "table3b_score_by_specification.csv")

# Spearman correlation of each specification with the headline
rho = {k: spearman(spec_scores["S0 Equal weights (headline)"], spec_scores[k]) for k in spec_scores}
rho.update({k: spearman(base["FRI"], jk[k]) for k in jk})
pd.Series(rho, name="spearman_vs_headline").to_csv(TAB / "table4_spearman_vs_headline.csv")

# ---------------------------------------------------------------- Monte Carlo
ranks_mc, mc = monte_carlo(df, n=10000)
mc.insert(0, "country", df["country"]); mc.to_csv(TAB / "table5_montecarlo_rank_intervals.csv")
ranks_mc9, mc9 = monte_carlo(df, n=10000, subset=NONUS)
mc9.insert(0, "country", df.loc[NONUS, "country"]); mc9.to_csv(TAB / "table5b_montecarlo_exUS.csv")
# rank frequency matrix (for dashboard / supplement)
freq = pd.DataFrame({c: np.bincount(ranks_mc[:, j], minlength=len(df) + 1)[1:] / len(ranks_mc) for j, c in enumerate(df.index)}).T
freq.columns = [f"rank{r}" for r in range(1, len(df) + 1)]; freq.index.name = "iso3"; freq.insert(0, "country", df["country"]); freq.to_csv(TAB / "table5c_rank_frequency.csv")

# ---------------------------------------------------------------- PCA
S = normalise(raw_matrix(df))
evr, load, pcs = pca(S)
pd.DataFrame({"explained_variance_ratio": evr}, index=load.columns).to_csv(TAB / "table6_pca_variance.csv")
load.to_csv(TAB / "table6b_pca_loadings.csv")
pcs.insert(0, "country", df["country"]); pcs.to_csv(TAB / "table6c_pca_scores.csv")
corr = S.corr(method="spearman"); corr.to_csv(TAB / "table6d_component_spearman.csv")
pearson = S.corr(); pearson.to_csv(TAB / "table6e_component_pearson.csv")

# ---------------------------------------------------------------- External comparators
ext = pd.DataFrame({
    "country": df["country"], "FRI_headline": base["FRI"], "FRI_rank": base["rank"],
    "Kolchinsky_Freeriding_Index_pct": df["kolchinsky_freeriding_index_pct"],
    "ASPE_rev_to_GDP_ratio_all_innov": df["rev_to_gdp_ratio_all_innov"],
    "ASPE_rev_to_pop_ratio_all_innov": df["rev_to_pop_ratio_all_innov"],
    "Frech2026_contribution_per_capita_usd": df["frech_contribution_per_capita_usd"],
    "PC1_score": pcs["PC1"],
})
ext.to_csv(TAB / "table7_external_comparators.csv")
extrho = {
    "Kolchinsky (7 countries)": spearman(ext["FRI_headline"], ext["Kolchinsky_Freeriding_Index_pct"]),
    "ASPE revenue/GDP (10, inverted)": spearman(ext["FRI_headline"], -ext["ASPE_rev_to_GDP_ratio_all_innov"]),
    "ASPE revenue/population (10, inverted)": spearman(ext["FRI_headline"], -ext["ASPE_rev_to_pop_ratio_all_innov"]),
    "Frech per-capita contribution (7, inverted)": spearman(ext["FRI_headline"], -ext["Frech2026_contribution_per_capita_usd"]),
    "PC1 (10)": spearman(ext["FRI_headline"], ext["PC1_score"]),
    "Kolchinsky vs ex-US headline (7)": spearman(spec_scores["S10 Excluding United States (rescaled)"], ext["Kolchinsky_Freeriding_Index_pct"]),
}
pd.Series(extrho, name="spearman").to_csv(TAB / "table7b_external_spearman.csv")

# ---------------------------------------------------------------- Component contributions (headline)
contrib = S / len(ORDER); contrib.insert(0, "country", df["country"]); contrib.to_csv(TAB / "table8_component_contributions.csv")

# ---------------------------------------------------------------- JSON for dashboard
out = {
    "generated": pd.Timestamp.today().strftime("%Y-%m-%d"),
    "components": {k: {"column": v[0], "direction": v[1], "label": v[2], "domain": v[3]} for k, v in COMPONENTS.items()},
    "countries": [
        {"iso3": c, "name": df.loc[c, "country"],
         "raw": {k: (None if pd.isna(df.loc[c, COMPONENTS[k][0]]) else float(df.loc[c, COMPONENTS[k][0]])) for k in ORDER},
         "raw_alt": {"price_index_income_adj": float(df.loc[c, "price_index_income_adj"]),
                      "rev_to_gdp_ratio_new_innov": float(df.loc[c, "rev_to_gdp_ratio_new_innov"])},
         "gdp_pc_ppp_usd": float(df.loc[c, "gdp_pc_ppp_usd"]), "rev_share_all_innov_pct": float(df.loc[c, "rev_share_all_innov_pct"]),
         "headline": {"FRI": float(base.loc[c, "FRI"]), "rank": int(base.loc[c, "rank"])},
         "mc": {"rank_median": float(mc.loc[c, "rank_median"]), "rank_p05": float(mc.loc[c, "rank_p05"]), "rank_p95": float(mc.loc[c, "rank_p95"])},
        } for c in df.index],
    "pca": {"explained_variance_ratio": [float(x) for x in evr], "loadings_PC1": {k: float(load.loc[k, "PC1"]) for k in ORDER}},
}
(PROC / "results.json").write_text(json.dumps(out, indent=1))
print(base.sort_values("FRI", ascending=False)[["country", *ORDER, "FRI", "rank"]].round(1).to_string())
print("\nMC rank intervals:\n", mc[["country", "rank_median", "rank_p05", "rank_p95", "p_top3"]].sort_values("rank_median").to_string())
print("\nPCA EVR:", np.round(evr, 3), "\nPC1 loadings:\n", load["PC1"].round(2).to_string())
print("\nSpearman vs headline:\n", pd.Series(rho).round(2).to_string())
print("\nExternal:\n", pd.Series(extrho).round(2).to_string())
