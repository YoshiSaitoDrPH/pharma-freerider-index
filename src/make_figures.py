"""Publication figures (SVG + 300-dpi PNG). Headline = nine non-US countries.
Fig 1  Headline index with component contributions (A) and Monte Carlo rank intervals (B)
Fig 2  Rank robustness heatmap: specifications S0-S22 and leave-one-component-out
Fig 3  Comparison with the Kolchinsky-Xie index: headline, payment sub-index, adoption sub-index
S1 PCA biplot; S2 rank-frequency matrix; S3 payment x adoption domain map; S4 leave-one-country-out
"""
import pathlib, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from frindex import ORDER, NONUS, normalise, raw_matrix, pca

ROOT = pathlib.Path(__file__).resolve().parents[1]
TAB, FIG, PROC = ROOT / "tables", ROOT / "figures", ROOT / "data" / "processed"
FIG.mkdir(exist_ok=True)
plt.rcParams.update({"font.family": "serif", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False, "axes.titleweight": "bold", "figure.dpi": 110})
PAL = {"P": "#1f4e79", "R": "#2e75b6", "A": "#c55a11", "D": "#f4b183", "I": "#548235"}
LBL = {"P": "Brand price level", "R": "Revenue/GDP", "A": "Availability", "D": "Interval to reimbursement", "I": "Pharma R&D"}
df = pd.read_csv(PROC / "countries.csv", index_col="iso3")
base = pd.read_csv(TAB / "table2_headline_index.csv", index_col="iso3")
mc = pd.read_csv(TAB / "table5_montecarlo_rank_intervals.csv", index_col="iso3")
ranks = pd.read_csv(TAB / "table3_rank_by_specification.csv", index_col="iso3")
ext = pd.read_csv(TAB / "table7_external_comparators.csv", index_col="iso3")
lcoo = pd.read_csv(TAB / "table3c_leave_one_country_out_ranks.csv", index_col="iso3")
names = df["country"]
def save(fig, name):
    fig.savefig(FIG / f"{name}.svg", bbox_inches="tight"); fig.savefig(FIG / f"{name}.png", dpi=300, bbox_inches="tight"); plt.close(fig)
for old in ["fig3_domain_map", "fig4_external_comparison"]:
    for ext_ in ("svg", "png"): (FIG / f"{old}.{ext_}").unlink(missing_ok=True)

# ---------------- Figure 1
order = base.sort_values("FRI").index
fig, (ax, ax2) = plt.subplots(1, 2, figsize=(7.2, 3.4), gridspec_kw={"width_ratios": [3, 1.3]}, sharey=True)
left = np.zeros(len(order))
for k in ORDER:
    v = base.loc[order, k].values / len(ORDER)
    ax.barh(range(len(order)), v, left=left, color=PAL[k], label=LBL[k]); left += v
for i, c in enumerate(order): ax.text(left[i] + 1, i, f"{base.loc[c,'FRI']:.0f}", va="center", fontsize=8)
ax.set_yticks(range(len(order))); ax.set_yticklabels(names[order]); ax.set_xlabel("Free-Rider Index (0–100), nine countries, equal weights"); ax.set_xlim(0, 105)
ax.legend(frameon=False, fontsize=6.8, loc="lower right", title="Component", title_fontsize=7)
ax.set_title("A. Headline index and component contributions", loc="left", fontsize=9)
for i, c in enumerate(order):
    ax2.plot([mc.loc[c, "rank_p05"], mc.loc[c, "rank_p95"]], [i, i], color="#7f7f7f", lw=2)
    ax2.plot(mc.loc[c, "rank_median"], i, "o", color="black", ms=4); ax2.plot(base.loc[c, "rank"], i, "|", color="#c00000", ms=9, mew=1.5)
ax2.set_xlim(0.5, len(order) + 0.5); ax2.set_xticks(range(1, len(order) + 1)); ax2.invert_xaxis()
ax2.set_xlabel("Rank (1 = most apparent free-riding)"); ax2.set_title("B. Rank across 10,000 specifications", loc="left", fontsize=9)
ax2.text(0.02, 0.02, "bar: 5th–95th pct; dot: median; red: headline", transform=ax2.transAxes, fontsize=6.3)
save(fig, "fig1_headline_index")

