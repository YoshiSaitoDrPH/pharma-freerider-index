# Tables and Figure Legends

## Table 1. Components of the Free-Rider Index and raw values (United States shown as the reference point)

| Country | P: Brand-name originator price, % of US (2022) | R: Innovative-drug revenue share ÷ GDP share (2020-2025) | A: US-first new drugs publicly reimbursed by 2023, % | D: Mean interval from US launch to public reimbursement, years | I: Pharmaceutical business R&D, % of GDP (year; source) | GDP per capita, PPP US$ thousand (2025) |
|---|---:|---:|---:|---:|---:|---:|
| United States (reference) | 100.0 | 1.94 | 100.0 | 0.00 | 0.451 (2022; OECD) | 90.0 |
| South Korea | 14.2 | 0.21 | 36.4 | 3.22 | 0.106 (2023; OECD) | 63.1 |
| Australia | 20.0 | 0.49 | 44.4 | 2.87 | 0.035 (2024; ABS) | 71.9 |
| Canada | 30.9 | 0.74 | 36.4 | 3.13 | 0.021 (2022; OECD) | 66.7 |
| France | 22.5 | 0.67 | 62.2 | 2.28 | 0.072 (2023; OECD) | 64.0 |
| Japan | 21.5 | 0.73 | 56.4 | 2.00 | 0.246 (2023; OECD) | 55.4 |
| United Kingdom | 26.0 | 0.56 | 64.0 | 2.34 | 0.322 (2024; ONS) | 64.6 |
| Italy | 28.1 | 0.76 | 68.0 | 2.21 | 0.038 (2023; OECD) | 62.8 |
| Germany | 25.8 | 0.58 | 72.9 | 1.11 | 0.150 (2021; OECD) | 75.4 |
| Switzerland | 29.5 | 0.61 | 54.2 | 2.17 | 0.659 (2023; OECD) | 102.5 |

Sources: P, RAND international price comparison using IQVIA MIDAS 2022 manufacturer prices, bilateral US-volume-weighted index for brand-name originator drugs (Appendix Table B.1), expressed as the comparison country's price relative to the United States = 100. R, HHS-ASPE analysis of IQVIA MIDAS 2020-2025, Table 3 (all innovative branded products). A and D, Philipson et al, 225 novel drugs first launched in the United States in 2014-2019 and their public reimbursement status in 15 markets by 2023 (PhRMA launch dataset; industry-compiled; no microdata released); D is conditional on reimbursement and the interval includes sponsor filing, regulatory review, and payer decision; US values are reference values by construction. I, OECD business enterprise R&D by industry (ISIC Rev. 4 division 21) divided by GDP in purchasing-power-parity US dollars for the same year; United Kingdom from the Office for National Statistics product-group series (£9.3 billion, 2024); Australia from the Australian Bureau of Statistics line for ANZSIC subdivision 18, basic chemical and chemical product manufacturing (A$948 million, 2023-24; an upper bound). GDP per capita from the World Bank. For the index, P, R, A, and I are inverted so that higher normalized scores indicate more apparent free-riding; normalization is across the nine non-US countries. Abbreviations: ABS, Australian Bureau of Statistics; GDP, gross domestic product; OECD, Organisation for Economic Co-operation and Development; ONS, Office for National Statistics; PPP, purchasing power parity; R&D, research and development.

## Table 2. Robustness of the headline index: rank uncertainty, alternative specifications, and internal structure

**Panel A. Headline score and rank uncertainty across 10,000 Monte Carlo specifications (nine countries)**

| Country | Headline score (0-100) | Headline rank | Median rank (5th-95th percentile) | Share of specifications in top 3 | Share of specifications in bottom 3 |
|---|---:|---:|---:|---:|---:|
| South Korea | 97.4 | 1 | 1 (1-2) | 99% | 0% |
| Australia | 74.8 | 2 | 2 (2-7) | 83% | 6% |
| Canada | 59.9 | 3 | 3 (2-8) | 58% | 17% |
| France | 48.7 | 4 | 4 (3-7) | 23% | 8% |
| Japan | 42.7 | 5 | 6 (3-9) | 11% | 48% |
| United Kingdom | 40.2 | 6 | 5 (3-8) | 16% | 23% |
| Italy | 35.8 | 7 | 6 (3-9) | 5% | 45% |
| Germany | 28.5 | 8 | 8 (5-9) | 1% | 87% |
| Switzerland | 27.4 | 9 | 7 (4-9) | 4% | 65% |

**Panel B. Spearman rank correlation of alternative specifications with the headline index**

