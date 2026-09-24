# Tables and Figure Legends

## Table 1. Components of the Free-Rider Index and raw values for ten high-income countries

| Country | P: Price level, all drugs, % of US (2022) | R: Innovative-drug revenue share ÷ GDP share (2020-2025) | A: US-first new drugs publicly reimbursed by 2023, % | D: Mean reimbursement delay after US launch, years | I: Pharmaceutical business R&D, % of GDP (year; source) | GDP per capita, PPP US$ thousand (2025) |
|---|---:|---:|---:|---:|---:|---:|
| South Korea | 33.6 | 0.21 | 36.4 | 3.22 | 0.106 (2023; OECD) | 63.1 |
| Australia | 36.3 | 0.49 | 44.4 | 2.87 | 0.035 (2024; ABS) | 71.9 |
| Canada | 47.6 | 0.74 | 36.4 | 3.13 | 0.021 (2022; OECD) | 66.7 |
| France | 40.3 | 0.67 | 62.2 | 2.28 | 0.072 (2023; OECD) | 64.0 |
| Italy | 40.0 | 0.76 | 68.0 | 2.21 | 0.038 (2023; OECD) | 62.8 |
| United Kingdom | 38.2 | 0.56 | 64.0 | 2.34 | 0.322 (2024; ONS) | 64.6 |
| Japan | 51.0 | 0.73 | 56.4 | 2.00 | 0.246 (2023; OECD) | 55.4 |
| Germany | 44.9 | 0.58 | 72.9 | 1.11 | 0.150 (2021; OECD) | 75.4 |
| Switzerland | 55.7 | 0.61 | 54.2 | 2.17 | 0.659 (2023; OECD) | 102.5 |
| United States | 100.0 | 1.94 | 100.0 | 0.00 | 0.451 (2022; OECD) | 90.0 |

Sources: P, RAND international price comparison using IQVIA MIDAS 2022 data, bilateral US-volume-weighted index, all drugs (Appendix Table B.2, main specification), expressed as the comparison country's price relative to the United States = 100. R, HHS-ASPE analysis of IQVIA MIDAS 2020-2025, Table 3 (all innovative branded products). A and D, Philipson et al, 225 novel drugs first launched in the United States in 2014-2019 and their public reimbursement status in 15 markets by 2023; US values are reference values by construction. I, OECD business enterprise R&D by industry (ISIC Rev. 4 division 21) divided by GDP in purchasing-power-parity US dollars for the same year; United Kingdom from the Office for National Statistics product-group series (£9.3 billion, 2024); Australia from the Australian Bureau of Statistics chemical and pharmaceutical manufacturing line (A$948 million, 2023-24). GDP per capita from the World Bank. For the index, P, R, A, and I are inverted so that higher normalized scores indicate more apparent free-riding. Abbreviations: ABS, Australian Bureau of Statistics; GDP, gross domestic product; OECD, Organisation for Economic Co-operation and Development; ONS, Office for National Statistics; PPP, purchasing power parity; R&D, research and development.

## Table 2. Robustness of the headline index: rank uncertainty, alternative specifications, and internal structure

**Panel A. Headline score and rank uncertainty across 10,000 Monte Carlo specifications**

| Country | Headline score (0-100) | Headline rank | Median rank (5th-95th percentile) | Probability of top-3 rank | Probability of bottom-3 rank among non-US countries |
|---|---:|---:|---:|---:|---:|
| South Korea | 97.4 | 1 | 1 (1-3) | 99% | 0% |
| Australia | 90.8 | 2 | 2 (1-3) | 100% | 0% |
| Canada | 89.1 | 3 | 3 (1-6) | 81% | 1% |
| France | 77.1 | 4 | 4 (3-6) | 6% | 1% |
| Italy | 75.0 | 5 | 5 (4-8) | 3% | 12% |
| United Kingdom | 71.0 | 6 | 6 (3-8) | 10% | 10% |
| Japan | 67.8 | 7 | 7 (5-9) | 0% | 37% |
| Germany | 63.7 | 8 | 8 (6-9) | 0% | 60% |
| Switzerland | 56.6 | 9 | 9 (5-9) | 0% | 79% |
| United States | 6.5 | 10 | 10 (10-10) | 0% | 100% |

