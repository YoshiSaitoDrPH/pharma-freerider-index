"""Assemble the analysis dataset (data/processed/countries.csv) from raw inputs.

Inputs : data/raw/manual_inputs.csv (hand-transcribed, source-cited values)
         data/raw/oecd_berd_c21.csv, data/raw/wb_indicators.csv, data/raw/oecd_rdtax.csv
Output : data/processed/countries.csv  (one row per country, wide)
         data/processed/provenance.csv (variable -> source, year)
"""
import pathlib, pandas as pd, numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW, PROC = ROOT / "data" / "raw", ROOT / "data" / "processed"
PROC.mkdir(parents=True, exist_ok=True)
ISO3 = ["USA","JPN","DEU","FRA","GBR","ITA","CAN","CHE","AUS","KOR"]
NAMES = dict(USA="United States", JPN="Japan", DEU="Germany", FRA="France", GBR="United Kingdom",
             ITA="Italy", CAN="Canada", CHE="Switzerland", AUS="Australia", KOR="South Korea")

man = pd.read_csv(RAW / "manual_inputs.csv")
wide = man.pivot_table(index="iso3", columns="variable", values="value", aggfunc="first").reindex(ISO3)
prov = man.groupby("variable").agg(source_id=("source_id", "first"), year=("year", "first")).reset_index()

# --- World Bank -------------------------------------------------------------
wb = pd.read_csv(RAW / "wb_indicators.csv").dropna(subset=["value"])
def latest(ind, year=None):
    d = wb[wb.indicator == ind]
    if year is not None:
        d = d[d.year == year]
    else:
        d = d.sort_values("year").groupby("iso3").tail(1)
    return d.set_index("iso3")["value"].reindex(ISO3), d.set_index("iso3")["year"].reindex(ISO3)
for ind, col in [("NY.GDP.PCAP.PP.CD", "gdp_pc_ppp_usd"), ("NY.GDP.PCAP.CD", "gdp_pc_usd"),
                 ("SP.POP.TOTL", "population"), ("NY.GDP.MKTP.PP.CD", "gdp_ppp_usd"), ("NY.GDP.MKTP.CD", "gdp_usd")]:
    v, y = latest(ind)
    wide[col] = v; wide[col + "_year"] = y
    prov = pd.concat([prov, pd.DataFrame([{"variable": col, "source_id": "WB_WDI", "year": "latest available"}])])
pop2018, _ = latest("SP.POP.TOTL", 2018)
wide["population_2018"] = pop2018

# --- OECD BERD ISIC C21 -----------------------------------------------------
berd = pd.read_csv(RAW / "oecd_berd_c21.csv")
berd = berd[(berd.UNIT_MEASURE == "USD_PPP") & (berd.PRICE_BASE == "V")]
def last_obs(activity):
    d = berd[berd.ACTIVITY == activity].dropna(subset=["OBS_VALUE"]).sort_values("TIME_PERIOD")
    d = d.groupby("REF_AREA").tail(1).set_index("REF_AREA")
    return d["OBS_VALUE"].reindex(ISO3), d["TIME_PERIOD"].reindex(ISO3)
c21, c21y = last_obs("C21"); tot, toty = last_obs("_T")
wide["pharma_berd_usd_ppp_m"] = c21; wide["pharma_berd_year"] = c21y
wide["total_berd_usd_ppp_m"] = tot; wide["total_berd_year"] = toty
# GDP PPP in the same year as the pharma BERD observation
gdp_ppp_same = []
for c in ISO3:
    y = c21y.get(c)
    d = wb[(wb.indicator == "NY.GDP.MKTP.PP.CD") & (wb.iso3 == c) & (wb.year == y)]
    gdp_ppp_same.append(d.value.iloc[0] if len(d) else np.nan)
wide["gdp_ppp_usd_berd_year"] = gdp_ppp_same
wide["pharma_berd_pct_gdp"] = wide["pharma_berd_usd_ppp_m"] * 1e6 / wide["gdp_ppp_usd_berd_year"] * 100
wide["pharma_share_of_berd_pct"] = wide["pharma_berd_usd_ppp_m"] / wide["total_berd_usd_ppp_m"] * 100
prov = pd.concat([prov, pd.DataFrame([{"variable": "pharma_berd_pct_gdp", "source_id": "OECD_BERD + WB_WDI", "year": "latest (2021-2023)"}])])

