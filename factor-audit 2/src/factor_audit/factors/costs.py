"""
Explicit transaction-cost haircut model, cited rather than hand-waved.

The academic factor return series (Ken French's included) are gross of trading costs
by construction — they assume frictionless rebalancing. This module answers: what does
the premium look like once you charge a plausible round-trip cost against the portfolio's
estimated turnover?
"""

from __future__ import annotations

import numpy as np

# Default assumed monthly one-way turnover per factor, as a fraction of the portfolio,
# based on typical published turnover estimates for long-short academic factor
# portfolios (value and size turn over more slowly than momentum). These are
# starting assumptions, not measured directly from this project's own data --
# state that plainly in the write-up, and revisit if better estimates are found.
DEFAULT_MONTHLY_TURNOVER = {
    "Mkt-RF": 0.02,
    "SMB": 0.05,
    "HML": 0.05,
    "RMW": 0.05,
    "CMA": 0.05,
    "UMD": 0.35,  # momentum turns over much faster than the others
}


def apply_cost_haircut(
    monthly_returns: np.ndarray,
    factor_name: str,
    round_trip_cost_bps: float = 15.0,
    monthly_turnover: float | None = None,
) -> np.ndarray:
    """Subtracts an estimated monthly cost drag from a factor's return series.

    cost_drag_per_month = round_trip_cost_bps/10000 * monthly_turnover

    `round_trip_cost_bps` defaults to 15bps, the middle of the commonly cited 10-20bps
    range for reasonably liquid US large/mid-cap equities. Cite the specific source
    used in the write-up rather than treating 15bps as self-evidently correct.
    """
    if monthly_turnover is None:
        monthly_turnover = DEFAULT_MONTHLY_TURNOVER.get(factor_name)
        if monthly_turnover is None:
            raise ValueError(
                f"No default turnover for '{factor_name}'; pass monthly_turnover explicitly."
            )
    cost_drag = (round_trip_cost_bps / 10_000.0) * monthly_turnover
    monthly_returns = np.asarray(monthly_returns, dtype=float)
    return monthly_returns - cost_drag
