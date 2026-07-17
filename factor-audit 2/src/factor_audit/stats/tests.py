"""
Statistical tools for the decay analysis (H1, H2) and the composite-factor stretch (H3).

Every function here takes plain numpy arrays / pandas Series of periodic returns and
returns plain numbers — no hidden state, no network calls, fully unit-testable with
synthetic data. See tests/test_stats.py.

References:
- Harvey, Liu & Zhu (2016), "...and the Cross-Section of Expected Returns", RFS.
- McLean & Pontiff (2016), "Does Academic Research Destroy Stock Return Predictability?", JF.
- Bailey & Lopez de Prado (2014), "The Deflated Sharpe Ratio", Journal of Portfolio Management.
"""

from __future__ import annotations

import numpy as np
from scipy import stats as sp_stats

EULER_MASCHERONI = 0.5772156649015329

HLZ_TSTAT_THRESHOLD = 3.0  # Harvey-Liu-Zhu's suggested bar, vs. the classical 2.0.


def annualized_premium(monthly_returns: np.ndarray, periods_per_year: int = 12) -> float:
    """Simple arithmetic annualization of a mean monthly return. Deliberately simple
    (not compounded) since we're comparing premia across sub-periods, not forecasting
    terminal wealth."""
    return float(np.mean(monthly_returns) * periods_per_year)


def premium_ttest(monthly_returns: np.ndarray) -> dict:
    """One-sample t-test of whether mean monthly return differs from zero.
    Returns mean, t-stat, p-value, and whether it clears the HLZ bar."""
    monthly_returns = np.asarray(monthly_returns, dtype=float)
    monthly_returns = monthly_returns[~np.isnan(monthly_returns)]
    n = len(monthly_returns)
    if n < 2:
        raise ValueError("Need at least 2 observations for a t-test.")
    mean = float(np.mean(monthly_returns))
    se = float(np.std(monthly_returns, ddof=1) / np.sqrt(n))
    has_variance = se > 1e-10
    t_stat = mean / se if has_variance else float("nan")
    p_value = float(2 * (1 - sp_stats.t.cdf(abs(t_stat), df=n - 1))) if has_variance else float("nan")
    return {
        "n_obs": n,
        "mean_monthly": mean,
        "annualized_premium": annualized_premium(monthly_returns),
        "t_stat": t_stat,
        "p_value": p_value,
        "clears_hlz_bar": bool(abs(t_stat) >= HLZ_TSTAT_THRESHOLD),
    }


def bootstrap_ci(
    monthly_returns: np.ndarray,
    n_boot: int = 10_000,
    ci: float = 0.95,
    seed: int | None = 42,
) -> dict:
    """Percentile bootstrap confidence interval on the mean monthly return.
    Used as a check against relying purely on the t-test's normality assumption."""
    monthly_returns = np.asarray(monthly_returns, dtype=float)
    monthly_returns = monthly_returns[~np.isnan(monthly_returns)]
    rng = np.random.default_rng(seed)
    n = len(monthly_returns)
    boot_means = np.empty(n_boot)
    for i in range(n_boot):
        sample = rng.choice(monthly_returns, size=n, replace=True)
        boot_means[i] = sample.mean()
    lower_pct = (1 - ci) / 2 * 100
    upper_pct = (1 + ci) / 2 * 100
    return {
        "ci_level": ci,
        "point_estimate": float(np.mean(monthly_returns)),
        "ci_low": float(np.percentile(boot_means, lower_pct)),
        "ci_high": float(np.percentile(boot_means, upper_pct)),
    }


def sharpe_ratio(monthly_returns: np.ndarray, periods_per_year: int = 12) -> float:
    monthly_returns = np.asarray(monthly_returns, dtype=float)
    monthly_returns = monthly_returns[~np.isnan(monthly_returns)]
    std = np.std(monthly_returns, ddof=1)
    if std < 1e-10:  # effectively zero variance; avoid a floating-point blow-up
        return float("nan")
    return float(np.mean(monthly_returns) / std * np.sqrt(periods_per_year))


def expected_max_sharpe_under_null(sr_std: float, n_trials: int) -> float:
    """Bailey & Lopez de Prado's approximation for the expected maximum Sharpe ratio
    you'd see by chance across `n_trials` independent strategy variants, given the
    standard deviation of the Sharpe-ratio estimator `sr_std`.

    E[max SR] ~= sr_std * [ (1-gamma) * Phi^-1(1 - 1/N) + gamma * Phi^-1(1 - 1/(N*e)) ]
    """
    if n_trials < 2:
        return 0.0
    inv1 = sp_stats.norm.ppf(1 - 1.0 / n_trials)
    inv2 = sp_stats.norm.ppf(1 - 1.0 / (n_trials * np.e))
    return float(sr_std * ((1 - EULER_MASCHERONI) * inv1 + EULER_MASCHERONI * inv2))


def deflated_sharpe_ratio(
    monthly_returns: np.ndarray,
    n_trials: int,
    sr_std: float | None = None,
    periods_per_year: int = 12,
) -> dict:
    """Bailey & Lopez de Prado (2014) deflated Sharpe ratio: the probability that the
    observed Sharpe ratio is genuinely positive after correcting for (a) the number of
    strategy variants tried (n_trials) and (b) non-normality (skew/kurtosis) of returns.

    `sr_std` is the assumed standard deviation of the Sharpe-ratio estimator across
    trials; if not supplied, a common simplifying default of 1.0 is used (this is a
    modeling choice — state it explicitly in the write-up rather than treating it as
    a precise input).
    """
    monthly_returns = np.asarray(monthly_returns, dtype=float)
    monthly_returns = monthly_returns[~np.isnan(monthly_returns)]
    n = len(monthly_returns)
    if n < 4:
        raise ValueError("Need at least 4 observations to estimate skew/kurtosis reliably.")

    sr_hat = sharpe_ratio(monthly_returns, periods_per_year=periods_per_year) / np.sqrt(periods_per_year)
    # sr_hat above is un-annualized (per-period) Sharpe, matching the DSR derivation's convention.
    skew = float(sp_stats.skew(monthly_returns))
    kurt = float(sp_stats.kurtosis(monthly_returns, fisher=False))  # non-excess kurtosis

    if sr_std is None:
        sr_std = 1.0
    sr0 = expected_max_sharpe_under_null(sr_std, n_trials)

    denom = np.sqrt(max(1 - skew * sr_hat + ((kurt - 1) / 4) * sr_hat**2, 1e-12))
    z = (sr_hat - sr0) * np.sqrt(n - 1) / denom
    dsr = float(sp_stats.norm.cdf(z))

    return {
        "sharpe_hat_annualized": sharpe_ratio(monthly_returns, periods_per_year=periods_per_year),
        "sr0_expected_max_under_null": sr0,
        "n_trials_assumed": n_trials,
        "deflated_sharpe_ratio": dsr,
        "interpretation": (
            "Probability the true Sharpe ratio is positive, after correcting for "
            f"having tried {n_trials} variant(s). Values near 1.0 are strong; values "
            "near 0.5 mean the result is indistinguishable from what chance alone "
            "would produce across that many trials."
        ),
    }
