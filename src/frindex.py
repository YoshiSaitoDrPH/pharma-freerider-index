"""Free-Rider Index: component scoring, aggregation and robustness analysis.

Design follows the OECD/JRC Handbook on Constructing Composite Indicators (2008):
normalisation -> weighting -> aggregation, with uncertainty analysis over all three.
Higher scores = larger apparent free-riding on globally funded pharmaceutical innovation.
"""
from __future__ import annotations
import numpy as np, pandas as pd

# component id -> (column in countries.csv, direction, label, domain)
# direction +1: higher raw value = more free-riding; -1: higher raw value = less free-riding
COMPONENTS = {
    "P": ("price_index_all_us100",      -1, "Relative price level (% of US, all drugs)",              "Payment"),
    "R": ("rev_to_gdp_ratio_all_innov", -1, "Innovative-drug revenue share / GDP share",              "Payment"),
    "A": ("reimb_share_2023_pct",       -1, "Share of US-first new drugs publicly reimbursed by 2023", "Access"),
    "D": ("reimb_delay_years",          +1, "Mean reimbursement delay after US launch (years)",        "Access"),
    "I": ("pharma_berd_pct_gdp",        -1, "Pharmaceutical business R&D (% of GDP)",                  "R&D input"),
}
ORDER = list(COMPONENTS)

def raw_matrix(df: pd.DataFrame, comps=ORDER, overrides: dict | None = None) -> pd.DataFrame:
    """Return raw component values (columns = component ids). `overrides` maps id -> column name."""
    cols = {k: (overrides or {}).get(k, COMPONENTS[k][0]) for k in comps}
    return pd.DataFrame({k: df[c].astype(float) for k, c in cols.items()}, index=df.index)

def normalise(X: pd.DataFrame, method="minmax", comps=ORDER) -> pd.DataFrame:
    """Map each component to a 0-100 'free-riding' scale (direction-adjusted)."""
    S = pd.DataFrame(index=X.index)
    for k in X.columns:
        x = X[k] * COMPONENTS[k][1]          # direction so that higher = more free-riding
        if method == "minmax":
            s = (x - x.min()) / (x.max() - x.min()) * 100
        elif method == "zscore":
            s = (x - x.mean()) / x.std(ddof=0) * 20 + 50      # centred at 50, SD 20
        elif method == "rank":
            s = (x.rank(method="average") - 1) / (len(x) - 1) * 100
        elif method == "log_minmax":
            v = X[k].astype(float); v = np.log(v.clip(lower=1e-3)) * COMPONENTS[k][1]
            s = (v - v.min()) / (v.max() - v.min()) * 100
        else:
            raise ValueError(method)
        S[k] = s
    return S

def aggregate(S: pd.DataFrame, weights: dict | None = None, method="arithmetic") -> pd.Series:
    comps = list(S.columns)
    w = np.array([1.0] * len(comps)) if weights is None else np.array([weights.get(k, 0.0) for k in comps], float)
    w = w / w.sum()
    if method == "arithmetic":
        return pd.Series(S.values @ w, index=S.index, name="FRI")
    if method == "geometric":   # shift so that the minimum is 1 (avoids log of zero/negative values)
        shift = 1.0 - float(np.nanmin(S.values))
        return pd.Series(np.exp((np.log(S.values + shift)) @ w) - shift, index=S.index, name="FRI")
    raise ValueError(method)

def composite(df, weights=None, norm="minmax", agg="arithmetic", comps=ORDER, overrides=None, subset=None):
    d = df if subset is None else df.loc[subset]
    X = raw_matrix(d, comps, overrides)
    S = normalise(X, norm, comps)
    fri = aggregate(S, weights, agg)
    out = S.copy(); out["FRI"] = fri; out["rank"] = fri.rank(ascending=False, method="min").astype("Int64")
    return out

def domain_weights(comps=ORDER) -> dict:
    """Equal weight per domain, split equally within domain (Payment 1/3, Access 1/3, R&D 1/3)."""
    doms = {}
    for k in comps: doms.setdefault(COMPONENTS[k][3], []).append(k)
    return {k: 1.0 / len(doms) / len(v) for dom, v in doms.items() for k in v}

def monte_carlo(df, n=10000, seed=2026, comps=ORDER, input_noise=0.10, subset=None):
    """Joint uncertainty analysis over weights (Dirichlet(1)), normalisation, aggregation and +-input noise.
    Returns rank draws (n x countries) and a summary table."""
    rng = np.random.default_rng(seed)
    d = df if subset is None else df.loc[subset]
    X0 = raw_matrix(d, comps)
    norms = ["minmax", "zscore", "rank"]; aggs = ["arithmetic", "geometric"]
    ranks = np.zeros((n, len(d)), int); scores = np.zeros((n, len(d)))
    for i in range(n):
        w = dict(zip(comps, rng.dirichlet(np.ones(len(comps)))))
        X = X0 * (1 + rng.uniform(-input_noise, input_noise, X0.shape)) if input_noise else X0
        S = normalise(X, norms[rng.integers(len(norms))], comps)
        fri = aggregate(S, w, aggs[rng.integers(len(aggs))])
        scores[i] = fri.values
        ranks[i] = fri.rank(ascending=False, method="min").values
    summ = pd.DataFrame({
        "rank_median": np.median(ranks, 0), "rank_p05": np.percentile(ranks, 5, 0), "rank_p95": np.percentile(ranks, 95, 0),
        "rank_mode": [np.bincount(ranks[:, j]).argmax() for j in range(ranks.shape[1])],
        "p_top3": (ranks <= 3).mean(0), "p_bottom3": (ranks >= len(d) - 2).mean(0),
        "score_mean": scores.mean(0), "score_p05": np.percentile(scores, 5, 0), "score_p95": np.percentile(scores, 95, 0),
    }, index=d.index)
    return ranks, summ

def jackknife(df, comps=ORDER, **kw):
    """Composite with each component dropped in turn (equal weights on the rest)."""
    out = {}
    for k in comps:
        rest = [c for c in comps if c != k]
        out[f"drop_{k}"] = composite(df, comps=rest, **kw)["FRI"]
    return pd.DataFrame(out)

def pca(S: pd.DataFrame):
    """PCA on standardised component scores (SVD). Returns explained variance ratio, loadings, scores."""
    Z = (S - S.mean()) / S.std(ddof=0)
    U, sv, Vt = np.linalg.svd(Z.values, full_matrices=False)
    evr = sv**2 / (sv**2).sum()
    loadings = pd.DataFrame(Vt.T * sv / np.sqrt(len(Z)), index=S.columns, columns=[f"PC{i+1}" for i in range(len(sv))])
    scores = pd.DataFrame(U * sv, index=S.index, columns=loadings.columns)
    # orient PC1 so that it correlates positively with the equal-weight composite
    if np.corrcoef(scores["PC1"], S.mean(1))[0, 1] < 0:
        scores["PC1"] *= -1; loadings["PC1"] *= -1
    return evr, loadings, scores

def spearman(a: pd.Series, b: pd.Series) -> float:
    d = pd.concat([a, b], axis=1).dropna()
    return d.iloc[:, 0].rank().corr(d.iloc[:, 1].rank())