# --- national fallback where OECD ISIC C21 is unavailable ----------------------
wide["pharma_berd_source"] = np.where(wide["pharma_berd_pct_gdp"].notna(), "OECD BERD ISIC C21", None)
fb_path = RAW / "national_fallback.csv"
if fb_path.exists():
    fb = pd.read_csv(fb_path)
    for _, r in fb.iterrows():
        if pd.isna(wide.loc[r.iso3, r.variable]):
            wide.loc[r.iso3, r.variable] = r.value
            wide.loc[r.iso3, "pharma_berd_source"] = r.source_id
            wide.loc[r.iso3, "pharma_berd_year"] = r.year
            prov = pd.concat([prov, pd.DataFrame([{"variable": f"{r.variable} ({r.iso3} fallback)", "source_id": r.source_id, "year": r.year}])])

# --- national overrides (documented) ---------------------------------------
ovr_path = RAW / "national_overrides.csv"
if ovr_path.exists():
    ovr = pd.read_csv(ovr_path)
    for _, r in ovr.iterrows():
        wide.loc[r.iso3, r.variable] = r.value
        if r.variable == "pharma_berd_pct_gdp":
            wide.loc[r.iso3, "pharma_berd_source"] = r.source_id
        prov = pd.concat([prov, pd.DataFrame([{"variable": f"{r.variable} ({r.iso3} override)", "source_id": r.source_id, "year": r.year}])])

# --- OECD R&D tax subsidy (extension component) ------------------------------
p = RAW / "oecd_rdtax.csv"
if p.exists():
    tax = pd.read_csv(p).dropna(subset=["OBS_VALUE"])
    for size, col in [("LARGE", "rd_tax_subsidy_large"), ("SME", "rd_tax_subsidy_sme")]:
        d = tax[(tax.SIZE == size) & (tax.PROFIT_SCENARIO == "PROFITABLE")].sort_values("TIME_PERIOD").groupby("REF_AREA").tail(1).set_index("REF_AREA")
        wide[col] = d["OBS_VALUE"].reindex(ISO3); wide[col + "_year"] = d["TIME_PERIOD"].reindex(ISO3)
    prov = pd.concat([prov, pd.DataFrame([{"variable": "rd_tax_subsidy_*", "source_id": "OECD_RDTAX", "year": "2025"}])])


# --- Clinical-trial hosting (ClinicalTrials.gov API v2, industry-sponsored interventional trials starting 2023-2025) ---
ct_path = RAW / "ctgov_trial_counts.csv"
if ct_path.exists():
    ct = pd.read_csv(ct_path)
    ind = ct[ct.sponsor_class == "INDUSTRY"].set_index("iso3")["trials_2023_2025"].reindex(ISO3)
    wide["industry_trials_2023_2025"] = ind
    wide["industry_trials_per_million"] = ind / (wide["population"] / 1e6) / 3.0   # per million population per year
    prov = pd.concat([prov, pd.DataFrame([{"variable": "industry_trials_per_million", "source_id": "CTGOV", "year": "2023-2025 starts"}])])
# --- Imputed delay: non-reimbursed drugs assigned the mean follow-up horizon (launch 2014-2019 -> end 2023 ~ 6.5 y) ---
TMAX = 6.5
wide["reimb_delay_imputed"] = wide["reimb_share_2023_pct"] / 100 * wide["reimb_delay_years"] + (1 - wide["reimb_share_2023_pct"] / 100) * TMAX
# --- W.A.I.T. substitution for the five European countries (EU-authorisation cohort 2021-2024) ---
wide["reimb_share_wait_mix"] = wide["reimb_share_2023_pct"]
wide["reimb_delay_wait_mix"] = wide["reimb_delay_years"]
m = wide["wait_availability_pct"].notna()
wide.loc[m, "reimb_share_wait_mix"] = wide.loc[m, "wait_availability_pct"]
wide.loc[m, "reimb_delay_wait_mix"] = wide.loc[m, "wait_mean_days"] / 365.25

