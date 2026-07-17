"""
Integration test for the decay analysis pipeline, using synthetic data with a
built-in decay effect — no network access required (fetch_french.py is never
called here). This is the closest thing to an end-to-end smoke test we can run
without hitting Ken French's server.
"""

import numpy as np
import pandas as pd

from factor_audit.analysis.decay import FACTORS, run_decay_analysis


def make_synthetic_factor_panel():
    """Builds a monthly panel from 2000-01 to 2019-12 where every factor's premium
    is deliberately larger before 2010 than after -- i.e. H1 should hold by
    construction, which is what we're checking the pipeline correctly detects."""
    dates = pd.date_range("2000-01-01", "2019-12-01", freq="MS")
    rng = np.random.default_rng(0)

    data = {}
    for factor in FACTORS:
        pre_mean, post_mean = 0.01, 0.002  # premium clearly shrinks after the split
        n_pre = (dates < "2010-01-01").sum()
        n_post = (dates >= "2010-01-01").sum()
        pre_returns = rng.normal(pre_mean, 0.02, n_pre)
        post_returns = rng.normal(post_mean, 0.02, n_post)
        data[factor] = np.concatenate([pre_returns, post_returns])

    return pd.DataFrame(data, index=dates)


def test_decay_pipeline_detects_constructed_decay():
    panel = make_synthetic_factor_panel()
    results = run_decay_analysis(panel)

    # One row per factor per window (full_sample, pre_2010, post_2010).
    assert set(results["window"].unique()) == {"full_sample", "pre_2010", "post_2010"}
    assert len(results) == len(FACTORS) * 3

    pivot = results.pivot(index="factor", columns="window", values="gross_annualized_premium")
    # By construction, every factor's post-2010 premium should be smaller than pre-2010.
    assert (pivot["post_2010"] < pivot["pre_2010"]).all()


def test_decay_pipeline_net_premium_always_le_gross():
    panel = make_synthetic_factor_panel()
    results = run_decay_analysis(panel)
    # Costs only ever subtract, so net premium can never exceed gross premium.
    assert (results["net_annualized_premium"] <= results["gross_annualized_premium"] + 1e-9).all()
