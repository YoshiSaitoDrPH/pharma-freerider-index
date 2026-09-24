"""World Bank WDI pull only (used when OECD SDMX is unavailable)."""
import pathlib, time, requests, pandas as pd
RAW = pathlib.Path(__file__).resolve().parents[1] / "data" / "raw"
ISO2 = ["US","JP","DE","FR","GB","IT","CA","CH","AU","KR"]
rows = []
for ind in ["NY.GDP.MKTP.CD","NY.GDP.MKTP.PP.CD","NY.GDP.PCAP.CD","NY.GDP.PCAP.PP.CD","SP.POP.TOTL","NY.GDP.MKTP.CN","PA.NUS.PPP"]:
    for c2 in ISO2:
        url = f"https://api.worldbank.org/v2/country/{c2}/indicator/{ind}?format=json&date=2018:2025&per_page=100"
        for attempt in range(4):
            try:
                js = requests.get(url, timeout=60).json()
                rows += [{"indicator": ind, "iso3": r["countryiso3code"], "year": int(r["date"]), "value": r["value"]} for r in js[1]]
                break
            except Exception as e:
                print("retry", ind, c2, type(e).__name__); time.sleep(5)
    print("[ok]", ind)
pd.DataFrame(rows).to_csv(RAW / "wb_indicators.csv", index=False); print("done", len(rows))
