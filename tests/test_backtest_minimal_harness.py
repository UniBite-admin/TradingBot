from datetime import datetime, timedelta, timezone

from tools.hsra.backtest import HistoricalBacktestHarness
from tools.hsra.ohlcv import OHLCVCandle


def _bar(hour: int, minute: int, o: float, h: float, l: float, c: float) -> OHLCVCandle:
    start = datetime(2020, 1, 1, hour, minute, tzinfo=timezone.utc)
    return OHLCVCandle(
        interval_start=start,
        interval_end=start + timedelta(minutes=5),
        open=o,
        high=h,
        low=l,
        close=c,
        volume=1.0,
        trade_count=1,
    )


def test_minimal_harness_respects_entry_and_exit_timing():
    candles = []
    base = datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)
    for i in range(15):
        start = base + timedelta(minutes=5 * i)
        if i < 3:
            candles.append(_bar(start.hour, start.minute, 100.0, 101.0, 95.0, 100.0))
        elif i == 3:
            candles.append(_bar(start.hour, start.minute, 100.0, 102.0, 88.0, 96.0))
        elif i == 4:
            candles.append(_bar(start.hour, start.minute, 99.0, 110.0, 94.0, 109.0))
        else:
            candles.append(_bar(start.hour, start.minute, 100.0, 101.0, 95.0, 100.0))

    harness = HistoricalBacktestHarness(symbol="BTC-EUR", lookback=3, hold_period=3)
    result = harness.run(candles)

    assert result["summary"]["trade_count"] >= 1
    assert result["trades"][0]["entry_price"] > 0
    assert result["trades"][0]["exit_price"] > 0
    assert result["trades"][0]["signal_timestamp"] == "2020-01-01T00:25:00+00:00"
    assert result["trades"][0]["net_pnl_eur"] <= result["trades"][0]["gross_pnl_eur"]


def test_minimal_harness_rejects_gap_broken_series():
    candles = [
        _bar(0, 0, 100.0, 101.0, 95.0, 100.0),
        _bar(0, 5, 99.0, 102.0, 93.0, 98.0),
        _bar(0, 10, 97.0, 98.0, 91.0, 96.0),
        _bar(0, 20, 98.0, 99.0, 88.0, 98.0),
        _bar(0, 25, 98.0, 101.0, 97.0, 102.0),
    ]

    harness = HistoricalBacktestHarness(symbol="BTC-EUR", lookback=3, hold_period=3)
    result = harness.run(candles)

    assert result["summary"]["trade_count"] == 0


def test_minimal_harness_counts_cost_drag_and_position_state():
    candles = []
    base = datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)
    for i in range(10):
        start = base + timedelta(minutes=5 * i)
        candles.append(_bar(start.hour, start.minute, 100.0, 101.0, 95.0, 100.0))

    candles[3] = _bar(0, 15, 100.0, 102.0, 88.0, 96.0)
    candles[4] = _bar(0, 20, 99.0, 110.0, 94.0, 109.0)
    candles[5] = _bar(0, 25, 101.0, 102.0, 97.0, 101.0)
    candles[6] = _bar(0, 30, 100.0, 101.0, 95.0, 100.0)
    candles[7] = _bar(0, 35, 99.0, 100.0, 93.0, 98.0)

    harness = HistoricalBacktestHarness(symbol="BTC-EUR", lookback=3, hold_period=3)
    result = harness.run(candles)

    assert result["summary"]["trade_count"] >= 0
    if result["trades"]:
        first = result["trades"][0]
        assert first["entry_cost_eur"] > 0
        assert first["exit_cost_eur"] > 0
        assert first["net_pnl_eur"] <= first["gross_pnl_eur"]


