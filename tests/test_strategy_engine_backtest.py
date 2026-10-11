from datetime import datetime, timezone

from tools.hsra.ohlcv import OHLCVCandle
from tools.hsra.strategy import StrategyEngine
from tools.hsra.backtest import HistoricalBacktestHarness


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


def test_strategy_engine_evaluates_with_decision_metadata():
    candles = [
        _bar(0, 0, 100.0, 101.0, 95.0, 100.0),
        _bar(0, 5, 99.0, 102.0, 93.0, 98.0),
        _bar(0, 10, 97.0, 98.0, 91.0, 96.0),
        _bar(0, 15, 98.0, 99.0, 88.0, 98.0),
        _bar(0, 20, 98.0, 101.0, 97.0, 102.0),
    ]

    engine = StrategyEngine(symbol="BTC-EUR", lookback=3)
    first = engine.evaluate(candles)
    second = engine.evaluate(list(reversed(candles)))

    assert first["eligible"] is True
    assert first["decision_id"] == second["decision_id"]
    assert first["signal_timestamp"] == datetime(2020, 1, 1, 0, 25, tzinfo=timezone.utc)
    assert first["reason"] == "candidate_signal"


def test_backtest_harness_produces_deterministic_run_summary():
    candles = [
        _bar(0, 0, 100.0, 101.0, 95.0, 100.0),
        _bar(0, 5, 99.0, 102.0, 93.0, 98.0),
        _bar(0, 10, 97.0, 98.0, 91.0, 96.0),
        _bar(0, 15, 98.0, 99.0, 88.0, 98.0),
        _bar(0, 20, 98.0, 101.0, 97.0, 102.0),
    ]

    harness = HistoricalBacktestHarness(symbol="BTC-EUR", lookback=3)
    first = harness.run(candles)
    second = harness.run(list(reversed(candles)))

    assert first["summary"]["decision_count"] == 1
    assert first["summary"] == second["summary"]
    assert first["decisions"][0]["decision_id"] == second["decisions"][0]["decision_id"]
