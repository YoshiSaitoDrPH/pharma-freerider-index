"""Generate paper/tables_figures.md (Table 1, Table 2, figure legends) and paper/supplement.md from analysis outputs."""
import pandas as pd, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
T, P = ROOT / "tables", ROOT / "paper"
df = pd.read_csv(ROOT / "data/processed/countries.csv", index_col="iso3")
t1 = pd.read_csv(T / "table1_raw_components.csv", index_col="iso3")
b = pd.read_csv(T / "table2_headline_index.csv", index_col="iso3")
mc = pd.read_csv(T / "table5_montecarlo_rank_intervals.csv", index_col="iso3")
rho = pd.read_csv(T / "table4_spearman_vs_headline.csv", index_col=0).iloc[:, 0]
ranks = pd.read_csv(T / "table3_rank_by_specification.csv", index_col="iso3")
evr = pd.read_csv(T / "table6_pca_variance.csv", index_col=0).iloc[:, 0]
load = pd.read_csv(T / "table6b_pca_loadings.csv", index_col=0)
cs = pd.read_csv(T / "table6d_component_spearman.csv", index_col=0)
ext = pd.read_csv(T / "table7_external_comparators.csv", index_col="iso3")
hta = pd.read_csv(ROOT / "data/raw/hta_thresholds.csv")
src = {"OECD BERD ISIC C21": "OECD", "ONS_BERD2024_ABPI": "ONS", "ABS_BERD2023_24": "ABS"}
order = b.index.tolist()
f2 = lambda v: "—" if pd.isna(v) else f"{v:.2f}"

L = ["# Tables and Figure Legends", "", "## Table 1. Components of the Free-Rider Index and raw values for ten high-income countries", "",
     "| Country | P: Price level, all drugs, % of US (2022) | R: Innovative-drug revenue share ÷ GDP share (2020-2025) | A: US-first new drugs publicly reimbursed by 2023, % | D: Mean reimbursement delay after US launch, years | I: Pharmaceutical business R&D, % of GDP (year; source) | GDP per capita, PPP US$ thousand (2025) |",
     "|---|---:|---:|---:|---:|---:|---:|"]
for c in order:
    r = t1.loc[c]
    L.append(f"| {r.country} | {r.P:.1f} | {r.R:.2f} | {r.A:.1f} | {r.D:.2f} | {r.I:.3f} ({int(r.pharma_berd_year)}; {src.get(df.loc[c, 'pharma_berd_source'], df.loc[c, 'pharma_berd_source'])}) | {r.gdp_pc_ppp_usd / 1000:.1f} |")
L += ["", "Sources: P, RAND international price comparison using IQVIA MIDAS 2022 data, bilateral US-volume-weighted index, all drugs (Appendix Table B.2, main specification), expressed as the comparison country's price relative to the United States = 100. R, HHS-ASPE analysis of IQVIA MIDAS 2020-2025, Table 3 (all innovative branded products). A and D, Philipson et al, 225 novel drugs first launched in the United States in 2014-2019 and their public reimbursement status in 15 markets by 2023; US values are reference values by construction. I, OECD business enterprise R&D by industry (ISIC Rev. 4 division 21) divided by GDP in purchasing-power-parity US dollars for the same year; United Kingdom from the Office for National Statistics product-group series (£9.3 billion, 2024); Australia from the Australian Bureau of Statistics chemical and pharmaceutical manufacturing line (A$948 million, 2023-24). GDP per capita from the World Bank. For the index, P, R, A, and I are inverted so that higher normalized scores indicate more apparent free-riding. Abbreviations: ABS, Australian Bureau of Statistics; GDP, gross domestic product; OECD, Organisation for Economic Co-operation and Development; ONS, Office for National Statistics; PPP, purchasing power parity; R&D, research and development.",
      "", "## Table 2. Robustness of the headline index: rank uncertainty, alternative specifications, and internal structure", "",
      "**Panel A. Headline score and rank uncertainty across 10,000 Monte Carlo specifications**", "",
      "| Country | Headline score (0-100) | Headline rank | Median rank (5th-95th percentile) | Probability of top-3 rank | Probability of bottom-3 rank among non-US countries |",
      "|---|---:|---:|---:|---:|---:|"]
for c in order:
    L.append(f"| {b.loc[c, 'country']} | {b.loc[c, 'FRI']:.1f} | {int(b.loc[c, 'rank'])} | {mc.loc[c, 'rank_median']:.0f} ({mc.loc[c, 'rank_p05']:.0f}-{mc.loc[c, 'rank_p95']:.0f}) | {mc.loc[c, 'p_top3'] * 100:.0f}% | {mc.loc[c, 'p_bottom3'] * 100:.0f}% |")
