"""
Runs H1 and H2 (see PREREGISTRATION.md) against the cached Ken French factor data:
full-sample vs. post-2010 premia, before and after the cost haircut.

Usage (after running `python -m factor_audit.data.fetch_french` once, with network access):

    python -m factor_audit.analysis.decay
"""

from __future__ import annotations

import pandas as pd

from factor_audit.data.fetch_french import load_all_factors
from factor_audit.factors.costs import apply_cost_haircut
from factor_audit.stats.tests import premium_ttest

FACTORS = ["Mkt-RF", "SMB", "HML", "RMW", "CMA", "UMD"]
SPLIT_DATE = "2010-01-01"


def run_decay_analysis(df: pd.DataFrame, split_date: str = SPLIT_DATE) -> pd.DataFrame:
    """Returns one row per factor x window x cost-adjustment, per PREREGISTRATION.md's
    H1 (does the premium shrink post-split?) and H2 (does it lose HLZ significance
    after the cost haircut?)."""
    rows = []
    pre = df[df.index < split_date]
    post = df[df.index >= split_date]

    for factor in FACTORS:
        for window_name, window_df in [("full_sample", df), ("pre_2010", pre), ("post_2010", post)]:
            gross = window_df[factor].to_numpy()
            net = apply_cost_haircut(gross, factor_name=factor)

            gross_result = premium_ttest(gross)
            net_result = premium_ttest(net)

            rows.append(
                {
                    "factor": factor,
                    "window": window_name,
                    "n_months": gross_result["n_obs"],
                    "gross_annualized_premium": gross_result["annualized_premium"],
                    "gross_t_stat": gross_result["t_stat"],
                    "gross_clears_hlz_bar": gross_result["clears_hlz_bar"],
                    "net_annualized_premium": net_result["annualized_premium"],
                    "net_t_stat": net_result["t_stat"],
                    "net_clears_hlz_bar": net_result["clears_hlz_bar"],
                }
            )
    return pd.DataFrame(rows)


if __name__ == "__main__":
    factors_df = load_all_factors()
    results = run_decay_analysis(factors_df)
    pd.set_option("display.width", 160)
    print(results.to_string(index=False))

    print("\n--- H1 check: did the gross premium shrink post-2010 vs pre-2010? ---")
    pivot = results.pivot(index="factor", columns="window", values="gross_annualized_premium")
    pivot["H1_confirmed"] = pivot["post_2010"] < pivot["pre_2010"]
    print(pivot)

    print("\n--- H2 check: does any factor drop below the HLZ bar after costs, post-2010? ---")
    post_only = results[results["window"] == "post_2010"][["factor", "net_t_stat", "net_clears_hlz_bar"]]
    print(post_only)
