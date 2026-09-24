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

# --- derived -----------------------------------------------------------------
us_gdppc = wide.loc["USA", "gdp_pc_ppp_usd"]
wide["price_index_income_adj"] = wide["price_index_all_us100"] / (wide["gdp_pc_ppp_usd"] / us_gdppc)
wide["frech_contribution_per_capita_usd"] = wide["frech_contribution_usd_bn"] * 1e9 / wide["population_2018"]
wide.insert(0, "country", [NAMES[c] for c in ISO3])
wide.index.name = "iso3"
wide.to_csv(PROC / "countries.csv")
prov.to_csv(PROC / "provenance.csv", index=False)
print(wide[["country", "pharma_berd_source", "price_index_all_us100", "rev_to_gdp_ratio_all_innov", "reimb_share_2023_pct", "reimb_delay_years", "pharma_berd_pct_gdp", "gdp_pc_ppp_usd"]].round(3).to_string())
