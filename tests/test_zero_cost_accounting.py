from datetime import datetime, timedelta, timezone

import pytest

from tools.hsra.zero_cost_experiment import (
    ZeroCostPeriodAccount,
    _assert_accounting_invariants,
    run_zero_cost_period,
)
from tools.hsra.ohlcv import OHLCVCandle


def _bar(ts: datetime, *, o: float, h: float, l: float, c: float) -> OHLCVCandle:
    return OHLCVCandle(
        interval_start=ts,
        interval_end=ts + timedelta(minutes=5),
        open=o,
        high=h,
        low=l,
        close=c,
        volume=1.0,
        trade_count=1,
    )


def test_zero_cost_run_keeps_cash_and_equity_in_balance():
    base = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
    candles = []
    for i in range(18):
        start = base + timedelta(minutes=5 * i)
        candles.append(_bar(start, o=100.0, h=101.0, l=99.0, c=100.0))
    candles[3] = _bar(base + timedelta(minutes=15), o=100.0, h=102.0, l=88.0, c=96.0)
    candles[4] = _bar(base + timedelta(minutes=20), o=99.0, h=110.0, l=94.0, c=109.0)
    candles[5] = _bar(base + timedelta(minutes=25), o=101.0, h=102.0, l=97.0, c=101.0)
    candles[6] = _bar(base + timedelta(minutes=30), o=100.0, h=101.0, l=95.0, c=100.0)

    result = run_zero_cost_period(candles, period_id="synthetic-1")
    account = ZeroCostPeriodAccount.from_result(result)

    assert result["initial_cash_eur"] == 100.0
    assert account.positions_open <= 1
    assert abs(account.total_equity_eur - account.cash_eur - account.position_value_eur) < 1e-9
    assert result["realized_pnl_eur"] == result["realized_gross_pnl_eur"]
    assert result["costs_total_eur"] == 0.0


def test_zero_cost_selection_seed_is_reproducible():
    from tools.hsra.zero_cost_experiment import sample_periods

    a = sample_periods(seed=7, period_days=7, count=3)
    b = sample_periods(seed=7, period_days=7, count=3)
    assert a == b


def test_zero_cost_sampled_periods_have_exact_requested_duration():
    from tools.hsra.zero_cost_experiment import sample_periods

    periods = sample_periods(seed=7, period_days=7, count=3)
    assert len(periods) == 3
    for period in periods:
        assert period["end"] - period["start"] == timedelta(days=7)
        assert len(period["candles"]) == 2016
        assert period["end"] == period["candles"][-1].interval_end
        assert period["start"] == period["candles"][0].interval_start


def test_zero_cost_accounting_invariants_reject_bad_trade_counts():
    base = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
    candles = []
    for i in range(30):
        start = base + timedelta(minutes=5 * i)
        candles.append(_bar(start, o=100.0, h=101.0, l=99.0, c=100.0))

    result = run_zero_cost_period(candles, period_id="synthetic-2")
    result["trades_count"] = 3
    result["winning_trades"] = 1
    result["losing_trades"] = 1
    result["break_even_trades"] = 0

    with pytest.raises(AssertionError):
        _assert_accounting_invariants(result)
