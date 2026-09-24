"""Generate paper/tables_figures.md (Table 1, Table 2, figure legends) and paper/supplement.md from analysis outputs."""
import pandas as pd, numpy as np, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
T, P = ROOT / "tables", ROOT / "paper"
df = pd.read_csv(ROOT / "data/processed/countries.csv", index_col="iso3")
t1 = pd.read_csv(T / "table1_raw_components.csv", index_col="iso3")
b = pd.read_csv(T / "table2_headline_index.csv", index_col="iso3")
mc = pd.read_csv(T / "table5_montecarlo_rank_intervals.csv", index_col="iso3")
mcn = pd.read_csv(T / "table5b_montecarlo_no_source_switch.csv", index_col="iso3")
mc10 = pd.read_csv(T / "table5c_montecarlo_ten_countries.csv", index_col="iso3")
rho = pd.read_csv(T / "table4_spearman_vs_headline.csv", index_col=0).iloc[:, 0]
ranks = pd.read_csv(T / "table3_rank_by_specification.csv", index_col="iso3")
lcoo = pd.read_csv(T / "table3c_leave_one_country_out_ranks.csv", index_col="iso3")
evr = pd.read_csv(T / "table6_pca_variance.csv", index_col=0).iloc[:, 0]; load = pd.read_csv(T / "table6b_pca_loadings.csv", index_col=0)
evr10 = pd.read_csv(T / "table6f_pca_variance_ten.csv", index_col=0).iloc[:, 0]
imp = pd.read_csv(T / "table6h_effective_importance.csv", index_col=0)
cs = pd.read_csv(T / "table6d_component_spearman.csv", index_col=0); sz = pd.read_csv(T / "table6i_component_vs_size.csv", index_col=0)
ext = pd.read_csv(T / "table7_external_comparators.csv", index_col="iso3"); extr = pd.read_csv(T / "table7b_external_spearman.csv")
gap = pd.read_csv(T / "table9_revenue_gap_to_parity.csv", index_col="iso3")
hta = pd.read_csv(ROOT / "data/raw/hta_thresholds.csv"); acc = pd.read_csv(ROOT / "data/raw/access_definitions.csv")
src = {"OECD BERD ISIC C21": "OECD", "ONS_BERD2024_ABPI": "ONS", "ABS_BERD2023_24": "ABS"}
order = b.index.tolist(); f2 = lambda v: "—" if pd.isna(v) else f"{v:.2f}"
LBL = {"P": "Brand price level", "R": "Revenue contribution", "A": "Availability", "D": "Interval to reimbursement", "I": "Pharmaceutical R&D"}

L = ["# Tables and Figure Legends", "", "## Table 1. Components of the Free-Rider Index and raw values (United States shown as the reference point)", "",
     "| Country | P: Brand-name originator price, % of US (2022) | R: Innovative-drug revenue share ÷ GDP share (2020-2025) | A: US-first new drugs publicly reimbursed by 2023, % | D: Mean interval from US launch to public reimbursement, years | I: Pharmaceutical business R&D, % of GDP (year; source) | GDP per capita, PPP US$ thousand (2025) |",
     "|---|---:|---:|---:|---:|---:|---:|"]
for c in ["USA"] + order:
    r = t1.loc[c]
    L.append(f"| {r.country}{' (reference)' if c == 'USA' else ''} | {r.P:.1f} | {r.R:.2f} | {r.A:.1f} | {r.D:.2f} | {r.I:.3f} ({int(r.pharma_berd_year)}; {src.get(df.loc[c, 'pharma_berd_source'], df.loc[c, 'pharma_berd_source'])}) | {r.gdp_pc_ppp_usd / 1000:.1f} |")
