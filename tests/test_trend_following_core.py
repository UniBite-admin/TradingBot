from __future__ import annotations

import math
import statistics

import pytest

from tools.trend_following.core import (
    LOOKBACKS,
    MIN_PRIOR_DAILY_BARS,
    SubmodelState,
    TrendStrategyInputError,
    annualized_volatility,
    evaluate_daily_close,
    target_exposure,
    update_submodel,
    volatility_rebalance_required,
)


def test_entry_requires_exact_close_equality_to_upper_channel():
    assert update_submodel([100, 101, 102, 103, 104], 5, SubmodelState()) == SubmodelState(
        long=True, stop=102.0
    )
    assert update_submodel([100, 101, 102, 103, 103.5], 5, SubmodelState()).long is False


def test_long_state_checks_old_stop_before_ratchet():
    state = SubmodelState(long=True, stop=95.0)
    # Midpoint would be higher, but close breaches the old stop and exits first.
    assert update_submodel([90, 100, 110, 120, 94], 5, state) == SubmodelState()


def test_trailing_stop_never_decreases():
    state = SubmodelState(long=True, stop=105.0)
    updated = update_submodel([90, 100, 110, 120, 121], 5, state)
    assert updated.long
    assert updated.stop == 105.0


def test_exit_when_close_is_at_or_below_old_stop():
    state = SubmodelState(long=True, stop=100.0)
    assert update_submodel([90, 95, 105, 110, 100], 5, state) == SubmodelState()


def test_invalid_long_state_stop_is_rejected():
    with pytest.raises(TrendStrategyInputError, match="requires_finite_stop"):
        update_submodel([100] * 5, 5, SubmodelState(long=True, stop=None))


def test_volatility_matches_sample_standard_deviation_ddof_one():
    closes = [100.0 * (1.001 ** index) for index in range(91)]
    returns = [closes[i] / closes[i - 1] - 1 for i in range(1, len(closes))]
    expected = statistics.stdev(returns) * math.sqrt(365)
    assert annualized_volatility(closes) == pytest.approx(expected)


def test_volatility_needs_91_closes_for_90_returns():
    assert annualized_volatility([100.0] * 90) is None
    assert annualized_volatility([100.0] * 91) == 0.0


def test_zero_or_invalid_volatility_targets_zero_exposure():
    states = [SubmodelState(long=True, stop=90.0) for _ in LOOKBACKS]
    assert target_exposure(states, 0.0) == 0.0
    assert target_exposure(states, None) == 0.0
    assert target_exposure(states, float("nan")) == 0.0


def test_target_exposure_is_mean_of_nine_capped_weights():
    states = [SubmodelState(long=True, stop=90.0)] + [SubmodelState() for _ in range(8)]
    assert target_exposure(states, 0.10) == pytest.approx(0.25 / 9)
    assert target_exposure(states, 0.10) <= 1.0
    assert target_exposure(states, 0.01) == pytest.approx(1.0 / 9)


def test_core_requires_450_prior_daily_bars():
    closes = [100.0 + (index % 7) for index in range(MIN_PRIOR_DAILY_BARS)]
    decision = evaluate_daily_close(closes)
    assert not decision.valid
    assert decision.reason == "insufficient_prior_daily_bars"
    assert decision.target_exposure == 0.0


def test_core_accepts_450_prior_bars_plus_current_bar():
    closes = [100.0 + (index % 7) for index in range(MIN_PRIOR_DAILY_BARS + 1)]
    decision = evaluate_daily_close(closes)
    assert decision.valid
    assert len(decision.states) == 9
    assert 0.0 <= decision.target_exposure <= 1.0


@pytest.mark.parametrize(
    ("target", "current", "expected"),
    [
        (1.20, 1.00, False),
        (1.200001, 1.00, True),
        (0.80, 1.00, False),
        (0.799999, 1.00, True),
        (0.50, 0.00, False),
    ],
)
def test_volatility_rebalance_threshold_is_strict_and_zero_safe(target, current, expected):
    assert volatility_rebalance_required(target, current) is expected


def test_negative_quantities_are_rejected_for_spot_only():
    with pytest.raises(TrendStrategyInputError, match="nonnegative"):
        volatility_rebalance_required(-0.1, 0.1)
