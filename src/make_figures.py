"""Publication figures (SVG + 300-dpi PNG) for the Free-Rider Index paper.
Fig 1  Headline composite with component contributions and Monte Carlo rank intervals
Fig 2  Rank robustness heatmap across specifications and jackknife
Fig 3  Two-domain map: payment score vs access score, bubble = share of innovative revenue
Fig 4  Comparison with existing single-metric measures
S1     PCA biplot ; S2 rank-frequency matrix
"""
import pathlib, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from frindex import ORDER, COMPONENTS, normalise, raw_matrix, composite, pca

ROOT = pathlib.Path(__file__).resolve().parents[1]
TAB, FIG, PROC = ROOT / "tables", ROOT / "figures", ROOT / "data" / "processed"
FIG.mkdir(exist_ok=True)
plt.rcParams.update({"font.family": "serif", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.titleweight": "bold", "figure.dpi": 110})
PAL = {"P": "#1f4e79", "R": "#2e75b6", "A": "#c55a11", "D": "#f4b183", "I": "#548235"}
LBL = {"P": "Price level", "R": "Revenue/GDP", "A": "Availability", "D": "Delay", "I": "Pharma R&D"}

df = pd.read_csv(PROC / "countries.csv", index_col="iso3")
base = pd.read_csv(TAB / "table2_headline_index.csv", index_col="iso3")
mc = pd.read_csv(TAB / "table5_montecarlo_rank_intervals.csv", index_col="iso3")
ranks = pd.read_csv(TAB / "table3_rank_by_specification.csv", index_col="iso3")
ext = pd.read_csv(TAB / "table7_external_comparators.csv", index_col="iso3")
names = df["country"]

def save(fig, name):
    fig.savefig(FIG / f"{name}.svg", bbox_inches="tight"); fig.savefig(FIG / f"{name}.png", dpi=300, bbox_inches="tight"); plt.close(fig)

# ---------------- Figure 1
order = base.sort_values("FRI").index
fig, (ax, ax2) = plt.subplots(1, 2, figsize=(7.2, 3.6), gridspec_kw={"width_ratios": [3, 1.3]}, sharey=True)
left = np.zeros(len(order))
for k in ORDER:
    v = base.loc[order, k].values / len(ORDER)
    ax.barh(range(len(order)), v, left=left, color=PAL[k], label=LBL[k]); left += v
for i, c in enumerate(order):
    ax.text(left[i] + 1, i, f"{base.loc[c,'FRI']:.0f}", va="center", fontsize=8)
ax.set_yticks(range(len(order))); ax.set_yticklabels(names[order]); ax.set_xlabel("Free-Rider Index (0–100), equal weights")
ax.set_xlim(0, 100); ax.legend(frameon=False, fontsize=7, loc="lower right", title="Component", title_fontsize=7)
ax.set_title("A. Headline index and component contributions", loc="left", fontsize=9)
for i, c in enumerate(order):
    ax2.plot([mc.loc[c, "rank_p05"], mc.loc[c, "rank_p95"]], [i, i], color="#7f7f7f", lw=2)
    ax2.plot(mc.loc[c, "rank_median"], i, "o", color="black", ms=4)
    ax2.plot(base.loc[c, "rank"], i, "|", color="#c00000", ms=9, mew=1.5)
ax2.set_xlim(0.5, len(order) + 0.5); ax2.set_xticks(range(1, len(order) + 1)); ax2.invert_xaxis()
ax2.set_xlabel("Rank (1 = most free-riding)"); ax2.set_title("B. Rank under 10,000 specifications", loc="left", fontsize=9)
ax2.text(0.02, 0.02, "bar: 5th–95th percentile; dot: median; red tick: headline", transform=ax2.transAxes, fontsize=6.5)
save(fig, "fig1_headline_index")

# ---------------- Figure 2 heatmap
R = ranks.drop(columns="country").loc[base.sort_values("FRI", ascending=False).index]
cols = [c.split(" ", 1)[0] if c.startswith("S") else c.replace("drop_", "−") for c in R.columns]
fig, ax = plt.subplots(figsize=(7.2, 3.8))
im = ax.imshow(R.values, cmap="RdYlBu", aspect="auto", vmin=1, vmax=10)
ax.set_xticks(range(len(cols))); ax.set_xticklabels(cols, rotation=45, ha="right", fontsize=7)
ax.set_yticks(range(len(R))); ax.set_yticklabels(names[R.index])
for i in range(R.shape[0]):
    for j in range(R.shape[1]):
        v = R.values[i, j]
        ax.text(j, i, "" if np.isnan(v) else f"{int(v)}", ha="center", va="center", fontsize=7, color="black")
cb = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02); cb.set_label("Rank (1 = most free-riding)")
ax.set_title("Rank by specification and by dropped component", loc="left", fontsize=9)
ax.set_xlabel("S0 equal weights · S1 domain weights · S2 payment only · S3 access only · S4 price only · S5 geometric\n"
              "S6 z-score · S7 rank · S8 income-adjusted price · S9 new-drug revenue · S10 excluding US (US not scored) · S11 association-basis R&D · −X: component X dropped", fontsize=6.5)
save(fig, "fig2_rank_robustness")

# ---------------- Figure 3 two-domain map
S = normalise(raw_matrix(df))
pay = S[["P", "R"]].mean(1); acc = S[["A", "D"]].mean(1); rd = S["I"]
size = df["rev_share_all_innov_pct"].clip(lower=0.3) * 40
fig, ax = plt.subplots(figsize=(5.2, 4.2))
sc = ax.scatter(pay, acc, s=size, c=rd, cmap="Greens_r", edgecolor="black", lw=0.6, alpha=0.9, vmin=0, vmax=100)
OFF = {"JPN": (-38, 8), "FRA": (6, 8), "GBR": (8, -12), "ITA": (8, -14), "CHE": (-60, 6), "DEU": (8, 4), "CAN": (8, 4), "AUS": (8, 4), "KOR": (-52, 8), "USA": (8, 6)}
for c in df.index:
    ax.annotate(names[c], (pay[c], acc[c]), xytext=OFF.get(c, (6, 4)), textcoords="offset points", fontsize=7.5)
ax.axvline(50, color="#bbbbbb", lw=0.7, ls="--"); ax.axhline(50, color="#bbbbbb", lw=0.7, ls="--")
ax.set_xlabel("Payment domain score (price level, revenue/GDP) →  more free-riding")
ax.set_ylabel("Access domain score (availability, delay) →  more free-riding")
cb = fig.colorbar(sc, ax=ax, fraction=0.04, pad=0.02); cb.set_label("Pharma R&D score (dark = high R&D)")
ax.set_xlim(-5, 108); ax.set_ylim(-5, 108)
ax.text(0.99, 0.01, "bubble area ∝ share of OECD innovative-drug revenue 2020–25", transform=ax.transAxes, ha="right", fontsize=6.5)
save(fig, "fig3_domain_map")

# ---------------- Figure 4 external comparison
fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.7))
pairs = [("Kolchinsky_Freeriding_Index_pct", "Kolchinsky & Xie (2025)\nFreeriding Index (%)", 1),
         ("ASPE_rev_to_GDP_ratio_all_innov", "ASPE (2026) revenue share /\nGDP share (inverted axis)", -1),
         ("Frech2026_contribution_per_capita_usd", "Frech et al. (2026) contribution\nper capita, US$ (inverted axis)", -1)]
