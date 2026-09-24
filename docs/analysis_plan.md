# Analysis plan (documented 2026-09-24, before the first computation of results)

Headline design fixed before results were computed:
- Countries: G7 + Switzerland, Australia, South Korea (n = 10).
- Components (one or two per domain, 2024-2026 sources covering all ten countries with a common definition):
  P relative price level (RAND 2024, Table B.2 main results); R innovative-drug revenue share / GDP share (ASPE 2026, Table 3);
  A share of US-first drugs reimbursed by 2023 and D mean reimbursement delay (Philipson et al 2026); I pharmaceutical BERD % GDP (OECD ISIC 21; national series where OECD unavailable or non-comparable).
- Normalisation: min-max to 0-100, direction-adjusted (higher = more apparent free-riding). Aggregation: arithmetic mean, equal weights.
- Pre-specified robustness: domain weights; single-domain and price-only indices; geometric aggregation; z-score and rank normalisation; income-adjusted price; new-drug revenue ratio; nine-country (ex-US) re-estimation; jackknife; 10,000-draw Monte Carlo (Dirichlet weights, normalisation, aggregation, ±10% input noise); PCA; comparison with Kolchinsky-Xie, ASPE and Frech et al.
- Added after internal review (2026-09-25), before submission: association-based R&D series (S11); ability-to-pay adjustment of both payment components (S12); US net-price adjustment (S13); trial-hosting substitution (S14); imputed delay for non-reimbursed drugs (S15); W.A.I.T. access data for the five European countries (S16); six- and seven-component indices adding R&D tax subsidy and trial hosting (S17, S18). The headline specification was not changed.
