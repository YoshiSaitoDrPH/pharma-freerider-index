"""Free-Rider Index: component scoring, aggregation and robustness analysis.

Design follows the OECD/JRC Handbook on Constructing Composite Indicators (2008):
normalisation -> weighting -> aggregation, with uncertainty analysis over all three.
Higher scores = larger apparent free-riding on globally funded pharmaceutical innovation.
The headline is computed for the nine non-US countries; the United States is the numeraire
(reference values by construction for price, availability and delay).
"""
from __future__ import annotations
import numpy as np, pandas as pd

# component id -> (column in countries.csv, direction, label, domain)
# direction +1: higher raw value = more free-riding; -1: higher raw value = less free-riding
COMPONENTS = {
    "P": ("price_index_brand_us100",     -1, "Brand-name originator price level (% of US)",             "Payment"),
    "R": ("rev_to_gdp_ratio_all_innov",  -1, "Innovative-drug revenue share / GDP share",               "Payment"),
    "A": ("reimb_share_2023_pct",        -1, "Share of US-first new drugs publicly reimbursed by 2023",  "Adoption"),
    "D": ("reimb_delay_years",           +1, "Mean interval from US launch to public reimbursement (y)", "Adoption"),
    "I": ("pharma_berd_pct_gdp",         -1, "Pharmaceutical business R&D (% of GDP)",                   "R&D input"),
    # alternative / extension indicators (used by specifications, not in the headline)
    "G": ("gbard_health_pct_gdp",        -1, "Government budget for health R&D (% of GDP; not comparable where GUF dominates)", "R&D input"),
    "T": ("rd_tax_subsidy_large",        -1, "Implied R&D tax subsidy rate, large profitable firm",      "R&D input"),
    "C": ("industry_trials_per_million", -1, "Industry-sponsored trial starts per million per year",     "R&D input"),
}
ORDER = ["P", "R", "A", "D", "I"]
NONUS = ["JPN", "DEU", "FRA", "GBR", "ITA", "CAN", "CHE", "AUS", "KOR"]

def raw_matrix(df, comps=ORDER, overrides=None):
    cols = {k: (overrides or {}).get(k, COMPONENTS[k][0]) for k in comps}
    return pd.DataFrame({k: df[c].astype(float) for k, c in cols.items()}, index=df.index)

def normalise(X, method="minmax", comps=None):
    S = pd.DataFrame(index=X.index)
    for k in X.columns:
        d = COMPONENTS[k][1]
        x = X[k] * d
        if method == "minmax":
            s = (x - x.min()) / (x.max() - x.min()) * 100
        elif method == "zscore":
            s = (x - x.mean()) / x.std(ddof=0) * 20 + 50
        elif method == "rank":
            s = (x.rank(method="average") - 1) / (len(x) - 1) * 100
        elif method == "log_minmax":
            v = np.log(X[k].astype(float).clip(lower=1e-3)) * d
            s = (v - v.min()) / (v.max() - v.min()) * 100
        else:
            raise ValueError(method)
        S[k] = s
    return S

def aggregate(S, weights=None, method="arithmetic"):
    comps = list(S.columns)
    w = np.ones(len(comps)) if weights is None else np.array([weights.get(k, 0.0) for k in comps], float)
    w = w / w.sum()
    if method == "arithmetic":
        return pd.Series(S.values @ w, index=S.index, name="FRI")
    if method == "geometric":
        shift = 1.0 - float(np.nanmin(S.values))
        return pd.Series(np.exp(np.log(S.values + shift) @ w) - shift, index=S.index, name="FRI")
    raise ValueError(method)

def composite(df, weights=None, norm="minmax", agg="arithmetic", comps=ORDER, overrides=None, subset=NONUS, size_adjust=False):
    d = df if subset is None else df.loc[subset]
    X = raw_matrix(d, comps, overrides)
    S = normalise(X, norm)
    if size_adjust:   # residualise each normalised component on log GDP (PPP) across the sample, re-centre to 50
        lg = np.log(d["gdp_ppp_usd"].astype(float))
        Z = np.column_stack([np.ones(len(lg)), lg])
        for k in S.columns:
            beta, *_ = np.linalg.lstsq(Z, S[k].values, rcond=None)
            S[k] = S[k].values - Z @ beta + 50.0
    fri = aggregate(S, weights, agg)
    out = S.copy(); out["FRI"] = fri; out["rank"] = fri.rank(ascending=False, method="min").astype("Int64")
    return out