**Panel B. Spearman rank correlation of alternative specifications with the headline index**

| Specification | ρ | Specification | ρ |
|---|---:|---|---:|
| S1 Domain weights (1/3 each domain) | 1.00 | S9 New-drug revenue ratio | 0.99 |
| S2 Payment-only (P,R) | 0.78 | S10 Excluding United States (rescaled) | 0.98 |
| S3 Access-only (A,D) | 0.72 | S11 Association-basis pharma R&D | 0.99 |
| S4 Price only (P) | 0.81 | Drop component P | 0.98 |
| S5 Geometric aggregation | 1.00 | Drop component R | 0.99 |
| S6 z-score normalisation | 1.00 | Drop component A | 0.99 |
| S7 Rank normalisation | 0.94 | Drop component D | 0.96 |
| S8 Income-adjusted price | 0.96 | Drop component I | 0.88 |

**Panel C. Principal component analysis of the five normalized components**

| Component | PC1 loading | PC2 loading |
|---|---:|---:|
| Price level | 0.94 | -0.05 |
| Revenue contribution | 0.92 | 0.21 |
| Availability | 0.91 | 0.23 |
| Delay | 0.94 | 0.13 |
| Pharmaceutical R&D | 0.61 | -0.79 |
| Variance explained | 76.5% | 14.8% |

Monte Carlo specifications draw weights from a flat Dirichlet distribution, a normalization method (min-max, z-score, rank), an aggregation rule (arithmetic, geometric), and independent ±10% uniform perturbations of each input. The bottom-3 probability for the United States is 100% by construction. Specifications: S1 domain weights (one third each for payment, access, and R&D); S2 payment components only; S3 access components only; S4 price only; S5 geometric aggregation; S6 z-score normalization; S7 rank normalization; S8 income-adjusted price; S9 revenue contribution for drugs launched after 2020; S10 nine non-US countries; S11 association-based R&D series. Abbreviations: PC, principal component; R&D, research and development.

## Figure legends

**Figure 1. Headline Free-Rider Index and rank uncertainty.** (A) Equal-weight index for ten high-income countries with the contribution of each normalized component (each contributes one fifth of its 0-100 score). (B) Rank of each country across 10,000 Monte Carlo specifications: dot, median; horizontal bar, 5th-95th percentile; red tick, headline rank. Higher scores indicate lower relative prices, lower revenue contribution relative to GDP, fewer and later reimbursed US-first drugs, and lower pharmaceutical R&D intensity than peers. GDP, gross domestic product; R&D, research and development.

**Figure 2. Country rank under alternative specifications and jackknife.** Cells show each country's rank (1 = most apparent free-riding) under the headline specification (S0), 11 alternative specifications (S1-S11; defined in Table 2), and five jackknife indices in which one component is dropped (−P price, −R revenue contribution, −A availability, −D delay, −I pharmaceutical R&D). The United States is not scored in S10.

**Figure 3. Payment and access domains.** Horizontal axis: mean of normalized price-level and revenue-contribution scores. Vertical axis: mean of normalized availability and delay scores. Shading: normalized pharmaceutical R&D score (dark = high R&D intensity). Bubble area is proportional to each country's share of OECD innovative-drug revenue in 2020-2025. Dashed lines mark the midpoint of each axis. OECD, Organisation for Economic Co-operation and Development; R&D, research and development.

**Figure 4. Comparison with existing single-metric measures.** Headline index plotted against (left) the Kolchinsky-Xie Freeriding Index (seven overlapping countries), (center) the HHS-ASPE ratio of innovative-drug revenue share to GDP share (ten countries; axis inverted so that right = less contribution), and (right) Frech et al's estimated per-capita contribution to global pharmaceutical R&D (seven countries; inverted). ρ, Spearman rank correlation, signed so that positive values indicate agreement in the direction of free-riding. GDP, gross domestic product; HHS-ASPE, Office of the Assistant Secretary for Planning and Evaluation, US Department of Health and Human Services.
