from __future__ import annotations

from datetime import datetime, timedelta, timezone

from tools.hsra.breakout_strategy import (
    TrendBreakoutStrategyEngine,
    evaluate_price_channel_breakout_signal,
)
from tools.hsra.ohlcv import OHLCVCandle


def _bar(start: datetime, *, o: float, h: float, l: float, c: float) -> OHLCVCandle:
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


def _series(start: datetime, closes: list[float], highs: list[float] | None = None, lows: list[float] | None = None) -> list[OHLCVCandle]:
    candles: list[OHLCVCandle] = []
    highs = highs or closes
    lows = lows or closes
    for idx, close in enumerate(closes):
        bar_start = start + timedelta(minutes=5 * idx)
        candles.append(
            _bar(
                bar_start,
                o=close * 0.99,
                h=highs[idx],
                l=lows[idx],
                c=close,
            )
        )
    return candles


def test_breakout_signal_eligible_when_close_exceeds_prior_channel_high():
    start = datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)
    candles = _series(
        start,
        closes=[100.0, 99.0, 98.0, 97.0, 99.0, 96.0, 102.0, 101.0, 100.0, 99.0, 98.0, 97.0],
        highs=[100.0, 100.0, 99.0, 98.0, 99.0, 98.0, 103.0, 102.0, 101.0, 100.0, 99.0, 98.0],
        lows=[95.0, 94.0, 93.0, 92.0, 94.0, 92.0, 96.0, 95.0, 94.0, 93.0, 92.0, 90.0],
    )

    result = evaluate_price_channel_breakout_signal(candles, channel_lookback=6, trend_filter="none", hold_period=3)

    assert result["eligible"] is True
    assert result["signal_index"] == 6
    assert result["entry_reference_index"] == 7
    assert result["exit_reference_index"] == 9
    assert result["reason"] == "candidate_signal"


def test_trend_filter_variants_all_pass_and_reject_correctly():
    start = datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)
    closes = [100.0] * 30 + [104.0, 104.1, 104.3, 104.4, 104.5, 104.6, 104.7, 104.8, 104.9, 104.9, 104.8, 104.7, 104.6, 104.5, 104.6, 104.7, 104.8, 104.9, 104.9, 104.8, 105.1]
    highs = [101.0] * len(closes)
    highs[-1] = 106.0
    lows = [95.0] * len(closes)
    candles = _series(start, closes=closes, highs=highs, lows=lows)

    no_filter = evaluate_price_channel_breakout_signal(candles, channel_lookback=6, trend_filter="none", hold_period=3)
    sma20 = evaluate_price_channel_breakout_signal(candles, channel_lookback=6, trend_filter="close_above_sma20", hold_period=3)
    sma_combo = evaluate_price_channel_breakout_signal(candles, channel_lookback=6, trend_filter="close_above_sma20_and_sma20_gt_sma50", hold_period=3)

    assert no_filter["eligible"] is True
    assert sma20["eligible"] is True
    assert sma_combo["eligible"] is False
    assert sma_combo["reason"] in {"insufficient_history", "trend_filter_failed"}

    weak_closes = [101.8] * 20 + [101.5, 101.6, 101.3, 101.0, 101.4, 101.5]
    weak_highs = [101.9] * 20 + [101.7, 101.8, 101.5, 101.2, 101.6, 101.7]
    weak_lows = [100.8] * len(weak_closes)
    weak = _series(start, closes=weak_closes, highs=weak_highs, lows=weak_lows)
    weak_result = evaluate_price_channel_breakout_signal(weak, channel_lookback=6, trend_filter="close_above_sma20", hold_period=3)
    assert weak_result["eligible"] is False
    assert weak_result["reason"] in {"no_signal", "trend_filter_failed"}


def test_rejects_invalid_configuration_and_incomplete_history():
    start = datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)
    candles = _series(start, closes=[100.0] * 10)

    invalid_lookback = evaluate_price_channel_breakout_signal(candles, channel_lookback=5, trend_filter="none", hold_period=3)
    invalid_filter = evaluate_price_channel_breakout_signal(candles, channel_lookback=6, trend_filter="bad_filter", hold_period=3)
    invalid_hold = evaluate_price_channel_breakout_signal(candles, channel_lookback=6, trend_filter="none", hold_period=2)
    insufficient = evaluate_price_channel_breakout_signal(candles, channel_lookback=48, trend_filter="none", hold_period=3)

    assert invalid_lookback["eligible"] is False
    assert invalid_lookback["reason"] == "invalid_parameters"
    assert invalid_filter["eligible"] is False
    assert invalid_filter["reason"] == "invalid_parameters"
    assert invalid_hold["eligible"] is False
    assert invalid_hold["reason"] == "invalid_parameters"
    assert insufficient["eligible"] is False
    assert insufficient["reason"] == "insufficient_history"


def test_rejects_gap_broken_and_lookahead_incomplete_context():
    start = datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)
    gap_candles = [
        _bar(start, o=100.0, h=101.0, l=95.0, c=100.0),
        _bar(start + timedelta(minutes=5), o=101.0, h=102.0, l=96.0, c=101.0),
        _bar(start + timedelta(minutes=10), o=99.0, h=100.0, l=95.0, c=99.0),
        _bar(start + timedelta(minutes=15), o=98.0, h=99.0, l=94.0, c=98.0),
        _bar(start + timedelta(minutes=30), o=105.0, h=108.0, l=100.0, c=105.0),
    ]

    gap_result = evaluate_price_channel_breakout_signal(gap_candles, channel_lookback=6, trend_filter="none", hold_period=3)
    assert gap_result["eligible"] is False
    assert gap_result["reason"] == "gap_in_history"

    current_candles = _series(
        start,
        closes=[100.0, 99.0, 98.0, 97.0, 99.0, 96.0, 102.0, 101.0, 100.0, 99.0, 98.0, 97.0],
        highs=[100.0, 100.0, 99.0, 98.0, 99.0, 98.0, 103.0, 102.0, 101.0, 100.0, 99.0, 98.0],
        lows=[95.0, 94.0, 93.0, 92.0, 94.0, 92.0, 96.0, 95.0, 94.0, 93.0, 92.0, 90.0],
    )
    current_bar = evaluate_price_channel_breakout_signal(current_candles, channel_lookback=6, trend_filter="none", hold_period=3, current_bar_start=start + timedelta(minutes=30))
    assert current_bar["eligible"] is False
    assert current_bar["reason"] == "incomplete_current_bar"


def test_engine_uses_completed_bar_only_and_generates_detector_metadata():
    start = datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)
    candles = _series(
        start,
        closes=[100.0, 99.0, 98.0, 97.0, 99.0, 96.0, 102.0, 101.0, 100.0, 99.0, 98.0, 97.0],
        highs=[100.0, 100.0, 99.0, 98.0, 99.0, 98.0, 103.0, 102.0, 101.0, 100.0, 99.0, 98.0],
        lows=[95.0, 94.0, 93.0, 92.0, 94.0, 92.0, 96.0, 95.0, 94.0, 93.0, 92.0, 90.0],
    )

    engine = TrendBreakoutStrategyEngine(symbol="BTC-EUR", channel_lookback=6, trend_filter="none", hold_period=3)
    decision = engine.evaluate(candles)

    assert decision["eligible"] is True
    assert decision["symbol"] == "BTC-EUR"
    assert decision["signal_timestamp"] == datetime(2020, 1, 1, 0, 35, tzinfo=timezone.utc)
    assert decision["reason"] == "candidate_signal"