def domain_weights(comps=ORDER):
    doms = {}
    for k in comps: doms.setdefault(COMPONENTS[k][3], []).append(k)
    return {k: 1.0 / len(doms) / len(v) for dom, v in doms.items() for k in v}

def effective_importance(S: pd.DataFrame, fri: pd.Series) -> pd.Series:
    """Squared Pearson correlation of each normalised component with the composite (Paruolo, Saisana & Saltelli 2013)."""
    return pd.Series({k: np.corrcoef(S[k], fri)[0, 1] ** 2 for k in S.columns}, name="effective_importance")

def equal_importance_weights(S: pd.DataFrame, iters=200):
    """Iteratively adjust nominal weights until effective importances are (approximately) equal (Becker et al 2017)."""
    w = {k: 1.0 for k in S.columns}
    for _ in range(iters):
        fri = aggregate(S, w); imp = effective_importance(S, fri)
        target = imp.mean()
        for k in S.columns:
            w[k] *= (target / max(imp[k], 1e-6)) ** 0.5
        tot = sum(w.values()); w = {k: v / tot for k, v in w.items()}
    return w, effective_importance(S, aggregate(S, w))

# calibrated input noise: multiplicative for P, R, I (log-normal sigma), additive for A (pp) and D (years)
NOISE = {"P": ("mult", 0.05), "R": ("mult", 0.05), "A": ("add", 3.0), "D": ("add", 0.3), "I": ("mult", 0.50),
         "G": ("mult", 0.50), "T": ("add", 0.02), "C": ("mult", 0.15)}
# discrete source switches: component -> list of alternative columns (drawn with equal probability incl. headline)
SWITCHES = {"P": ["price_index_brand_us100", "price_index_all_us100"],
            "R": ["rev_to_gdp_ratio_all_innov", "rev_to_gdp_ratio_new_innov"],
            "I": ["pharma_berd_pct_gdp", "pharma_rd_pct_gdp_assoc", "industry_trials_per_million"]}

def monte_carlo(df, n=10000, seed=2026, comps=ORDER, subset=NONUS, use_switches=True, noise=NOISE, ad_corr=0.0):
    """ad_corr: correlation of the noise shocks applied to A and D (shared data source); 0 = independent."""
    rng = np.random.default_rng(seed)
    d = df if subset is None else df.loc[subset]
    norms = ["minmax", "zscore", "rank", "log_minmax"]; aggs = ["arithmetic", "geometric"]
    ranks = np.zeros((n, len(d)), int); scores = np.zeros((n, len(d)))
    for i in range(n):
        w = dict(zip(comps, rng.dirichlet(np.ones(len(comps)))))
        ov = {}
        if use_switches:
            for k, alts in SWITCHES.items():
                if k in comps: ov[k] = alts[rng.integers(len(alts))]
        X = raw_matrix(d, comps, ov).copy()
        zA = rng.normal(0, 1, len(X)); zD = ad_corr * zA + np.sqrt(1 - ad_corr ** 2) * rng.normal(0, 1, len(X))
        for k in comps:
            kind, sc = noise.get(k, ("mult", 0.0))
            z = zA if k == "A" else (zD if k == "D" else rng.normal(0, 1, len(X)))
            if kind == "mult": X[k] = X[k] * np.exp(sc * z)
            else: X[k] = X[k] + sc * z
            if COMPONENTS[k][1] == -1 and k in ("A",): X[k] = X[k].clip(0, 100)
            if k == "D": X[k] = X[k].clip(lower=0)
        S = normalise(X, norms[rng.integers(len(norms))])
        fri = aggregate(S, w, aggs[rng.integers(len(aggs))])
        scores[i] = fri.values
        ranks[i] = fri.rank(ascending=False, method="min").values
    k = len(d)
    summ = pd.DataFrame({
        "rank_median": np.median(ranks, 0), "rank_p05": np.percentile(ranks, 5, 0), "rank_p95": np.percentile(ranks, 95, 0),
        "rank_mode": [np.bincount(ranks[:, j]).argmax() for j in range(k)],
        "share_top3": (ranks <= 3).mean(0), "share_bottom3": (ranks >= k - 2).mean(0),
        "score_mean": scores.mean(0), "score_p05": np.percentile(scores, 5, 0), "score_p95": np.percentile(scores, 95, 0),
    }, index=d.index)
    return ranks, summ

