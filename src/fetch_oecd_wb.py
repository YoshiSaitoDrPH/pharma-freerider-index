"""Fetch OECD (SDMX) and World Bank inputs for the Free-Rider Index.

Small per-country requests are used because large multi-key SDMX queries time out.
Outputs (data/raw/):
  oecd_berd_c21.csv   BERD, ISIC C21 (pharmaceuticals) and total (_T), USD PPP millions, current prices
  oecd_rdtax.csv      Implied tax subsidy rates on R&D (1 - B-index), large/SME x profitable/loss
  wb_indicators.csv   GDP (current USD; PPP), GDP per capita (USD; PPP), population
Run: python src/fetch_oecd_wb.py
"""
import io, time, pathlib
import requests, pandas as pd

RAW = pathlib.Path(__file__).resolve().parents[1] / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)
ISO3 = ["USA","JPN","DEU","FRA","GBR","ITA","CAN","CHE","AUS","KOR"]
ISO2 = ["US","JP","DE","FR","GB","IT","CA","CH","AU","KR"]
HDR = {"Accept": "application/vnd.sdmx.data+csv;version=2.0.0",
       "User-Agent": "pharma-freerider-index/0.1 (academic research)"}

def sdmx_one(flow, key, start):
    url = f"https://sdmx.oecd.org/public/rest/data/{flow}/{key}?startPeriod={start}&dimensionAtObservation=AllDimensions"
    for attempt in range(4):
        try:
            r = requests.get(url, headers=HDR, timeout=90)
            if r.status_code == 200:
                return pd.read_csv(io.StringIO(r.text))
            if r.status_code == 404:
                print(f"  [404 no data] {key}"); return None
            print(f"  [{r.status_code}] {key} attempt {attempt+1}")
        except Exception as e:
            print(f"  [retry] {key}: {type(e).__name__}")
        time.sleep(4 * (attempt + 1))
    return None

def sdmx_loop(flow, keyfmt, start, name):
    frames = []
    for c in ISO3:
        df = sdmx_one(flow, keyfmt.format(c=c), start)
        if df is not None and len(df):
            frames.append(df); print(f"  {name}: {c} {len(df)} rows")
    if frames:
        out = pd.concat(frames, ignore_index=True)
        out.to_csv(RAW / name, index=False); print(f"[ok] {name}: {len(out)} rows")
    else:
        print(f"[FAIL] {name}")

# BERD by industry: REF_AREA.FREQ.MEASURE.SECT_PERF.SECT_FUND.TYPE_COST.SIZE_CLASS.ACTIVITY.CRITERIA.UNIT_MEASURE.PRICE_BASE
def sdmx_loop_multi(flow, keyfmts, start, name):
    frames = []
    for c in ISO3:
        for kf in keyfmts:
            df = sdmx_one(flow, kf.format(c=c), start)
            if df is not None and len(df):
                frames.append(df); print(f"  {name}: {c} {kf.split('.')[7]} {len(df)} rows")
    if frames:
        out = pd.concat(frames, ignore_index=True); out.to_csv(RAW / name, index=False); print(f"[ok] {name}: {len(out)} rows")
    else:
        print(f"[FAIL] {name}")

sdmx_loop_multi("OECD.STI.STP,DSD_RDS_BERD@DF_BERD_INDU,1.0",
                ["{c}.A.B.BES._T._T._Z.C21.MA.USD_PPP.V", "{c}.A.B.BES._T._T._Z._T.MA.USD_PPP.V"], 2015, "oecd_berd_c21.csv")
# R&D tax subsidy: REF_AREA.FREQ.MEASURE.UNIT_MEASURE.SIZE.PROFIT_SCENARIO
sdmx_loop("OECD.STI.STP,DSD_RDTAX@DF_RDSUB,1.0", "{c}.A.RDSUB.IX.LARGE+SME.PROFITABLE+LOSS", 2019, "oecd_rdtax.csv")

rows = []
for ind in ["NY.GDP.MKTP.CD","NY.GDP.MKTP.PP.CD","NY.GDP.PCAP.CD","NY.GDP.PCAP.PP.CD","SP.POP.TOTL"]:
    for c2 in ISO2:
        url = f"https://api.worldbank.org/v2/country/{c2}/indicator/{ind}?format=json&date=2018:2025&per_page=100"
        for attempt in range(4):
            try:
                js = requests.get(url, timeout=60).json()
                for rec in js[1]:
                    rows.append({"indicator": ind, "iso3": rec["countryiso3code"], "year": int(rec["date"]), "value": rec["value"]})
                break
            except Exception as e:
                print(f"  [retry] WB {ind} {c2}: {type(e).__name__}"); time.sleep(5)
    print(f"[ok] WB {ind}")
pd.DataFrame(rows).to_csv(RAW / "wb_indicators.csv", index=False)
print("done")
