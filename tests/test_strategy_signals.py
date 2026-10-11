from datetime import datetime, timezone

from tools.hsra.ohlcv import OHLCVCandle
from tools.hsra.strategy import evaluate_local_structure_signal


def _bar(hour: int, minute: int, o: float, h: float, l: float, c: float) -> OHLCVCandle:
    start = datetime(2020, 1, 1, hour, minute, tzinfo=timezone.utc)
    return OHLCVCandle(
        interval_start=start,
        interval_end=start.replace(minute=(minute + 5) % 60),
        open=o,
        high=h,
        low=l,
        close=c,
        volume=1.0,
        trade_count=1,
    )


def test_evaluates_local_structure_signal_when_all_rules_hold():
    candles = [
        _bar(0, 0, 100.0, 101.0, 95.0, 100.0),
        _bar(0, 5, 99.0, 102.0, 93.0, 98.0),
        _bar(0, 10, 97.0, 98.0, 91.0, 96.0),
        _bar(0, 15, 98.0, 99.0, 88.0, 98.0),
        _bar(0, 20, 98.0, 101.0, 97.0, 102.0),
    ]

    result = evaluate_local_structure_signal(candles, lookback=3)

    assert result["eligible"] is True
    assert result["setup_index"] == 3
    assert result["confirmation_index"] == 4
    assert result["signal_timestamp"] == datetime(2020, 1, 1, 0, 25, tzinfo=timezone.utc)


def test_rejects_when_context_is_missing_or_current_bar_is_incomplete():
    candles = [
        _bar(0, 0, 100.0, 101.0, 98.0, 100.0),
        _bar(0, 5, 101.0, 102.0, 97.0, 99.0),
        _bar(0, 10, 99.0, 100.0, 92.0, 93.0),
    ]

    result = evaluate_local_structure_signal(candles, lookback=3)
    assert result["eligible"] is False
    assert result["reason"] == "missing_context"

    result2 = evaluate_local_structure_signal(candles, lookback=3, current_bar_start=datetime(2020, 1, 1, 0, 15, tzinfo=timezone.utc))
    assert result2["eligible"] is False
    assert result2["reason"] == "incomplete_current_bar"


def test_is_deterministic_for_identical_inputs():
    candles = [
        _bar(0, 0, 100.0, 101.0, 95.0, 100.0),
        _bar(0, 5, 99.0, 102.0, 93.0, 98.0),
        _bar(0, 10, 97.0, 98.0, 91.0, 96.0),
        _bar(0, 15, 98.0, 99.0, 88.0, 98.0),
        _bar(0, 20, 98.0, 101.0, 97.0, 102.0),
    ]

    first = evaluate_local_structure_signal(candles, lookback=3)
    second = evaluate_local_structure_signal(list(reversed(candles)), lookback=3)

    assert first["eligible"] == second["eligible"]
    assert first["setup_index"] == second["setup_index"]
    assert first["confirmation_index"] == second["confirmation_index"]