def monte_carlo_component(df, n=5000, seed=7, comps=ORDER, subset=NONUS, vary_weights=False, vary_method=False, vary_noise=False, vary_source=False):
    """Monte Carlo varying one source of uncertainty at a time (others held at the headline setting)."""
    rng = np.random.default_rng(seed)
    d = df if subset is None else df.loc[subset]
    norms = ["minmax", "zscore", "rank", "log_minmax"]; aggs = ["arithmetic", "geometric"]
    ranks = np.zeros((n, len(d)), int)
    for i in range(n):
        w = dict(zip(comps, rng.dirichlet(np.ones(len(comps))))) if vary_weights else None
        ov = {}
        if vary_source:
            for k, alts in SWITCHES.items():
                if k in comps: ov[k] = alts[rng.integers(len(alts))]
        X = raw_matrix(d, comps, ov).copy()
        if vary_noise:
            for k in comps:
                kind, sc = NOISE.get(k, ("mult", 0.0))
                X[k] = X[k] * np.exp(rng.normal(0, sc, len(X))) if kind == "mult" else X[k] + rng.normal(0, sc, len(X))
                if k == "A": X[k] = X[k].clip(0, 100)
                if k == "D": X[k] = X[k].clip(lower=0)
        nm = norms[rng.integers(len(norms))] if vary_method else "minmax"
        ag = aggs[rng.integers(len(aggs))] if vary_method else "arithmetic"
        fri = aggregate(normalise(X, nm), w, ag)
        ranks[i] = fri.rank(ascending=False, method="min").values
    k = len(d)
    return ranks, pd.DataFrame({"rank_median": np.median(ranks, 0), "rank_p05": np.percentile(ranks, 5, 0), "rank_p95": np.percentile(ranks, 95, 0),
                                "share_top3": (ranks <= 3).mean(0), "share_bottom3": (ranks >= k - 2).mean(0)}, index=d.index)

def leave_one_component_out(df, comps=ORDER, **kw):
    out = {}
    for k in comps:
        out[f"drop_{k}"] = composite(df, comps=[c for c in comps if c != k], **kw)["FRI"]
    return pd.DataFrame(out)

def leave_one_country_out(df, subset=NONUS, **kw):
    out = {}
    for c in subset:
        sub = [x for x in subset if x != c]
        r = composite(df, subset=sub, **kw)["rank"]
        out[f"−{c}"] = r
    return pd.DataFrame(out).reindex(subset)

def pca(S):
    Z = (S - S.mean()) / S.std(ddof=0)
    U, sv, Vt = np.linalg.svd(Z.values, full_matrices=False)
    evr = sv**2 / (sv**2).sum()
    loadings = pd.DataFrame(Vt.T * sv / np.sqrt(len(Z)), index=S.columns, columns=[f"PC{i+1}" for i in range(len(sv))])
    scores = pd.DataFrame(U * sv, index=S.index, columns=loadings.columns)
    if np.corrcoef(scores["PC1"], S.mean(1))[0, 1] < 0:
        scores["PC1"] *= -1; loadings["PC1"] *= -1
    return evr, loadings, scores

def spearman(a, b):
    d = pd.concat([a, b], axis=1).dropna()
    return d.iloc[:, 0].rank().corr(d.iloc[:, 1].rank()), len(d)

def spearman_ci(rho, n, z=1.96):
    """Fisher z interval for a rank correlation (approximate; n small)."""
    if n < 4 or abs(rho) >= 1: return (np.nan, np.nan)
    se = 1.0 / np.sqrt(n - 3); f = np.arctanh(rho)
    return (np.tanh(f - z * se), np.tanh(f + z * se))

def spearman_perm_p(a, b, n_perm=20000, seed=1):
    d = pd.concat([a, b], axis=1).dropna(); x = d.iloc[:, 0].rank().values; y = d.iloc[:, 1].rank().values
    obs = np.corrcoef(x, y)[0, 1]; rng = np.random.default_rng(seed)
    cnt = sum(abs(np.corrcoef(x, rng.permutation(y))[0, 1]) >= abs(obs) - 1e-12 for _ in range(n_perm))
    return cnt / n_perm
