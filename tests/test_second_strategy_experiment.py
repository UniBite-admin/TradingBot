from datetime import datetime, timedelta, timezone

from tools.hsra.ohlcv import OHLCVCandle
from tools.hsra.second_strategy_experiment import (
    _signal_observations_for_window,
    evaluate_local_rejection_signal,
    run_second_strategy_experiment,
)


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


def test_local_rejection_signal_detects_valid_setup_and_confirmation():
    candles = []
    base = datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)
    for i in range(20):
        start = base + timedelta(minutes=5 * i)
        if i < 12:
            candles.append(_bar(start.hour, start.minute, 100.0, 101.0, 95.0, 100.0))
        elif i == 12:
            candles.append(_bar(start.hour, start.minute, 100.0, 102.0, 88.0, 96.0))
        elif i == 13:
            candles.append(_bar(start.hour, start.minute, 99.0, 110.0, 94.0, 109.0))
        else:
            candles.append(_bar(start.hour, start.minute, 100.0, 101.0, 95.0, 100.0))

    result = evaluate_local_rejection_signal(candles, lookback=12)
    assert result["eligible"] is True
    assert result["setup_index"] == 12
    assert result["confirmation_index"] == 13
    assert result["signal_timestamp"] == datetime(2020, 1, 1, 1, 10, tzinfo=timezone.utc)


def test_local_rejection_signal_rejects_lookup_on_incomplete_current_bar():
    candles = []
    base = datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)
    for i in range(15):
        start = base + timedelta(minutes=5 * i)
        candles.append(_bar(start.hour, start.minute, 100.0, 101.0, 95.0, 100.0))

    current_bar_start = candles[-1].interval_start
    result = evaluate_local_rejection_signal(candles, lookback=12, current_bar_start=current_bar_start)
    assert result["eligible"] is False
    assert result["reason"] == "incomplete_current_bar"


def test_local_rejection_signal_rejects_insufficient_lookback_context():
    candles = []
    base = datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)
    for i in range(13):
        start = base + timedelta(minutes=5 * i)
        candles.append(_bar(start.hour, start.minute, 100.0, 101.0, 95.0, 100.0))

    result = evaluate_local_rejection_signal(candles, lookback=12)
    assert result["eligible"] is False
    assert result["reason"] == "missing_context"


def test_local_rejection_signal_rejects_missing_forward_outcome():
    candles = []
    base = datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)
    for i in range(15):
        start = base + timedelta(minutes=5 * i)
        if i < 12:
            candles.append(_bar(start.hour, start.minute, 100.0, 101.0, 95.0, 100.0))
        elif i == 12:
            candles.append(_bar(start.hour, start.minute, 100.0, 102.0, 88.0, 96.0))
        elif i == 13:
            candles.append(_bar(start.hour, start.minute, 99.0, 110.0, 94.0, 109.0))
        else:
            candles.append(_bar(start.hour, start.minute, 100.0, 101.0, 95.0, 100.0))

    observations = _signal_observations_for_window(candles, lookback=12, hold_period=3)
    assert observations == []


def test_second_strategy_experiment_runs_on_manifest_and_is_reproducible(tmp_path):
    report = run_second_strategy_experiment(output_dir=tmp_path / "results")
    assert report["execution_status"] == "BLOCKED"
    assert report["lookback"] == 12
    assert report["forward_horizon_candles"] == 3
    assert report["entry_reference"] == "next_candle_open"
    assert report["signal_validity"] == "immediately_following_confirmation_candle"
    assert report["reason"].startswith("The approved bounded sample produced no eligible forward-return observations")

    second = run_second_strategy_experiment(output_dir=tmp_path / "results")
    assert second == report
