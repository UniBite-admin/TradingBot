from datetime import datetime, timezone

from tools.hsra.ohlcv import OHLCVCandle
from tools.hsra.replay import ReplayError, replay_candles


def _candle(start_hour: int, start_minute: int, open_: float, close_: float) -> OHLCVCandle:
    start = datetime(2020, 1, 1, start_hour, start_minute, tzinfo=timezone.utc)
    end = start.replace(minute=start.minute + 5) if start.minute < 55 else start.replace(hour=start.hour + 1, minute=0)
    return OHLCVCandle(
        interval_start=start,
        interval_end=end,
        open=open_,
        high=max(open_, close_),
        low=min(open_, close_),
        close=close_,
        volume=1.0,
        trade_count=1,
    )


def test_replay_candles_sorts_and_excludes_incomplete_current_bar():
    candles = [
        _candle(0, 10, 100.0, 101.0),
        _candle(0, 0, 99.0, 100.0),
        _candle(0, 5, 100.0, 100.5),
    ]

    replay = replay_candles(candles, current_bar_start=datetime(2020, 1, 1, 0, 10, tzinfo=timezone.utc))

    assert [step.decision_time for step in replay] == [
        datetime(2020, 1, 1, 0, 5, tzinfo=timezone.utc),
        datetime(2020, 1, 1, 0, 10, tzinfo=timezone.utc),
    ]
    assert replay[0].available_candles == [candles[1], candles[2]]
    assert replay[1].available_candles == [candles[1], candles[2]]
    assert replay[1].current_bar is None


def test_replay_rejects_non_chronological_gap():
    candles = [
        _candle(0, 0, 99.0, 100.0),
        _candle(0, 10, 101.0, 102.0),
    ]

    try:
        replay_candles(candles)
        raise AssertionError("expected ReplayError")
    except ReplayError as exc:
        assert "missing_interval" in str(exc)


def test_replay_is_deterministic_for_same_inputs():
    candles = [
        _candle(0, 0, 99.0, 100.0),
        _candle(0, 5, 100.0, 100.5),
    ]

    first = replay_candles(candles)
    second = replay_candles(list(reversed(candles)))

    assert [step.decision_time for step in first] == [step.decision_time for step in second]
    assert [step.available_candles for step in first] == [step.available_candles for step in second]
