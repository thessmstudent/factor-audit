"""
Unit tests for the stats module, using synthetic data only — no network dependency.
Run with: pytest (from the factor-audit/ root, after `pip install -e .`)
"""

import numpy as np
import pytest

from factor_audit.stats.tests import (
    HLZ_TSTAT_THRESHOLD,
    annualized_premium,
    bootstrap_ci,
    deflated_sharpe_ratio,
    expected_max_sharpe_under_null,
    premium_ttest,
    sharpe_ratio,
)


def make_returns(mean, std, n, seed=1):
    rng = np.random.default_rng(seed)
    return rng.normal(loc=mean, scale=std, size=n)


def test_annualized_premium_scales_by_twelve():
    returns = np.full(24, 0.01)  # exactly 1% every month
    assert annualized_premium(returns) == pytest.approx(0.12)


def test_premium_ttest_detects_clear_positive_premium():
    # Large, consistent positive mean with modest noise -> should be highly significant.
    returns = make_returns(mean=0.02, std=0.01, n=300, seed=1)
    result = premium_ttest(returns)
    assert result["mean_monthly"] > 0
    assert result["t_stat"] > HLZ_TSTAT_THRESHOLD
    assert result["clears_hlz_bar"] is True


def test_premium_ttest_detects_no_premium():
    # Mean zero, pure noise -> should NOT clear the HLZ bar (with overwhelming probability).
    returns = make_returns(mean=0.0, std=0.04, n=120, seed=2)
    result = premium_ttest(returns)
    assert abs(result["t_stat"]) < HLZ_TSTAT_THRESHOLD
    assert result["clears_hlz_bar"] is False


def test_premium_ttest_requires_min_observations():
    with pytest.raises(ValueError):
        premium_ttest(np.array([0.01]))


def test_bootstrap_ci_contains_true_mean_most_of_the_time():
    true_mean = 0.01
    returns = make_returns(mean=true_mean, std=0.03, n=400, seed=3)
    result = bootstrap_ci(returns, n_boot=2000, seed=7)
    assert result["ci_low"] < result["point_estimate"] < result["ci_high"]
    # With 400 observations and a reasonably tight sampling distribution, the true
    # mean should typically fall inside a 95% CI.
    assert result["ci_low"] <= true_mean <= result["ci_high"]


def test_sharpe_ratio_zero_std_returns_nan():
    returns = np.full(10, 0.01)  # zero variance
    assert np.isnan(sharpe_ratio(returns))


def test_expected_max_sharpe_increases_with_more_trials():
    sr0_few = expected_max_sharpe_under_null(sr_std=1.0, n_trials=5)
    sr0_many = expected_max_sharpe_under_null(sr_std=1.0, n_trials=500)
    assert sr0_many > sr0_few > 0


def test_deflated_sharpe_penalizes_more_trials():
    # Same return series, more assumed trials -> lower (or equal) deflated Sharpe ratio.
    returns = make_returns(mean=0.015, std=0.03, n=180, seed=4)
    dsr_few_trials = deflated_sharpe_ratio(returns, n_trials=1)
    dsr_many_trials = deflated_sharpe_ratio(returns, n_trials=200)
    assert dsr_many_trials["deflated_sharpe_ratio"] <= dsr_few_trials["deflated_sharpe_ratio"]


def test_deflated_sharpe_requires_min_observations():
    with pytest.raises(ValueError):
        deflated_sharpe_ratio(np.array([0.01, 0.02, 0.01]), n_trials=1)