| Specification | ρ | Specification | ρ |
|---|---:|---|---:|
| S1 Domain weights (1/3 each) | 0.98 | S15 W.A.I.T. adoption data for EU-5 | 1.00 |
| S2 Payment only (P,R) | 0.53 | S16 Association-basis pharma R&D | 1.00 |
| S3 Adoption only (A,D) | 0.72 | S17 Trial hosting replaces R&D input | 0.90 |
| S4 Price only (P) | 0.58 | S18 R&D input dropped (P,R,A,D) | 0.95 |
| S5 Geometric aggregation | 0.87 | S19 Six components (+ R&D tax subsidy) | 0.87 |
| S6 z-score normalisation | 1.00 | S20 Seven components (+ tax, + trials) | 0.87 |
| S7 Rank normalisation | 0.97 | S21 Size-adjusted (residual on log GDP) | 1.00 |
| S8 Log min-max normalisation | 0.97 | S22 Ten countries including United States | 0.95 |
| S9 All-drug price index | 0.95 | Drop component P | 0.93 |
| S10 Income-adjusted brand price | 0.82 | Drop component R | 0.98 |
| S11 Ability-to-pay adjusted payment | 0.82 | Drop component A | 0.97 |
| S12 US net-price adjustment | 1.00 | Drop component D | 0.98 |
| S13 New-drug revenue ratio | 0.92 | Drop component I | 0.95 |
| S14 Delay imputed for non-reimbursed drugs | 0.98 |  |  |

**Panel C. Internal structure of the five normalized components (nine countries)**

| Component | PC1 loading | PC2 loading | Effective importance (squared correlation with composite) | Spearman ρ with log GDP |
|---|---:|---:|---:|---:|
| Brand price level | 0.73 | -0.55 | 0.55 | 0.23 |
| Revenue contribution | 0.75 | -0.57 | 0.51 | -0.15 |
| Availability | 0.83 | 0.38 | 0.65 | -0.63 |
| Interval to reimbursement | 0.83 | 0.47 | 0.66 | -0.50 |
| Pharmaceutical R&D | 0.37 | 0.35 | 0.24 | -0.28 |
| Variance explained | 52.6% | 22.4% | | |

Monte Carlo specifications draw weights from a flat Dirichlet distribution; a normalization method (min-max, z-score, rank, log min-max); an aggregation rule (arithmetic, geometric); calibrated input noise (log-normal with σ = 0.05 for P and R and σ = 0.50 for I; normal with SD 3 percentage points for A and 0.3 years for D); and, for P, R, and I, a randomly chosen data source among the alternatives listed below. Shares of specifications are frequencies under this prior, not probabilities. Specifications: S1 domain weights (one third each for payment, adoption, and R&D); S2 payment components only; S3 adoption components only; S4 brand price only; S5 geometric aggregation; S6 z-score normalization; S7 rank normalization; S8 log min-max normalization; S9 all-drug price index in place of brand price; S10 brand price divided by relative GDP per capita; S11 ability-to-pay adjustment of both payment components (income elasticity 1.3); S12 US net-price adjustment (US prices and revenue reduced by 37.7%); S13 revenue contribution for drugs launched after 2020; S14 delay imputed for non-reimbursed drugs (6.5-year follow-up horizon); S15 EFPIA W.A.I.T. availability and time to availability substituted for the five European countries; S16 association-based R&D series; S17 industry-sponsored trial starts per million population replace R&D input; S18 R&D input dropped; S19 six components adding the OECD implied R&D tax subsidy rate; S20 seven components adding tax subsidy and trial hosting; S21 each normalized component residualized on log GDP before aggregation; S22 ten countries including the United States. Abbreviations: GDP, gross domestic product; PC, principal component; R&D, research and development.

## Figure legends

**Figure 1. Headline Free-Rider Index and rank uncertainty (nine countries).** (A) Equal-weight index with the contribution of each normalized component (each contributes one fifth of its 0-100 score). (B) Rank of each country across 10,000 Monte Carlo specifications: dot, median; horizontal bar, 5th-95th percentile; red tick, headline rank. Higher scores indicate lower brand-name prices, lower innovative-drug revenue relative to GDP, fewer and later reimbursed US-first drugs, and lower pharmaceutical R&D intensity than the other eight countries. The United States is the reference point for price, availability, and interval and is not ranked. GDP, gross domestic product; R&D, research and development.

**Figure 2. Country rank under alternative specifications and with each component dropped.** Cells show each country's rank among the nine non-US countries (1 = most apparent free-riding) under the headline specification (S0), 21 alternative specifications (S1-S21; defined in Table 2), and five indices in which one component is dropped (−P brand price, −R revenue contribution, −A availability, −D interval, −I pharmaceutical R&D).

**Figure 3. Decomposition of the comparison with the Kolchinsky-Xie Freeriding Index (seven overlapping countries).** Left, headline index; center, payment sub-index (mean of normalized brand-price and revenue-contribution scores); right, adoption sub-index (mean of normalized availability and interval scores), each plotted against the Kolchinsky-Xie index, a net brand-price measure adjusted for income. ρ, Spearman rank correlation. The payment sub-index reproduces the price-based measure; the adoption sub-index is unrelated to it.
