# Analysis plan (documented 2026-09-24, before the first computation of results)

Headline design fixed before results were computed:
- Countries: G7 + Switzerland, Australia, South Korea (n = 10).
- Components (one or two per domain, 2024-2026 sources covering all ten countries with a common definition):
  P relative price level (RAND 2024, Table B.2 main results); R innovative-drug revenue share / GDP share (ASPE 2026, Table 3);
  A share of US-first drugs reimbursed by 2023 and D mean reimbursement delay (Philipson et al 2026); I pharmaceutical BERD % GDP (OECD ISIC 21; national series where OECD unavailable or non-comparable).
- Normalisation: min-max to 0-100, direction-adjusted (higher = more apparent free-riding). Aggregation: arithmetic mean, equal weights.
- Pre-specified robustness: domain weights; single-domain and price-only indices; geometric aggregation; z-score and rank normalisation; income-adjusted price; new-drug revenue ratio; nine-country (ex-US) re-estimation; jackknife; 10,000-draw Monte Carlo (Dirichlet weights, normalisation, aggregation, ±10% input noise); PCA; comparison with Kolchinsky-Xie, ASPE and Frech et al.
- Added after internal review (2026-09-25), before submission: association-based R&D series (S11); ability-to-pay adjustment of both payment components (S12); US net-price adjustment (S13); trial-hosting substitution (S14); imputed delay for non-reimbursed drugs (S15); W.A.I.T. access data for the five European countries (S16); six- and seven-component indices adding R&D tax subsidy and trial hosting (S17, S18). The headline specification was not changed.

## Amendments and deviations recorded before submission (2026-11-11)

The entries above are kept as written. The following changes were made after them and are reflected in the submitted manuscript:
- Price component P: the headline uses the brand-name originator index (RAND 2024, Table 2.1), not the all-drug table named above; the all-drug index is sensitivity S9 and, after full-text verification on 2026-10-08, is taken from Appendix Table B.1 ("Main Results"), which matches the report's body text, rather than Table B.2.
- Specification numbering: the working numbers S11-S18 above do not correspond to the manuscript's Table 2 (S1-S21); the US net-price adjustment was dropped as a specification because a uniform rescaling of the numeraire cannot change the nine-country ranking under min-max normalization.
- Monte Carlo: the uniform +/-10% noise above was replaced by component-specific calibrated noise (Table 2 footnote), data-source switching for P, R and I was added, and a correlated-noise analysis for A and D (rho = +/-0.7; Appendix Table S9c) and a decomposition by source of uncertainty (Appendix Table S9b) were added on 2026-10-08.
- Added analyses: effective importance (squared correlation with the composite), leave-one-country-out, component correlations with log GDP, and the revenue-gap-to-parity scenario (Appendix Table S11, two parity definitions).
- Data corrections from full-text verification (2026-10-01 to 2026-10-08): Frech et al per-capita contributions taken from their Table 1; W.A.I.T. availability counts for Italy and France re-read from the 2025 survey slides; UK pharmaceutical R&D from the ONS product-group table of the designated-official-statistics dataset.
- The headline specification (five components, min-max, equal weights, nine countries) was not changed.