L += ["", "**Panel B. Spearman rank correlation of alternative specifications with the headline index**", "", "| Specification | ρ | Specification | ρ |", "|---|---:|---|---:|"]
items = list(rho.items())[1:]; half = (len(items) + 1) // 2
fmt = lambda k: k.replace("drop_", "Drop component ")
for i in range(half):
    l = items[i]; r = items[i + half] if i + half < len(items) else None
    L.append(f"| {fmt(l[0])} | {l[1]:.2f} | {fmt(r[0]) if r else ''} | {f'{r[1]:.2f}' if r else ''} |")
L += ["", "**Panel C. Principal component analysis of the five normalized components**", "", "| Component | PC1 loading | PC2 loading |", "|---|---:|---:|"]
for k, lab in zip(["P", "R", "A", "D", "I"], ["Price level", "Revenue contribution", "Availability", "Delay", "Pharmaceutical R&D"]):
    L.append(f"| {lab} | {load.loc[k, 'PC1']:.2f} | {load.loc[k, 'PC2']:.2f} |")
L.append(f"| Variance explained | {evr.iloc[0] * 100:.1f}% | {evr.iloc[1] * 100:.1f}% |")
L += ["", "Monte Carlo specifications draw weights from a flat Dirichlet distribution, a normalization method (min-max, z-score, rank), an aggregation rule (arithmetic, geometric), and independent ±10% uniform perturbations of each input. The bottom-3 probability for the United States is 100% by construction. Specifications: S1 domain weights (one third each for payment, access, and R&D); S2 payment components only; S3 access components only; S4 price only; S5 geometric aggregation; S6 z-score normalization; S7 rank normalization; S8 income-adjusted price; S9 revenue contribution for drugs launched after 2020; S10 nine non-US countries; S11 association-based R&D series. Abbreviations: PC, principal component; R&D, research and development.",
      "", "## Figure legends", "",
      "**Figure 1. Headline Free-Rider Index and rank uncertainty.** (A) Equal-weight index for ten high-income countries with the contribution of each normalized component (each contributes one fifth of its 0-100 score). (B) Rank of each country across 10,000 Monte Carlo specifications: dot, median; horizontal bar, 5th-95th percentile; red tick, headline rank. Higher scores indicate lower relative prices, lower revenue contribution relative to GDP, fewer and later reimbursed US-first drugs, and lower pharmaceutical R&D intensity than peers. GDP, gross domestic product; R&D, research and development.",
      "", "**Figure 2. Country rank under alternative specifications and jackknife.** Cells show each country's rank (1 = most apparent free-riding) under the headline specification (S0), 11 alternative specifications (S1-S11; defined in Table 2), and five jackknife indices in which one component is dropped (−P price, −R revenue contribution, −A availability, −D delay, −I pharmaceutical R&D). The United States is not scored in S10.",
      "", "**Figure 3. Payment and access domains.** Horizontal axis: mean of normalized price-level and revenue-contribution scores. Vertical axis: mean of normalized availability and delay scores. Shading: normalized pharmaceutical R&D score (dark = high R&D intensity). Bubble area is proportional to each country's share of OECD innovative-drug revenue in 2020-2025. Dashed lines mark the midpoint of each axis. OECD, Organisation for Economic Co-operation and Development; R&D, research and development.",
      "", "**Figure 4. Comparison with existing single-metric measures.** Headline index plotted against (left) the Kolchinsky-Xie Freeriding Index (seven overlapping countries), (center) the HHS-ASPE ratio of innovative-drug revenue share to GDP share (ten countries; axis inverted so that right = less contribution), and (right) Frech et al's estimated per-capita contribution to global pharmaceutical R&D (seven countries; inverted). ρ, Spearman rank correlation, signed so that positive values indicate agreement in the direction of free-riding. GDP, gross domestic product; HHS-ASPE, Office of the Assistant Secretary for Planning and Evaluation, US Department of Health and Human Services."]
(P / "tables_figures.md").write_text("\n".join(L) + "\n")

