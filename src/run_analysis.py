"""Full analysis. Headline = nine non-US countries (US is the numeraire). Writes tables/ and data/processed/results.json."""
import json, pathlib, numpy as np, pandas as pd
from frindex import (COMPONENTS, ORDER, NONUS, composite, domain_weights, monte_carlo, leave_one_component_out,
                     leave_one_country_out, pca, normalise, raw_matrix, spearman, spearman_ci, spearman_perm_p,
                     effective_importance, equal_importance_weights, aggregate)

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROC, TAB = ROOT / "data" / "processed", ROOT / "tables"
TAB.mkdir(exist_ok=True)
df = pd.read_csv(PROC / "countries.csv", index_col="iso3")
ALL = list(df.index)

# ---- Table 1: raw components (all ten, US shown as numeraire)
t1 = raw_matrix(df).copy(); t1.insert(0, "country", df["country"])
for extra in ["price_index_all_us100", "gdp_pc_ppp_usd", "pharma_berd_year", "industry_trials_per_million", "rd_tax_subsidy_large", "gbard_health_pct_gdp"]:
    t1[extra] = df[extra]
t1.to_csv(TAB / "table1_raw_components.csv")

# ---- Headline: nine non-US countries
base = composite(df); base.insert(0, "country", df.loc[NONUS, "country"])
base.sort_values("FRI", ascending=False).to_csv(TAB / "table2_headline_index.csv")
S9 = normalise(raw_matrix(df.loc[NONUS]))
imp = effective_importance(S9, base["FRI"])

# ---- Specifications
specs = {
    "S0 Headline (nine countries, equal weights)": dict(),
    "S1 Domain weights (1/3 each)":               dict(weights=domain_weights()),
    "S2 Payment only (P,R)":                      dict(comps=["P", "R"]),
    "S3 Adoption only (A,D)":                     dict(comps=["A", "D"]),
    "S4 Price only (P)":                          dict(comps=["P"]),
    "S5 Geometric aggregation":                   dict(agg="geometric"),
    "S6 z-score normalisation":                   dict(norm="zscore"),
    "S7 Rank normalisation":                      dict(norm="rank"),
    "S8 Log min-max normalisation":               dict(norm="log_minmax"),
    "S9 All-drug price index":                    dict(overrides={"P": "price_index_all_us100"}),
    "S10 Income-adjusted brand price":            dict(overrides={"P": "price_index_brand_income_adj"}),
    "S11 Ability-to-pay adjusted payment":        dict(overrides={"P": "price_index_brand_income_adj", "R": "rev_to_gdp_ratio_progressive"}),
    "S12 New-drug revenue ratio":                 dict(overrides={"R": "rev_to_gdp_ratio_new_innov"}),
    "S13 Delay imputed for non-reimbursed drugs": dict(overrides={"D": "reimb_delay_imputed"}),
    "S14 W.A.I.T. adoption data for EU-5":        dict(overrides={"A": "reimb_share_wait_mix", "D": "reimb_delay_wait_mix"}),
    "S15 Association-basis pharma R&D":           dict(overrides={"I": "pharma_rd_pct_gdp_assoc"}),
    "S16 Trial hosting replaces R&D input":       dict(overrides={"I": "industry_trials_per_million"}),
    "S17 Payment and adoption only (P,R,A,D)":    dict(comps=["P", "R", "A", "D"]),
    "S18 Six components (+ R&D tax subsidy)":     dict(comps=ORDER + ["T"]),
    "S19 Seven components (+ tax, + trials)":     dict(comps=ORDER + ["T", "C"]),
    "S20 Size-adjusted (residual on log GDP)":    dict(size_adjust=True),
    "S21 Ten countries including United States":  dict(subset=ALL),
}
spec_scores = pd.DataFrame({k: composite(df, **v)["FRI"] for k, v in specs.items()}).reindex(ALL)
spec_ranks = spec_scores.rank(ascending=False, method="min")
loco = leave_one_component_out(df); loco_ranks = loco.rank(ascending=False, method="min")
lcoo = leave_one_country_out(df)
allranks = pd.concat([spec_ranks, loco_ranks], axis=1).reindex(ALL); allranks.insert(0, "country", df["country"])
allranks.to_csv(TAB / "table3_rank_by_specification.csv")
allscores = pd.concat([spec_scores, loco], axis=1).reindex(ALL); allscores.insert(0, "country", df["country"]); allscores.to_csv(TAB / "table3b_score_by_specification.csv")
lcoo.insert(0, "country", df.loc[NONUS, "country"]); lcoo.to_csv(TAB / "table3c_leave_one_country_out_ranks.csv")