L += ["", "Sources: P, RAND international price comparison using IQVIA MIDAS 2022 manufacturer prices, bilateral US-volume-weighted index for brand-name originator drugs (Appendix Table B.1), expressed as the comparison country's price relative to the United States = 100. R, HHS-ASPE analysis of IQVIA MIDAS 2020-2025, Table 3 (all innovative branded products). A and D, Philipson et al, 225 novel drugs first launched in the United States in 2014-2019 and their public reimbursement status in 15 markets by 2023 (PhRMA launch dataset; industry-compiled; no microdata released); D is conditional on reimbursement and the interval includes sponsor filing, regulatory review, and payer decision; US values are reference values by construction. I, OECD business enterprise R&D by industry (ISIC Rev. 4 division 21) divided by GDP in purchasing-power-parity US dollars for the same year; United Kingdom from the Office for National Statistics product-group series (£9.3 billion, 2024); Australia from the Australian Bureau of Statistics line for ANZSIC subdivision 18, basic chemical and chemical product manufacturing (A$948 million, 2023-24; an upper bound). GDP per capita from the World Bank. For the index, P, R, A, and I are inverted so that higher normalized scores indicate more apparent free-riding; normalization is across the nine non-US countries. Abbreviations: ABS, Australian Bureau of Statistics; GDP, gross domestic product; OECD, Organisation for Economic Co-operation and Development; ONS, Office for National Statistics; PPP, purchasing power parity; R&D, research and development.",
      "", "## Table 2. Robustness of the headline index: rank uncertainty, alternative specifications, and internal structure", "",
      "**Panel A. Headline score and rank uncertainty across 10,000 Monte Carlo specifications (nine countries)**", "",
      "| Country | Headline score (0-100) | Headline rank | Median rank (5th-95th percentile) | Share of specifications in top 3 | Share of specifications in bottom 3 |", "|---|---:|---:|---:|---:|---:|"]
for c in order:
    L.append(f"| {b.loc[c, 'country']} | {b.loc[c, 'FRI']:.1f} | {int(b.loc[c, 'rank'])} | {mc.loc[c, 'rank_median']:.0f} ({mc.loc[c, 'rank_p05']:.0f}-{mc.loc[c, 'rank_p95']:.0f}) | {mc.loc[c, 'share_top3'] * 100:.0f}% | {mc.loc[c, 'share_bottom3'] * 100:.0f}% |")
L += ["", "**Panel B. Spearman rank correlation of alternative specifications with the headline index**", "", "| Specification | ρ | Specification | ρ |", "|---|---:|---|---:|"]
items = list(rho.items()); half = (len(items) + 1) // 2
fmt = lambda k: k.replace("drop_", "Drop component ")
for i in range(half):
    l = items[i]; r = items[i + half] if i + half < len(items) else None
    L.append(f"| {fmt(l[0])} | {l[1]:.2f} | {fmt(r[0]) if r else ''} | {f'{r[1]:.2f}' if r else ''} |")
L += ["", "**Panel C. Internal structure of the five normalized components (nine countries)**", "", "| Component | PC1 loading | PC2 loading | Effective importance (squared correlation with composite) | Spearman ρ with log GDP |", "|---|---:|---:|---:|---:|"]
for k in ["P", "R", "A", "D", "I"]:
    L.append(f"| {LBL[k]} | {load.loc[k, 'PC1']:.2f} | {load.loc[k, 'PC2']:.2f} | {imp.loc[k, 'effective_importance_nine']:.2f} | {sz.loc[k, 'spearman_vs_logGDP']:.2f} |")