# ---------------- Figure 2 heatmap (nine countries)
R = ranks.drop(columns="country").loc[base.sort_values("FRI", ascending=False).index]
R = R.drop(columns=[c for c in R.columns if c.startswith("S21")])  # ten-country spec shown in supplement
cols = [c.split(" ", 1)[0] if c.startswith("S") else c.replace("drop_", "−") for c in R.columns]
fig, ax = plt.subplots(figsize=(7.4, 3.5))
im = ax.imshow(R.values.astype(float), cmap="RdYlBu", aspect="auto", vmin=1, vmax=9)
ax.set_xticks(range(len(cols))); ax.set_xticklabels(cols, rotation=45, ha="right", fontsize=7)
ax.set_yticks(range(len(R))); ax.set_yticklabels(names[R.index])
for i in range(R.shape[0]):
    for j in range(R.shape[1]):
        v = R.values[i, j]
        if not np.isnan(v): ax.text(j, i, f"{int(v)}", ha="center", va="center", fontsize=7)
cb = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02); cb.set_label("Rank (1 = most apparent free-riding)")
ax.set_title("Rank by specification and by dropped component (nine countries)", loc="left", fontsize=9)
ax.set_xlabel("S0 headline · S1 domain weights · S2 payment only · S3 adoption only · S4 price only · S5 geometric · S6 z-score · S7 rank · S8 log min–max · S9 all-drug price\n"
              "S10 income-adj. price · S11 ability-to-pay · S12 new-drug revenue · S13 imputed delay · S14 W.A.I.T. EU-5 · S15 association R&D · S16 trials replace R&D\n"
              "S17 payment + adoption only · S18 +tax subsidy · S19 +tax +trials · S20 size-adjusted · −X: component X dropped", fontsize=6.3)
save(fig, "fig2_rank_robustness")

# ---------------- Figure 3: Kolchinsky–Xie decomposition
S = normalise(raw_matrix(df.loc[NONUS]))
kx = df.loc[NONUS, "kolchinsky_freeriding_index_pct"]
panels = [("Headline index", base["FRI"]), ("Payment sub-index (P, R)", S[["P", "R"]].mean(1)), ("Adoption sub-index (A, D)", S[["A", "D"]].mean(1))]
fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.6))
for ax, (lab, y) in zip(axes, panels):
    d = pd.concat([kx, y], axis=1).dropna(); d.columns = ["kx", "y"]
    ax.scatter(d.kx, d.y, color="#1f4e79", s=20)
    for c in d.index:
        dx, dy = (3, 2)
        if c == "FRA": dx, dy = (3, -9)
        ax.annotate(c, (d.loc[c, "kx"], d.loc[c, "y"]), xytext=(dx, dy), textcoords="offset points", fontsize=6.5)
    rho = d.kx.rank().corr(d.y.rank())
    ax.set_title(f"{lab}\nρ = {rho:.2f} (n = {len(d)})", fontsize=8)
axes[0].set_ylabel("Score (0–100)")
fig.supxlabel("Kolchinsky & Xie (2025) Freeriding Index, % (net brand price relative to income)", fontsize=8)
save(fig, "fig3_external_comparison")

# ---------------- S1 PCA biplot
evr, load, pcs = pca(S)
fig, ax = plt.subplots(figsize=(4.8, 4.2))
ax.scatter(pcs["PC1"], pcs["PC2"], color="#1f4e79", s=18)
for c in S.index: ax.annotate(names[c], (pcs.loc[c, "PC1"], pcs.loc[c, "PC2"]), xytext=(4, 3), textcoords="offset points", fontsize=7)
for k in ORDER:
    ax.arrow(0, 0, load.loc[k, "PC1"] * 2.5, load.loc[k, "PC2"] * 2.5, color=PAL[k], head_width=0.08, lw=1.2)
    ax.text(load.loc[k, "PC1"] * 2.8, load.loc[k, "PC2"] * 2.8, LBL[k], color=PAL[k], fontsize=7)