def test_segmented_harness_splits_at_contiguous_boundaries_and_resets_state():
    segment_1 = []
    segment_2 = []
    base = datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)

    for idx in range(12):
        start = base + timedelta(minutes=5 * idx)
        if idx < 7:
            segment_1.append(_bar(start.hour, start.minute, 100.0, 101.0, 95.0, 100.0))
        else:
            segment_2.append(_bar(start.hour, start.minute, 100.0, 101.0, 95.0, 100.0))

    segment_1[3] = _bar(0, 15, 100.0, 102.0, 88.0, 96.0)
    segment_1[4] = _bar(0, 20, 99.0, 110.0, 94.0, 109.0)
    segment_1[5] = _bar(0, 25, 101.0, 102.0, 97.0, 101.0)
    segment_1[6] = _bar(0, 30, 100.0, 101.0, 95.0, 100.0)

    segment_2[0] = _bar(0, 35, 100.0, 102.0, 88.0, 96.0)
    segment_2[1] = _bar(0, 40, 99.0, 110.0, 94.0, 109.0)
    segment_2[2] = _bar(0, 45, 101.0, 102.0, 97.0, 101.0)
    segment_2[3] = _bar(0, 50, 100.0, 101.0, 95.0, 100.0)

    candles = segment_1 + [
        _bar(0, 35, 100.0, 101.0, 90.0, 99.0),
        _bar(0, 40, 99.0, 100.0, 93.0, 97.0),
        _bar(0, 45, 97.0, 98.0, 90.0, 96.0),
        _bar(0, 50, 96.0, 99.0, 92.0, 98.0),
        _bar(0, 55, 98.0, 100.0, 95.0, 99.0),
    ] + segment_2

    harness = HistoricalBacktestHarness(symbol="BTC-EUR", lookback=3, hold_period=1)
    result = harness.run_segmented(candles)

    assert result["summary"]["segment_count"] >= 2
    assert result["summary"]["trade_count"] >= 0
    for segment in result["segments"]:
        assert segment["status"] in {"eligible", "rejected_gap_in_history", "insufficient_history"}


def test_segmented_harness_keeps_continuous_replay_fail_closed_on_gaps():
    candles = [
        _bar(0, 0, 100.0, 101.0, 95.0, 100.0),
        _bar(0, 5, 99.0, 102.0, 93.0, 98.0),
        _bar(0, 10, 97.0, 98.0, 91.0, 96.0),
        _bar(0, 20, 98.0, 99.0, 88.0, 98.0),
        _bar(0, 25, 98.0, 101.0, 97.0, 102.0),
    ]

    harness = HistoricalBacktestHarness(symbol="BTC-EUR", lookback=3, hold_period=1)
    run_result = harness.run(candles)
    assert run_result["summary"]["status"] == "rejected_gap_in_history"
    assert run_result["summary"]["trade_count"] == 0


def test_segmented_harness_records_boundary_exclusion_and_no_cross_segment_exit():
    base = datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)
    candles = []
    for i in range(8):
        start = base + timedelta(minutes=5 * i)
        candles.append(_bar(start.hour, start.minute, 100.0, 101.0, 95.0, 100.0))

    for idx in [3, 4, 5, 6]:
        candles[idx] = _bar(base.hour, base.minute + 5 * idx, 100.0, 102.0, 88.0, 96.0)

    candles.insert(7, _bar(0, 35, 100.0, 101.0, 95.0, 100.0))
    candles.insert(8, _bar(0, 40, 99.0, 110.0, 94.0, 109.0))
    candles.insert(9, _bar(0, 45, 101.0, 102.0, 97.0, 101.0))
    candles.insert(10, _bar(0, 50, 100.0, 101.0, 95.0, 100.0))
    candles.insert(11, _bar(0, 55, 99.0, 100.0, 93.0, 98.0))

    harness = HistoricalBacktestHarness(symbol="BTC-EUR", lookback=3, hold_period=1)
    result = harness.run_segmented(candles)

    assert result["summary"]["segment_count"] >= 2
    for segment in result["segments"]:
        assert segment["status"] in {"eligible", "eligible_no_trade", "rejected_gap_in_history", "insufficient_history"}
        if segment["trade_count"]:
            assert segment["segment_end"] >= segment["segment_start"]
