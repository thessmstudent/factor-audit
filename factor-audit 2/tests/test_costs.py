import numpy as np
import pytest

from factor_audit.factors.costs import DEFAULT_MONTHLY_TURNOVER, apply_cost_haircut


def test_haircut_reduces_returns_by_expected_drag():
    returns = np.full(12, 0.02)
    net = apply_cost_haircut(returns, factor_name="HML", round_trip_cost_bps=15.0)
    expected_drag = (15.0 / 10_000.0) * DEFAULT_MONTHLY_TURNOVER["HML"]
    assert np.allclose(net, 0.02 - expected_drag)


def test_momentum_haircut_bigger_than_value_due_to_turnover():
    returns = np.full(12, 0.02)
    net_umd = apply_cost_haircut(returns, factor_name="UMD")
    net_hml = apply_cost_haircut(returns, factor_name="HML")
    # Momentum's assumed turnover is much higher, so its cost drag should be larger,
    # i.e. its net return should be lower for the same gross return.
    assert net_umd[0] < net_hml[0]


def test_unknown_factor_without_explicit_turnover_raises():
    with pytest.raises(ValueError):
        apply_cost_haircut(np.array([0.01]), factor_name="NOT_A_FACTOR")


def test_explicit_turnover_overrides_default():
    returns = np.full(6, 0.03)
    net = apply_cost_haircut(returns, factor_name="HML", round_trip_cost_bps=20.0, monthly_turnover=0.5)
    expected_drag = (20.0 / 10_000.0) * 0.5
    assert np.allclose(net, 0.03 - expected_drag)