S = ["# Supplemental Materials", "", "Who Pays for Pharmaceutical Innovation? A Reproducible Multidimensional Free-Rider Index for Ten High-Income Countries", "",
     "All supplementary tables and figures are generated by the code at https://github.com/YoshiSaitoDrPH/pharma-freerider-index (folders tables/ and figures/).", "",
     "## Appendix Table S1. Data sources and provenance", "", "| Variable | Source | Reference period | Notes |", "|---|---|---|---|",
     "| Price level (P) | Mulcahy AW, Schwam D, Lovejoy SL. RAND RR-A788-3 (2024), Appendix Table B.2, Scenario 4 (main results) | 2022 | Bilateral index, US volume weights, all drugs sold in both markets; converted to comparison-country price as % of US |",
     "| Revenue contribution (R) | HHS-ASPE Issue Brief (Murphy, June 2026), Table 3, column 2 | 2020-2025 | Share of OECD revenue for 'Innovative Branded Products' (IQVIA MIDAS) divided by share of OECD GDP |",
     "| Availability (A), Delay (D) | Philipson et al, University of Chicago ECCHC policy brief (August 2026), Table 1 and Section 2 | US launches 2014-2019; reimbursement to 2023 | PhRMA Research dataset; Canada defined as provinces covering at least 50% of population |",
     "| Pharmaceutical R&D (I) | OECD BERD by industry, ISIC Rev. 4 C21, USD PPP current prices; ONS (UK); ABS (Australia); World Bank GDP PPP | 2021-2024 | Exact values, years and bases in data/raw/manual_inputs.csv, national_overrides.csv and national_fallback.csv |",
     "| GDP, GDP per capita, population | World Bank World Development Indicators | latest (2025) | NY.GDP.MKTP.CD, NY.GDP.MKTP.PP.CD, NY.GDP.PCAP.PP.CD, SP.POP.TOTL, NY.GDP.MKTP.CN, PA.NUS.PPP |",
     "| External comparators | Kolchinsky and Xie (2025); ASPE (2026) Tables 2-3; Frech et al (2026) | 2018-2025 | See Appendix Table S6 |",
     "", "## Appendix Table S2. Normalized component scores (0-100; higher = more apparent free-riding), headline specification", "",
     "| Country | P | R | A | D | I | Index | Rank |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
for c in order:
    r = b.loc[c]; S.append(f"| {r.country} | {r.P:.1f} | {r.R:.1f} | {r.A:.1f} | {r.D:.1f} | {r.I:.1f} | {r.FRI:.1f} | {int(r['rank'])} |")
cols = ranks.columns[1:]
S += ["", "## Appendix Table S3. Rank by specification (full matrix)", "",
      "| Country | " + " | ".join(c.split(" ", 1)[0] if c.startswith("S") else c.replace("drop_", "−") for c in cols) + " |", "|---|" + "---:|" * len(cols)]
for c in order:
    S.append(f"| {ranks.loc[c, 'country']} | " + " | ".join("—" if pd.isna(v) else f"{int(v)}" for v in ranks.loc[c, cols]) + " |")
S += ["", "Specifications: " + "; ".join(cols[:12]) + ". −X: component X dropped (equal weights on the remaining four).", "",
      "## Appendix Table S4. Spearman correlations among normalized components", "", "| | P | R | A | D | I |", "|---|---:|---:|---:|---:|---:|"]
for k in cs.index: S.append(f"| {k} | " + " | ".join(f"{cs.loc[k, j]:.2f}" for j in cs.columns) + " |")
S += ["", "## Appendix Table S5. Cost-effectiveness thresholds and HTA decision rules (descriptive; not an index component)", "",
      "| Country | Agency | Threshold type | Value or rule | Note | Source |", "|---|---|---|---|---|---|"]
for _, r in hta.iterrows(): S.append(f"| {r.country} | {r.agency} | {r.threshold_type} | {r.threshold_local} | {r.threshold_note} | {r.source} |")
S += ["", "## Appendix Table S6. External single-metric measures used for comparison", "",
      "| Country | Headline index | Kolchinsky-Xie Freeriding Index, % | ASPE revenue share ÷ GDP share | ASPE revenue share ÷ population share | Frech et al contribution per capita, US$ (2018) |", "|---|---:|---:|---:|---:|---:|"]
for c in order:
    r = ext.loc[c]
    S.append(f"| {r.country} | {r.FRI_headline:.1f} | {f2(r.Kolchinsky_Freeriding_Index_pct)} | {f2(r.ASPE_rev_to_GDP_ratio_all_innov)} | {f2(r.ASPE_rev_to_pop_ratio_all_innov)} | {'—' if pd.isna(r.Frech2026_contribution_per_capita_usd) else f'{r.Frech2026_contribution_per_capita_usd:.0f}'} |")
S += ["", "## Appendix Figure S1. Principal component biplot", "", "File figures/figS1_pca_biplot.png. Arrows show component loadings on PC1 and PC2; points show country scores.", "",
      "## Appendix Figure S2. Rank-frequency matrix", "", "File figures/figS2_rank_frequency.png. Share of 10,000 Monte Carlo specifications in which each country attains each rank.", "",
      "## Appendix S3. ELEVATE-GenAI items relevant to AI-assisted code development", "",
      "- Tool: Claude Fable 5.1 (Anthropic), accessed through Claude Code, September 2026.",
      "- Tasks: drafting Python analysis and figure scripts, drafting data-provenance files, compiling source lists, and drafting manuscript text under the author's specification.",
      "- Human oversight: the author specified the index design, reviewed every script, executed all code, checked outputs against hand calculations (min-max scores and equal-weight means for two countries), and verified every transcribed data value against the cited source document.",
      "- Reproducibility: all outputs are regenerated deterministically by the released scripts (Monte Carlo seed 2026).",
      "- Limitations: no AI-generated content was used as a data source; the model did not access proprietary data."]
(P / "supplement.md").write_text("\n".join(S) + "\n")
print("tables_figures.md and supplement.md written")
