from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from tools.hsra.box_theory import run_box_theory_cash_account_period
from tools.hsra.box_theory_20_period_experiment import load_period_manifest
from tools.hsra.ohlcv import OHLCVCandle


def _candle(start: datetime, *, open_: float = 100.0, high: float = 101.0, low: float = 99.0, close: float = 100.0) -> OHLCVCandle:
    return OHLCVCandle(
        interval_start=start,
        interval_end=start + timedelta(minutes=5),
        open=open_,
        high=high,
        low=low,
        close=close,
        volume=1.0,
        trade_count=1,
    )


def _full_box_day(day_start: datetime, *, box_low: float = 90.0, box_high: float = 110.0) -> list[OHLCVCandle]:
    candles: list[OHLCVCandle] = []
    for index in range(288):
        ts = day_start + timedelta(minutes=5 * index)
        candles.append(_candle(ts, open_=100.0, high=101.0, low=99.0, close=100.0))
    candles[0] = _candle(day_start, open_=100.0, high=box_high, low=box_low, close=100.0)
    candles[1] = _candle(day_start + timedelta(minutes=5), open_=100.0, high=box_high, low=99.0, close=100.0)
    return candles


def _multi_signal_dataset() -> list[OHLCVCandle]:
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    candles: list[OHLCVCandle] = []
    candles.extend(_full_box_day(start))
    candles.extend(_full_box_day(start + timedelta(days=1)))
    candles.extend(_full_box_day(start + timedelta(days=2)))

    signal_day = start + timedelta(days=1)
    candles[288 + 0] = _candle(signal_day, open_=97.0, high=98.0, low=95.0, close=97.2)
    candles[288 + 1] = _candle(signal_day + timedelta(minutes=5), open_=97.0, high=98.0, low=96.0, close=97.2)
    candles[288 + 2] = _candle(signal_day + timedelta(minutes=10), open_=100.0, high=100.0, low=100.0, close=100.0)

    next_signal_day = start + timedelta(days=2)
    candles[576 + 0] = _candle(next_signal_day, open_=97.0, high=98.0, low=95.0, close=97.2)
    candles[576 + 1] = _candle(next_signal_day + timedelta(minutes=5), open_=97.0, high=98.0, low=96.0, close=97.2)
    candles[576 + 2] = _candle(next_signal_day + timedelta(minutes=10), open_=100.0, high=100.0, low=100.0, close=100.0)
    return candles


def test_manifest_has_exactly_10_weekly_and_10_monthly_ranges():
    manifest = load_period_manifest()
    weekly = manifest["period_ranges"]["weekly"]
    monthly = manifest["period_ranges"]["monthly"]

    assert len(weekly) == 10
    assert len(monthly) == 10
    assert {entry["type"] for entry in weekly} == {"weekly"}
    assert {entry["type"] for entry in monthly} == {"monthly"}
    assert manifest["weekly_runs"] == 10
    assert manifest["monthly_runs"] == 10


def test_full_cash_position_sizing_and_reinvestment_after_closed_trades():
    candles = _multi_signal_dataset()
    result = run_box_theory_cash_account_period(
        candles,
        period_start=datetime(2024, 1, 1, tzinfo=timezone.utc),
        period_end=datetime(2024, 1, 3, 23, 55, tzinfo=timezone.utc),
    )

    assert result["summary"]["initial_cash_eur"] == pytest.approx(100.0)
    assert result["summary"]["transaction_costs_zeroed"] is True
    assert result["summary"]["ending_cash_eur"] >= 0.0
    assert result["summary"]["closed_trades"] == 2
    assert result["trades"][0]["entry_notional_eur"] == pytest.approx(100.0)
    assert result["trades"][1]["entry_notional_eur"] == pytest.approx(result["trades"][0]["exit_notional_eur"])
    assert result["summary"]["rejected_signals"] >= 0
    if result["summary"]["open_position"] is not None:
        assert result["summary"]["ending_equity_eur"] == pytest.approx(
            result["summary"]["ending_cash_eur"] + result["summary"]["open_position"]["mark_to_market_value_eur"]
        )