head = spec_scores["S0 Headline (nine countries, equal weights)"]
rho = {}
for k in list(spec_scores.columns)[1:]:
    r, n = spearman(head, spec_scores[k]); rho[k] = r
for k in loco: rho[k] = spearman(head, loco[k])[0]
pd.Series(rho, name="spearman_vs_headline").to_csv(TAB / "table4_spearman_vs_headline.csv")

# ---- Monte Carlo (nine countries, calibrated noise + source switches) and variants
ranks_mc, mc = monte_carlo(df, n=10000)
mc.insert(0, "country", df.loc[NONUS, "country"]); mc.to_csv(TAB / "table5_montecarlo_rank_intervals.csv")
_, mc_noswitch = monte_carlo(df, n=10000, use_switches=False); mc_noswitch.insert(0, "country", df.loc[NONUS, "country"]); mc_noswitch.to_csv(TAB / "table5b_montecarlo_no_source_switch.csv")
_, mc_adcorr = monte_carlo(df, n=10000, ad_corr=-0.7); mc_adcorr.insert(0, "country", df.loc[NONUS, "country"]); mc_adcorr.to_csv(TAB / "table5f_montecarlo_AD_correlated_noise.csv")
_, mc10 = monte_carlo(df, n=10000, subset=ALL); mc10.insert(0, "country", df["country"]); mc10.to_csv(TAB / "table5c_montecarlo_ten_countries.csv")
# decomposition by source of uncertainty
from frindex import monte_carlo_component
dec = {}
for name, kw in [("weights only", dict(vary_weights=True)), ("normalisation and aggregation only", dict(vary_method=True)),
                 ("input noise only", dict(vary_noise=True)), ("data source only", dict(vary_source=True))]:
    _, m_ = monte_carlo_component(df, n=5000, **kw); dec[name] = m_
decomp = pd.concat({k: v[["rank_median", "rank_p05", "rank_p95", "share_top3", "share_bottom3"]] for k, v in dec.items()}, axis=1)
decomp.insert(0, "country", df.loc[NONUS, "country"]); decomp.to_csv(TAB / "table5e_montecarlo_decomposition.csv")
freq = pd.DataFrame({c: np.bincount(ranks_mc[:, j], minlength=len(NONUS) + 1)[1:] / len(ranks_mc) for j, c in enumerate(NONUS)}).T
freq.columns = [f"rank{r}" for r in range(1, len(NONUS) + 1)]; freq.index.name = "iso3"; freq.insert(0, "country", df.loc[NONUS, "country"]); freq.to_csv(TAB / "table5d_rank_frequency.csv")