L.append(f"| Variance explained | {evr.iloc[0] * 100:.1f}% | {evr.iloc[1] * 100:.1f}% | | |")
L += ["", "Monte Carlo specifications draw weights from a flat Dirichlet distribution; a normalization method (min-max, z-score, rank, log min-max); an aggregation rule (arithmetic, geometric); calibrated input noise (log-normal with σ = 0.05 for P and R and σ = 0.50 for I; normal with SD 3 percentage points for A and 0.3 years for D); and, for P, R, and I, a randomly chosen data source among the alternatives listed below. Shares of specifications are frequencies under this prior, not probabilities. Specifications: S1 domain weights (one third each for payment, adoption, and R&D); S2 payment components only; S3 adoption components only; S4 brand price only; S5 geometric aggregation; S6 z-score normalization; S7 rank normalization; S8 log min-max normalization; S9 all-drug price index in place of brand price; S10 brand price divided by relative GDP per capita; S11 ability-to-pay adjustment of both payment components (income elasticity 1.3); S12 US net-price adjustment (US prices and revenue reduced by 37.7%); S13 revenue contribution for drugs launched after 2020; S14 delay imputed for non-reimbursed drugs (6.5-year follow-up horizon); S15 EFPIA W.A.I.T. availability and time to availability substituted for the five European countries; S16 association-based R&D series; S17 industry-sponsored trial starts per million population replace R&D input; S18 R&D input dropped; S19 six components adding the OECD implied R&D tax subsidy rate; S20 seven components adding tax subsidy and trial hosting; S21 each normalized component residualized on log GDP before aggregation; S22 ten countries including the United States. Abbreviations: GDP, gross domestic product; PC, principal component; R&D, research and development.",
      "", "## Figure legends", "",
      "**Figure 1. Headline Free-Rider Index and rank uncertainty (nine countries).** (A) Equal-weight index with the contribution of each normalized component (each contributes one fifth of its 0-100 score). (B) Rank of each country across 10,000 Monte Carlo specifications: dot, median; horizontal bar, 5th-95th percentile; red tick, headline rank. Higher scores indicate lower brand-name prices, lower innovative-drug revenue relative to GDP, fewer and later reimbursed US-first drugs, and lower pharmaceutical R&D intensity than the other eight countries. The United States is the reference point for price, availability, and interval and is not ranked. GDP, gross domestic product; R&D, research and development.",
      "", "**Figure 2. Country rank under alternative specifications and with each component dropped.** Cells show each country's rank among the nine non-US countries (1 = most apparent free-riding) under the headline specification (S0), 21 alternative specifications (S1-S21; defined in Table 2), and five indices in which one component is dropped (−P brand price, −R revenue contribution, −A availability, −D interval, −I pharmaceutical R&D).",
      "", "**Figure 3. Decomposition of the comparison with the Kolchinsky-Xie Freeriding Index (seven overlapping countries).** Left, headline index; center, payment sub-index (mean of normalized brand-price and revenue-contribution scores); right, adoption sub-index (mean of normalized availability and interval scores), each plotted against the Kolchinsky-Xie index, a net brand-price measure adjusted for income. ρ, Spearman rank correlation. The payment sub-index reproduces the price-based measure; the adoption sub-index is unrelated to it."]
(P / "tables_figures.md").write_text("\n".join(L) + "\n")