for ax, (col, lab, sgn) in zip(axes, pairs):
    d = ext[["FRI_headline", col]].dropna()
    ax.scatter(d[col], d["FRI_headline"], color="#1f4e79", s=18)
    for c in d.index:
        dx, dy = (3, 2)
        if c == "AUS": dx, dy = (-16, -8)
        if c == "FRA" and "Frech" in col: dx, dy = (3, 5)
        if c == "ITA": dx, dy = (-16, 2)
        ax.annotate(c, (d.loc[c, col], d.loc[c, "FRI_headline"]), xytext=(dx, dy), textcoords="offset points", fontsize=6.5)
    rho = d["FRI_headline"].rank().corr(d[col].rank()) * (1 if sgn == 1 else -1)
    ax.set_title(f"ρ = {rho:.2f} (n = {len(d)})", fontsize=8)
    ax.set_xlabel(lab, fontsize=7)
    if sgn == -1: ax.invert_xaxis()
axes[0].set_ylabel("Free-Rider Index (headline)")
save(fig, "fig4_external_comparison")

# ---------------- Supplementary: PCA biplot
evr, load, pcs = pca(S)
fig, ax = plt.subplots(figsize=(4.8, 4.2))
ax.scatter(pcs["PC1"], pcs["PC2"], color="#1f4e79", s=18)
for c in df.index: ax.annotate(names[c], (pcs.loc[c, "PC1"], pcs.loc[c, "PC2"]), xytext=(4, 3), textcoords="offset points", fontsize=7)
sc_ = 2.5
for k in ORDER:
    ax.arrow(0, 0, load.loc[k, "PC1"] * sc_, load.loc[k, "PC2"] * sc_, color=PAL[k], head_width=0.08, lw=1.2)
    ax.text(load.loc[k, "PC1"] * sc_ * 1.12, load.loc[k, "PC2"] * sc_ * 1.12, LBL[k], color=PAL[k], fontsize=7)
ax.axhline(0, color="#ccc", lw=0.6); ax.axvline(0, color="#ccc", lw=0.6)
ax.set_xlabel(f"PC1 ({evr[0]*100:.0f}% of variance)"); ax.set_ylabel(f"PC2 ({evr[1]*100:.0f}% of variance)")
save(fig, "figS1_pca_biplot")

# ---------------- Supplementary: rank frequency
freq = pd.read_csv(TAB / "table5c_rank_frequency.csv", index_col="iso3").drop(columns="country")
freq = freq.loc[base.sort_values("FRI", ascending=False).index]
fig, ax = plt.subplots(figsize=(5.5, 3.6))
im = ax.imshow(freq.values, cmap="Blues", aspect="auto", vmin=0, vmax=1)
ax.set_xticks(range(freq.shape[1])); ax.set_xticklabels(range(1, freq.shape[1] + 1)); ax.set_yticks(range(len(freq))); ax.set_yticklabels(names[freq.index])
for i in range(freq.shape[0]):
    for j in range(freq.shape[1]):
        if freq.values[i, j] >= 0.05: ax.text(j, i, f"{freq.values[i,j]*100:.0f}", ha="center", va="center", fontsize=6.5, color="white" if freq.values[i, j] > 0.5 else "black")
ax.set_xlabel("Rank"); fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02, label="Share of 10,000 specifications")
save(fig, "figS2_rank_frequency")
print("figures written:", sorted(p.name for p in FIG.glob("*.svg")))