ax.axhline(0, color="#ccc", lw=0.6); ax.axvline(0, color="#ccc", lw=0.6)
ax.set_xlabel(f"PC1 ({evr[0]*100:.0f}% of variance)"); ax.set_ylabel(f"PC2 ({evr[1]*100:.0f}% of variance)")
save(fig, "figS1_pca_biplot")

# ---------------- S2 rank frequency
freq = pd.read_csv(TAB / "table5d_rank_frequency.csv", index_col="iso3").drop(columns="country").loc[base.sort_values("FRI", ascending=False).index]
fig, ax = plt.subplots(figsize=(5.5, 3.4))
im = ax.imshow(freq.values, cmap="Blues", aspect="auto", vmin=0, vmax=1)
ax.set_xticks(range(freq.shape[1])); ax.set_xticklabels(range(1, freq.shape[1] + 1)); ax.set_yticks(range(len(freq))); ax.set_yticklabels(names[freq.index])
for i in range(freq.shape[0]):
    for j in range(freq.shape[1]):
        if freq.values[i, j] >= 0.05: ax.text(j, i, f"{freq.values[i,j]*100:.0f}", ha="center", va="center", fontsize=6.5, color="white" if freq.values[i, j] > 0.5 else "black")
ax.set_xlabel("Rank"); fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02, label="Share of 10,000 specifications")
save(fig, "figS2_rank_frequency")

# ---------------- S3 domain map
pay = S[["P", "R"]].mean(1); acc = S[["A", "D"]].mean(1); rd = S["I"]
size = df.loc[NONUS, "rev_share_all_innov_pct"].clip(lower=0.3) * 60
fig, ax = plt.subplots(figsize=(5.2, 4.2))
sc = ax.scatter(pay, acc, s=size, c=rd, cmap="Greens_r", edgecolor="black", lw=0.6, alpha=0.9, vmin=0, vmax=100)
OFF = {"JPN": (8, -10), "FRA": (8, 4), "GBR": (8, 4), "ITA": (8, -10), "CHE": (8, 4), "DEU": (8, 4), "CAN": (8, 4), "AUS": (8, 4), "KOR": (-48, 8)}
for c in NONUS: ax.annotate(names[c], (pay[c], acc[c]), xytext=OFF.get(c, (6, 4)), textcoords="offset points", fontsize=7.5)
ax.axvline(50, color="#bbbbbb", lw=0.7, ls="--"); ax.axhline(50, color="#bbbbbb", lw=0.7, ls="--")
ax.set_xlabel("Payment score (brand price, revenue/GDP) → more apparent free-riding"); ax.set_ylabel("Adoption score (availability, interval) → more")
cb = fig.colorbar(sc, ax=ax, fraction=0.04, pad=0.02); cb.set_label("Pharma R&D score (dark = high R&D)")
ax.set_xlim(-5, 108); ax.set_ylim(-5, 108)
ax.text(0.99, 0.01, "bubble area ∝ share of OECD innovative-drug revenue", transform=ax.transAxes, ha="right", fontsize=6.5)
save(fig, "figS3_domain_map")

# ---------------- S4 leave-one-country-out
L = lcoo.drop(columns="country").loc[base.sort_values("FRI", ascending=False).index]
fig, ax = plt.subplots(figsize=(5.5, 3.2))
im = ax.imshow(L.values.astype(float), cmap="RdYlBu", aspect="auto", vmin=1, vmax=8)
ax.set_xticks(range(L.shape[1])); ax.set_xticklabels(L.columns, fontsize=7); ax.set_yticks(range(len(L))); ax.set_yticklabels(names[L.index])
for i in range(L.shape[0]):
    for j in range(L.shape[1]):
        v = L.values[i, j]
        if not np.isnan(v): ax.text(j, i, f"{int(v)}", ha="center", va="center", fontsize=7)
ax.set_xlabel("Country removed from the sample"); fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02, label="Rank among remaining eight")
save(fig, "figS4_leave_one_country_out")
print("figures:", sorted(p.name for p in FIG.glob("*.svg")))
