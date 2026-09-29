# pharma-freerider-index

A reproducible, multi-dimensional **Free-Rider Index** of how ten high-income countries share the cost of
pharmaceutical innovation (United States, Japan, Germany, France, United Kingdom, Italy, Canada, Switzerland,
Australia, South Korea). Companion code and data for the manuscript
*"Who Pays for Pharmaceutical Innovation? A Reproducible Multi-Dimensional Free-Rider Index for Ten High-Income Countries"*.

Interactive dashboard: https://yoshisaitodrph.github.io/pharma-freerider-index/ (self-contained HTML; source in `dashboard/`).

Manuscript files (Value in Health format): `paper/`. Review log and analysis plan: `docs/`.

## What the index measures

Basu (2026, *Am J Health Econ*) shows that when a large and a small country coexist, the small country can
deviate from the dynamic-efficient payment rule by free-riding on the R&D induced by the larger market.
This repository turns that idea into a transparent, adjustable index built from five published indicators:

| Id | Component | Domain | Direction | Source |
|---|---|---|---|---|
| P | Price level, all drugs, % of US price (2022) | Payment | lower price = more free-riding | RAND RR-A788-3 (2024), Table B.2 |
| R | Innovative-drug revenue share ÷ GDP share (2020–25) | Payment | lower ratio = more | HHS-ASPE Issue Brief (June 2026), Table 3 |
| A | Share of 225 US-first novel drugs (2014–19) publicly reimbursed by 2023 | Access | lower share = more | Philipson et al. (Aug 2026) |
| D | Mean reimbursement delay after US launch, years | Access | longer = more | Philipson et al. (Aug 2026), Table 1 |
| I | Pharmaceutical business R&D (ISIC 21), % of GDP | R&D input | lower = more | OECD BERD by industry; World Bank GDP |

Each component is normalised to 0–100 (min–max in the headline; z-score and rank as sensitivities), then
aggregated with user-chosen weights (equal weights in the headline). Robustness follows the OECD/JRC
composite-indicator handbook: 10,000 Monte Carlo draws over weights, normalisation, aggregation and ±10 %
input noise; one-component-out jackknife; principal component analysis; and comparison with three existing
single-metric measures (Kolchinsky & Xie 2025; ASPE 2026; Frech et al. 2026).

## Reproduce

```bash
pip install -r requirements.txt
python src/fetch_oecd_wb.py      # OECD SDMX + World Bank (optional: raw files are committed)
python src/build_dataset.py      # -> data/processed/countries.csv
python src/run_analysis.py       # -> tables/*.csv, data/processed/results.json
python src/make_figures.py       # -> figures/*.svg|png
python src/build_dashboard.py    # -> dashboard/index.html
```

`data/raw/manual_inputs.csv` holds every hand-transcribed value with its source and page/table reference;
`data/raw/sources.csv` lists the sources; `data/processed/provenance.csv` maps each variable to its source.

## Repository layout

```
data/raw/        source-cited inputs (manual_inputs.csv, hta_thresholds.csv, OECD/World Bank pulls)
data/processed/  assembled dataset, results.json for the dashboard
src/             fetch_oecd_wb.py, build_dataset.py, frindex.py (library), run_analysis.py, make_figures.py, build_dashboard.py
tables/          analysis outputs (CSV)
figures/         publication figures (SVG, PNG 300 dpi)
dashboard/       template.html -> index.html
docs/            journal checklist, methods notes
paper/           manuscript files
```

## Use of AI

Code in this repository was drafted with the assistance of Claude (Anthropic; Claude Code, model Fable 5.1)
under the author's direction, then reviewed, executed and verified by the author. All data values were
transcribed from the cited primary sources and are traceable through `data/raw/manual_inputs.csv`.

## License

Code: MIT. Data compilation and documentation: CC BY 4.0. Underlying third-party data remain subject to their
original terms (RAND, HHS-ASPE, University of Chicago ECCHC, OECD, World Bank).

## Citation

See `CITATION.cff`.