# ---- Internal structure (nine countries) and ten-country comparison
evr, load, pcs = pca(S9)
pd.DataFrame({"explained_variance_ratio": evr}, index=load.columns).to_csv(TAB / "table6_pca_variance.csv")
load.to_csv(TAB / "table6b_pca_loadings.csv"); pcs.insert(0, "country", df.loc[NONUS, "country"]); pcs.to_csv(TAB / "table6c_pca_scores.csv")
S9.corr(method="spearman").to_csv(TAB / "table6d_component_spearman.csv"); S9.corr().to_csv(TAB / "table6e_component_pearson.csv")
S10 = normalise(raw_matrix(df)); evr10, load10, _ = pca(S10)
pd.DataFrame({"explained_variance_ratio": evr10}, index=load10.columns).to_csv(TAB / "table6f_pca_variance_ten.csv"); load10.to_csv(TAB / "table6g_pca_loadings_ten.csv")
imp10 = effective_importance(S10, aggregate(S10))
pd.DataFrame({"effective_importance_nine": imp, "effective_importance_ten": imp10}).to_csv(TAB / "table6h_effective_importance.csv")
# component correlation with log market size and log GDP
lg = np.log(df.loc[NONUS, "gdp_ppp_usd"]); ls = np.log(df.loc[NONUS, "rand_sales_2022_usd_bn"])
pd.DataFrame({k: {"spearman_vs_logGDP": S9[k].rank().corr(lg.rank()), "spearman_vs_logSales": S9[k].rank().corr(ls.rank())} for k in ORDER}).T.to_csv(TAB / "table6i_component_vs_size.csv")

# ---- External comparators (nine countries)
ext = pd.DataFrame({"country": df.loc[NONUS, "country"], "FRI_headline": base["FRI"], "FRI_rank": base["rank"],
    "Kolchinsky_Freeriding_Index_pct": df.loc[NONUS, "kolchinsky_freeriding_index_pct"],
    "ASPE_rev_to_GDP_ratio_all_innov": df.loc[NONUS, "rev_to_gdp_ratio_all_innov"], "ASPE_rev_to_pop_ratio_all_innov": df.loc[NONUS, "rev_to_pop_ratio_all_innov"],
    "Frech2026_contribution_per_capita_usd": df.loc[NONUS, "frech_contribution_per_capita_usd"], "PC1_score": pcs["PC1"]})
ext.to_csv(TAB / "table7_external_comparators.csv")
rows = []
def addrow(name, a, b):
    r, n = spearman(a, b); lo, hi = spearman_ci(r, n); p = spearman_perm_p(a, b)
    rows.append({"comparison": name, "spearman": r, "n": n, "ci95_low": lo, "ci95_high": hi, "perm_p": p})
addrow("Headline vs Kolchinsky-Xie", ext["FRI_headline"], ext["Kolchinsky_Freeriding_Index_pct"])
addrow("Headline vs ASPE revenue/GDP (inverted)", ext["FRI_headline"], -ext["ASPE_rev_to_GDP_ratio_all_innov"])
addrow("Headline vs ASPE revenue/population (inverted)", ext["FRI_headline"], -ext["ASPE_rev_to_pop_ratio_all_innov"])
addrow("Headline vs Frech per-capita contribution (inverted)", ext["FRI_headline"], -ext["Frech2026_contribution_per_capita_usd"])
for k in ORDER: addrow(f"Component {k} vs Kolchinsky-Xie", S9[k], ext["Kolchinsky_Freeriding_Index_pct"])
addrow("Adoption sub-index (A,D) vs Kolchinsky-Xie", S9[["A", "D"]].mean(1), ext["Kolchinsky_Freeriding_Index_pct"])
addrow("Payment sub-index (P,R) vs Kolchinsky-Xie", S9[["P", "R"]].mean(1), ext["Kolchinsky_Freeriding_Index_pct"])
pd.DataFrame(rows).to_csv(TAB / "table7b_external_spearman.csv", index=False)

contrib = S9 / len(ORDER); contrib.insert(0, "country", df.loc[NONUS, "country"]); contrib.to_csv(TAB / "table8_component_contributions.csv")