# --- OECD GBARD, socio-economic objective health (NABS07), USD PPP current prices -> % of GDP (PPP) ----------
gb_path = RAW / "oecd_gbard_health.csv"
if gb_path.exists():
    gb = pd.read_csv(gb_path).dropna(subset=["OBS_VALUE"])
    gb = gb[(gb.UNIT_MEASURE == "USD_PPP") & (gb.PRICE_BASE == "V")].sort_values("TIME_PERIOD")
    # use the latest year with data for all countries where possible (2023), else latest per country
    common = 2023
    last = gb[gb.TIME_PERIOD <= common].groupby("REF_AREA").tail(1).set_index("REF_AREA")
    wide["gbard_health_usd_ppp_m"] = last["OBS_VALUE"].reindex(ISO3); wide["gbard_health_year"] = last["TIME_PERIOD"].reindex(ISO3)
    gdp_same = []
    for c in ISO3:
        y = wide.loc[c, "gbard_health_year"]
        d = wb[(wb.indicator == "NY.GDP.MKTP.PP.CD") & (wb.iso3 == c) & (wb.year == y)]
        gdp_same.append(d.value.iloc[0] if len(d) else np.nan)
    wide["gbard_health_pct_gdp"] = wide["gbard_health_usd_ppp_m"] * 1e6 / pd.Series(gdp_same, index=ISO3) * 100
    prov = pd.concat([prov, pd.DataFrame([{"variable": "gbard_health_pct_gdp", "source_id": "OECD_GBARD + WB_WDI", "year": "2023 (or latest)"}])])

# --- derived -----------------------------------------------------------------
us_gdppc = wide.loc["USA", "gdp_pc_ppp_usd"]
wide["price_index_income_adj"] = wide["price_index_all_us100"] / (wide["gdp_pc_ppp_usd"] / us_gdppc)
wide["price_index_brand_income_adj"] = wide["price_index_brand_us100"] / (wide["gdp_pc_ppp_usd"] / us_gdppc)
# Progressive ability-to-pay adjustment of the revenue ratio: benchmark contribution rises with income elasticity 1.3
inc_ratio = wide["gdp_pc_ppp_usd"] / us_gdppc
wide["rev_to_gdp_ratio_progressive"] = wide["rev_to_gdp_ratio_all_innov"] / inc_ratio ** 0.3
# US net-price adjustment: RAND applied a 37.7% reduction to US manufacturer prices (all drugs) as a gross-to-net sensitivity
NET = 1 - 0.377
wide["price_index_us_net"] = (wide["price_index_all_us100"] / NET).clip(upper=100.0)
wide["price_index_brand_us_net"] = (wide["price_index_brand_us100"] / NET).clip(upper=100.0)
sh = wide["rev_share_all_innov_pct"].copy(); sh_us = sh["USA"] * NET
sh_adj = sh * (100.0 / (sh.drop("USA").sum() + sh_us)); sh_adj["USA"] = sh_us * (100.0 / (sh.drop("USA").sum() + sh_us))
gdp_share = wide["rev_share_all_innov_pct"] / wide["rev_to_gdp_ratio_all_innov"]
wide["rev_to_gdp_ratio_us_net"] = sh_adj / gdp_share
wide["frech_contribution_per_capita_usd"] = wide["frech_contribution_per_capita_usd_pub"].where(wide["frech_contribution_per_capita_usd_pub"].notna(), wide["frech_contribution_usd_bn"] * 1e9 / wide["population_2018"])  # Frech et al 2026 Table 1 per-capita column (all nine countries)
wide.insert(0, "country", [NAMES[c] for c in ISO3])
wide.index.name = "iso3"
wide.to_csv(PROC / "countries.csv")
prov.to_csv(PROC / "provenance.csv", index=False)
print(wide[["country", "pharma_berd_source", "price_index_all_us100", "rev_to_gdp_ratio_all_innov", "reimb_share_2023_pct", "reimb_delay_years", "pharma_berd_pct_gdp", "gdp_pc_ppp_usd"]].round(3).to_string())