S = ["# Supplemental Materials", "", "Who Pays for Pharmaceutical Innovation? A Reproducible Multidimensional Free-Rider Index for Ten High-Income Countries", "",
     "All supplementary tables and figures are generated by the released code (folders tables/ and figures/ in the repository).", "",
     "## Appendix Table S1. Data sources and provenance", "", "| Variable | Source | Reference period | Notes |", "|---|---|---|---|",
     "| Brand price level (P) | Mulcahy AW, Schwam D, Lovejoy SL. RAND RR-A788-3 (2024), Appendix Table B.1, column 'Brand-Name Originator Drugs' | 2022 | Bilateral index, US volume weights, presentations sold in both markets; IQVIA MIDAS manufacturer prices; converted to comparison-country price as % of US. All-drug index (Table B.2) and US net-price column used in S9 and S12 |",
     "| Revenue contribution (R) | HHS-ASPE Issue Brief (Murphy, June 2026), Table 3, column 2 | 2020-2025 | Share of OECD revenue for 'Innovative Branded Products' (IQVIA MIDAS) divided by share of OECD GDP |",
     "| Availability (A), Interval (D) | Philipson et al, University of Chicago ECCHC policy brief (August 11, 2026), Table 1 and Section 2 | US launches 2014-2019; reimbursement to 2023 | PhRMA Research dataset (industry-compiled; no microdata or confidence intervals released); Canada defined as provinces covering at least 50% of population; the brief itself attributes delays to 'foreign reimbursement delays and manufacturers' international launch strategies' |",
     "| Pharmaceutical R&D (I) | OECD BERD by industry, ISIC Rev. 4 C21, USD PPP current prices; ONS (UK); ABS (Australia); World Bank GDP PPP | 2021-2024 | Exact values, years and bases in data/raw/manual_inputs.csv, national_overrides.csv and national_fallback.csv |",
     "| Alternative R&D indicators | OECD implied R&D tax subsidy rates (2025); ClinicalTrials.gov API v2 industry-sponsored interventional trials starting 2023-2025 by site country; OECD GBARD socio-economic objective 'health' (NABS07) | 2023-2025 | GBARD-health is not used because countries that fund universities through general university funds (e.g., Switzerland, 0.001% of GDP) do not allocate it to health, so the series is not comparable |",
     "| GDP, GDP per capita, population | World Bank World Development Indicators | latest (2025) | NY.GDP.MKTP.CD, NY.GDP.MKTP.PP.CD, NY.GDP.PCAP.PP.CD, SP.POP.TOTL, NY.GDP.MKTP.CN, PA.NUS.PPP |",
     "| External comparators | Kolchinsky and Xie (2025); ASPE (2026) Tables 2-3; Frech et al (2026) | 2018-2025 | See Appendix Table S6 |",
     "", "## Appendix Table S2. Normalized component scores (0-100; higher = more apparent free-riding), headline specification (nine countries)", "",
     "| Country | P | R | A | D | I | Index | Rank |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
for c in order:
    r = b.loc[c]; S.append(f"| {r.country} | {r.P:.1f} | {r.R:.1f} | {r.A:.1f} | {r.D:.1f} | {r.I:.1f} | {r.FRI:.1f} | {int(r['rank'])} |")
cols = ranks.columns[1:]
S += ["", "## Appendix Table S3. Rank by specification (full matrix; S22 includes the United States, ranked among ten)", "",
      "| Country | " + " | ".join(c.split(" ", 1)[0] if c.startswith("S") else c.replace("drop_", "−") for c in cols) + " |", "|---|" + "---:|" * len(cols)]
for c in ranks.index:
    S.append(f"| {ranks.loc[c, 'country']} | " + " | ".join("—" if pd.isna(v) else f"{int(v)}" for v in ranks.loc[c, cols]) + " |")
S += ["", "Specifications: " + "; ".join(cols[:23]) + ". −X: component X dropped (equal weights on the remaining four).", "",
      "## Appendix Table S4. Spearman correlations among normalized components and with market size (nine countries)", "", "| | P | R | A | D | I | log GDP (PPP) | log 2022 drug sales |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
for k in cs.index: S.append(f"| {k} | " + " | ".join(f"{cs.loc[k, j]:.2f}" for j in cs.columns) + f" | {sz.loc[k, 'spearman_vs_logGDP']:.2f} | {sz.loc[k, 'spearman_vs_logSales']:.2f} |")
S += ["", f"Principal components, nine countries: PC1 {evr.iloc[0]*100:.1f}%, PC2 {evr.iloc[1]*100:.1f}%, PC3 {evr.iloc[2]*100:.1f}%. Ten countries including the United States: PC1 {evr10.iloc[0]*100:.1f}%, PC2 {evr10.iloc[1]*100:.1f}% (the US outlier produces the apparent one-dimensionality). Effective importance (squared correlation with the composite), nine countries: " + ", ".join(f"{k} {imp.loc[k,'effective_importance_nine']:.2f}" for k in ["P","R","A","D","I"]) + ".",
      "", "## Appendix Table S5. Cost-effectiveness thresholds and HTA decision rules (descriptive; not an index component)", "",
      "| Country | Agency | Threshold type | Value or rule | Note | Source |", "|---|---|---|---|---|---|"]
for _, r in hta.iterrows(): S.append(f"| {r.country} | {r.agency} | {r.threshold_type} | {r.threshold_local} | {r.threshold_note} | {r.source} |")
S += ["", "## Appendix Table S6. External single-metric measures and rank correlations with the headline index", "",
      "| Country | Headline index | Kolchinsky-Xie Freeriding Index, % | ASPE revenue share ÷ GDP share | ASPE revenue share ÷ population share | Frech et al contribution per capita, US$ (2018) |", "|---|---:|---:|---:|---:|---:|"]
for c in order:
    r = ext.loc[c]
    S.append(f"| {r.country} | {r.FRI_headline:.1f} | {f2(r.Kolchinsky_Freeriding_Index_pct)} | {f2(r.ASPE_rev_to_GDP_ratio_all_innov)} | {f2(r.ASPE_rev_to_pop_ratio_all_innov)} | {'—' if pd.isna(r.Frech2026_contribution_per_capita_usd) else f'{r.Frech2026_contribution_per_capita_usd:.0f}'} |")
S += ["", "| Comparison | Spearman ρ | n | Fisher 95% interval | Permutation p |", "|---|---:|---:|---|---:|"]
for _, r in extr.iterrows(): S.append(f"| {r.comparison} | {r.spearman:.2f} | {int(r.n)} | {r.ci95_low:.2f} to {r.ci95_high:.2f} | {r.perm_p:.2f} |")
wait = df.loc[["DEU", "CHE", "GBR", "ITA", "FRA"], ["country", "reimb_share_2023_pct", "wait_availability_pct", "reimb_delay_years", "wait_mean_days", "wait_median_days"]]
S += ["", "## Appendix Table S7. Concordance of the two adoption data sources for the five European countries", "",
      "| Country | Share of US-first drugs reimbursed by 2023, % (Philipson et al) | W.A.I.T. availability, % of 168 EMA approvals 2021-2024 | Mean interval after US launch, years (Philipson et al) | W.A.I.T. mean time to availability, days | W.A.I.T. median, days |", "|---|---:|---:|---:|---:|---:|"]
for c in wait.index:
    r = wait.loc[c]; S.append(f"| {r.country} | {r.reimb_share_2023_pct:.1f} | {r.wait_availability_pct:.1f} | {r.reimb_delay_years:.2f} | {r.wait_mean_days:.0f} | {r.wait_median_days:.0f} |")
sp_av = wait.reimb_share_2023_pct.rank().corr(wait.wait_availability_pct.rank()); sp_dm = wait.reimb_delay_years.rank().corr(wait.wait_mean_days.rank()); sp_dmed = wait.reimb_delay_years.rank().corr(wait.wait_median_days.rank()); pe_d = wait.reimb_delay_years.corr(wait.wait_mean_days)
S += ["", f"Spearman rank correlation between sources: availability {sp_av:.2f}; interval versus W.A.I.T. mean {sp_dm:.2f} (Pearson {pe_d:.2f}); interval versus W.A.I.T. median {sp_dmed:.2f}. The W.A.I.T. interval starts at EU (or, for England and Switzerland, national) marketing authorization and therefore excludes regulatory lag, whereas the Philipson interval starts at US launch and includes sponsor filing and regulatory review. Substituting the W.A.I.T. values for the five European countries (specification S15) leaves the nine-country ranking unchanged (ρ = {rho['S15 W.A.I.T. adoption data for EU-5']:.2f}).",
      "", "## Appendix Table S8. Operational meaning of 'public reimbursement' and of the interval by country", "", "| Country | Public reimbursement means | The interval contains | Not captured |", "|---|---|---|---|"]
for _, r in acc.iterrows(): S.append(f"| {r.country} | {r.operational_meaning_of_public_reimbursement} | {r.what_the_interval_contains} | {r.not_captured} |")
S += ["", "## Appendix Table S9. Monte Carlo rank statistics under alternative designs", "",
      "| Country | Nine countries, without source switching: median (5th-95th) | Top 3 | Bottom 3 | Ten countries including US: median (5th-95th) | Top 3 |", "|---|---|---:|---:|---|---:|"]
for c in order:
    S.append(f"| {b.loc[c,'country']} | {mcn.loc[c,'rank_median']:.0f} ({mcn.loc[c,'rank_p05']:.0f}-{mcn.loc[c,'rank_p95']:.0f}) | {mcn.loc[c,'share_top3']*100:.0f}% | {mcn.loc[c,'share_bottom3']*100:.0f}% | {mc10.loc[c,'rank_median']:.0f} ({mc10.loc[c,'rank_p05']:.0f}-{mc10.loc[c,'rank_p95']:.0f}) | {mc10.loc[c,'share_top3']*100:.0f}% |")
S.append(f"| United States | — | — | — | {mc10.loc['USA','rank_median']:.0f} ({mc10.loc['USA','rank_p05']:.0f}-{mc10.loc['USA','rank_p95']:.0f}) | {mc10.loc['USA','share_top3']*100:.0f}% |")
S += ["", "## Appendix Table S10. Leave-one-country-out ranks (rank among the remaining eight)", "",
      "| Country | " + " | ".join(lcoo.columns[1:]) + " |", "|---|" + "---:|" * (len(lcoo.columns) - 1)]
for c in order: S.append(f"| {lcoo.loc[c,'country']} | " + " | ".join("—" if pd.isna(v) else f"{int(v)}" for v in lcoo.loc[c].iloc[1:]) + " |")
S += ["", "## Appendix Table S11. Innovative-drug revenue relative to GDP share and the gap to parity", "",
      "| Country | Share of OECD innovative-drug revenue, % | Revenue share ÷ GDP share | Multiple required to reach parity | Gap, percentage points of OECD innovative-drug revenue |", "|---|---:|---:|---:|---:|"]
for c in order: S.append(f"| {gap.loc[c,'country']} | {gap.loc[c,'rev_share_pct']:.2f} | {gap.loc[c,'ratio']:.2f} | {gap.loc[c,'multiple_to_parity']:.2f} | {gap.loc[c,'gap_pp_of_OECD_innovative_revenue']:.2f} |")
S.append(f"| Total, nine countries | {gap.rev_share_pct.sum():.1f} | | | {gap.gap_pp_of_OECD_innovative_revenue.sum():.1f} |")
S += ["", "Source: HHS-ASPE (2026) Tables 1 and 3. Parity means a revenue share equal to the GDP share.", "",
      "## Appendix Figure S1. Principal component biplot (nine countries)", "", "File figures/figS1_pca_biplot.png.", "",
      "## Appendix Figure S2. Rank-frequency matrix", "", "File figures/figS2_rank_frequency.png. Share of 10,000 Monte Carlo specifications in which each country attains each rank.", "",
      "## Appendix Figure S3. Payment and adoption domains", "", "File figures/figS3_domain_map.png. Horizontal axis: mean of normalized brand-price and revenue-contribution scores; vertical axis: mean of normalized availability and interval scores; shading: normalized pharmaceutical R&D score; bubble area proportional to share of OECD innovative-drug revenue.", "",
      "## Appendix Figure S4. Leave-one-country-out ranks", "", "File figures/figS4_leave_one_country_out.png.", "",
      "## Appendix S12. ELEVATE-GenAI items relevant to AI-assisted code development", "",
      "- Tool: Claude Fable 5.1 (Anthropic), accessed through Claude Code, September 2026.",
      "- Tasks: drafting Python analysis and figure scripts, drafting data-provenance files, compiling source lists, and drafting manuscript text under the author's specification.",
      "- Human oversight: the author specified the index design, reviewed every script, executed all code, checked outputs against hand calculations (min-max scores and equal-weight means for two countries), and verified every transcribed data value against the cited source document.",
      "- Reproducibility: all outputs are regenerated deterministically by the released scripts (Monte Carlo seed 2026).",
      "- Limitations: no AI-generated content was used as a data source; the model did not access proprietary data.",
      "", "## Supplement references", "",
      "Bae EY, Kim HJ, Lee HJ, et al. Eight-year experience of using HTA in drug reimbursement: South Korea. Health Policy. 2016;120(6):612-620. doi:10.1016/j.healthpol.2016.03.013",
      "Claxton K, Martin S, Soares M, et al. Methods for the estimation of the National Institute for Health and Care Excellence cost-effectiveness threshold. Health Technol Assess. 2015;19(14):1-504. doi:10.3310/hta19140",
      "Edney LC, Haji Ali Afzali H, Cheng TC, Karnon J. Estimating the reference incremental cost-effectiveness ratio for the Australian health system. Pharmacoeconomics. 2018;36(2):239-252. doi:10.1007/s40273-017-0585-2",
      "Harris AH, Hill SR, Chin G, Li JJ, Walkom E. The role of value for money in public insurance coverage decisions for drugs in Australia: a retrospective analysis 1994-2004. Med Decis Making. 2008;28(5):713-722. doi:10.1177/0272989X08315247",
      "Murphy P, Griffin S, Walker S, et al. Cost-effectiveness thresholds in policy and practice: do HTA guidelines align with estimates of health opportunity cost? Health Econ Policy Law. 2026. doi:10.1017/S1744133126100395",
      "Association of the British Pharmaceutical Industry; Charles River Associates. Benchmarking the UK's Cost-Effectiveness Threshold: Findings from International Comparison. February 2026.",
      "Rawson NSB. Reimbursement recommendations for new medicines in Canada: current trends in an uncertain era. Canadian Health Policy. April 2026.",
      "Zhang K, Garau M. International Cost-Effectiveness Thresholds and Modifiers for HTA Decision Making. Office of Health Economics; 2020.",
      "Swiss Federal Supreme Court. BGE 136 V 395 (Myozyme), 23 November 2010.",
      "Ministry of Health, Labour and Welfare (Japan). Notification on the cost-effectiveness evaluation system, 2026 edition; Notification on NHI price listing of new drugs, 2026 edition (Japanese).",
      "Pharmaceutical Benefits Scheme (Australia). PBAC outcomes and time to listing. https://www.pbs.gov.au/info/industry/listing/elements/pbac-meetings/pbac-outcomes"]
(P / "supplement.md").write_text("\n".join(S) + "\n")
print("tables_figures.md and supplement.md written")