# ---- Revenue gap to GDP-share parity
c9 = df.loc[NONUS]
rs = c9["rev_share_all_innov_pct"] / 100; gsh = rs / c9["rev_to_gdp_ratio_all_innov"]   # GDP share of OECD
gap = (gsh - rs) * 100                                       # definition A: ratio -> 1 at the observed OECD total (others fixed)
delta_fp = (gsh.sum() - rs.sum()) / (1 - gsh.sum())           # definition B: fixed point where post-change revenue shares equal GDP shares
gap_fp = (gsh * (1 + delta_fp) - rs) * 100                    # each country's increase under definition B, pp of current OECD revenue
pd.DataFrame({"country": c9["country"], "rev_share_pct": c9["rev_share_all_innov_pct"], "gdp_share_pct": gsh * 100, "ratio": c9["rev_to_gdp_ratio_all_innov"],
              "multiple_to_parity": 1 / c9["rev_to_gdp_ratio_all_innov"], "gap_pp_of_OECD_innovative_revenue": gap,
              "gap_fixed_point_pp": gap_fp}).to_csv(TAB / "table9_revenue_gap_to_parity.csv")
pd.Series({"gap_A_pct_of_current_total": gap.sum(), "gap_B_fixed_point_pct": delta_fp * 100, "nine_rev_share_pct": rs.sum() * 100, "nine_gdp_share_pct": gsh.sum() * 100}, name="value").to_csv(TAB / "table9b_parity_totals.csv")

# ---- JSON for dashboard (ten countries; dashboard can exclude US)
out = {"generated": pd.Timestamp.today().strftime("%Y-%m-%d"),
       "components": {k: {"column": COMPONENTS[k][0], "direction": COMPONENTS[k][1], "label": COMPONENTS[k][2], "domain": COMPONENTS[k][3]} for k in ORDER},
       "countries": [{"iso3": c, "name": df.loc[c, "country"],
                      "raw": {k: (None if pd.isna(df.loc[c, COMPONENTS[k][0]]) else float(df.loc[c, COMPONENTS[k][0]])) for k in ORDER},
                      "gdp_pc_ppp_usd": float(df.loc[c, "gdp_pc_ppp_usd"]), "rev_share_all_innov_pct": float(df.loc[c, "rev_share_all_innov_pct"]),
                      "headline": ({"FRI": float(base.loc[c, "FRI"]), "rank": int(base.loc[c, "rank"])} if c in NONUS else None),
                      "mc": ({"rank_median": float(mc.loc[c, "rank_median"]), "rank_p05": float(mc.loc[c, "rank_p05"]), "rank_p95": float(mc.loc[c, "rank_p95"])} if c in NONUS else None)}
                     for c in ALL],
       "pca": {"explained_variance_ratio": [float(x) for x in evr], "loadings_PC1": {k: float(load.loc[k, "PC1"]) for k in ORDER}}}
(PROC / "results.json").write_text(json.dumps(out, indent=1))

print(base.sort_values("FRI", ascending=False)[["country", *ORDER, "FRI", "rank"]].round(1).to_string())
print("\nMC (nine, switches):\n", mc[["country", "rank_median", "rank_p05", "rank_p95", "share_top3", "share_bottom3"]].sort_values("rank_median").round(3).to_string())
print("\nMC (nine, no switches):\n", mc_noswitch[["country", "rank_median", "rank_p05", "rank_p95", "share_top3", "share_bottom3"]].sort_values("rank_median").round(3).to_string())
print("\nPCA EVR (nine):", np.round(evr, 3), "| ten:", np.round(evr10, 3)); print(load["PC1"].round(2).to_string())
print("\nEffective importance:", imp.round(2).to_dict())
print("\nSpearman vs headline:\n", pd.Series(rho).round(2).to_string())
print("\nExternal:\n", pd.DataFrame(rows).round(2).to_string())
print("\nSize:\n", pd.read_csv(TAB / "table6i_component_vs_size.csv", index_col=0).round(2).to_string())
print("\nLOCO:\n", lcoo.to_string())
print("\nGap pp (A, total fixed):", round(gap.sum(), 1), "| fixed point (B):", round(delta_fp * 100, 1))
print("\nMC A/D correlated noise:\n", mc_adcorr[["country","rank_median","share_top3","share_bottom3"]].sort_values("rank_median").round(3).to_string())
print("\nMC decomposition:\n", decomp.round(2).to_string())
