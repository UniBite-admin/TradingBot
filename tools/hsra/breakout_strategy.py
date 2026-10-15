from __future__ import annotations

import hashlib
from datetime import datetime, timedelta

from .ohlcv import OHLCVCandle

ALLOWED_CHANNEL_LOOKBACKS = {6, 12, 24, 48}
ALLOWED_HOLD_PERIODS = {3, 6, 12}
ALLOWED_TREND_FILTERS = {
    "none",
    "close_above_sma20",
    "close_above_sma20_and_sma20_gt_sma50",
}


def _sorted_ordered_candles(candles: list[OHLCVCandle]) -> list[OHLCVCandle]:
    ordered = sorted(candles, key=lambda candle: candle.interval_start)
    for index in range(1, len(ordered)):
        previous = ordered[index - 1]
        current = ordered[index]
        if current.interval_start <= previous.interval_start:
            raise ValueError("duplicate_or_unsorted_candle_timestamps")
        if current.interval_start - previous.interval_start != timedelta(minutes=5):
            raise ValueError("gap_in_history")
    return ordered


def _check_current_bar_context(ordered: list[OHLCVCandle], *, current_bar_start: datetime | None) -> None:
    if current_bar_start is None:
        return
    current_start = current_bar_start
    if current_start >= ordered[-1].interval_start:
        raise ValueError("incomplete_current_bar")
    for candle in ordered:
        if candle.interval_start == current_start:
            raise ValueError("incomplete_current_bar")


def _sma(closes: list[float], *, period: int) -> float | None:
    if len(closes) < period:
        return None
    return sum(closes[-period:]) / period


def _validate_parameters(*, channel_lookback: int, trend_filter: str, hold_period: int) -> None:
    if channel_lookback not in ALLOWED_CHANNEL_LOOKBACKS:
        raise ValueError("invalid_parameters")
    if trend_filter not in ALLOWED_TREND_FILTERS:
        raise ValueError("invalid_parameters")
    if hold_period not in ALLOWED_HOLD_PERIODS:
        raise ValueError("invalid_parameters")


def _trend_filter_passes(*, signal_close: float, ordered: list[OHLCVCandle], signal_index: int, trend_filter: str) -> tuple[bool, str, dict]:
    if trend_filter == "none":
        return True, "candidate_signal", {}

    lookback_20 = ordered[max(0, signal_index - 20):signal_index]
    if len(lookback_20) < 20:
        return False, "insufficient_history", {"required_window": 20}

    sma_20 = sum(candle.close for candle in lookback_20) / len(lookback_20)
    if trend_filter == "close_above_sma20":
        if signal_close > sma_20:
            return True, "candidate_signal", {"sma20": sma_20}
        return False, "trend_filter_failed", {"sma20": sma_20}

    lookback_50 = ordered[max(0, signal_index - 50):signal_index]
    if len(lookback_50) < 50:
        return False, "insufficient_history", {"required_window": 50}

    sma_50 = sum(candle.close for candle in lookback_50) / len(lookback_50)
    if signal_close > sma_20 and sma_20 > sma_50:
        return True, "candidate_signal", {"sma20": sma_20, "sma50": sma_50}
    return False, "trend_filter_failed", {"sma20": sma_20, "sma50": sma_50}


def evaluate_price_channel_breakout_signal(
    candles: list[OHLCVCandle],
    *,
    channel_lookback: int = 6,
    trend_filter: str = "none",
    hold_period: int = 3,
    current_bar_start: datetime | None = None,
) -> dict:
    """Evaluate a completed-candle breakout against the prior channel high.

    This is a research-only signal generator. It never creates synthetic candles, allows
    no look-ahead, and rejects any signal whose required history or exit horizon is not
    fully present in the input window.
    """
    try:
        _validate_parameters(channel_lookback=channel_lookback, trend_filter=trend_filter, hold_period=hold_period)
        ordered = _sorted_ordered_candles(candles)
        _check_current_bar_context(ordered, current_bar_start=current_bar_start)
    except ValueError as exc:
        reason = str(exc)
        if reason == "invalid_parameters":
            return {"eligible": False, "reason": "invalid_parameters", "signal_index": None, "entry_reference_index": None, "exit_reference_index": None, "signal_timestamp": None}
        if reason == "gap_in_history":
            return {"eligible": False, "reason": "gap_in_history", "signal_index": None, "entry_reference_index": None, "exit_reference_index": None, "signal_timestamp": None}
        if reason == "duplicate_or_unsorted_candle_timestamps":
            return {"eligible": False, "reason": "duplicate_or_unsorted_candle_timestamps", "signal_index": None, "entry_reference_index": None, "exit_reference_index": None, "signal_timestamp": None}
        if reason == "incomplete_current_bar":
            return {"eligible": False, "reason": "incomplete_current_bar", "signal_index": None, "entry_reference_index": None, "exit_reference_index": None, "signal_timestamp": None}
        return {"eligible": False, "reason": "invalid_input", "signal_index": None, "entry_reference_index": None, "exit_reference_index": None, "signal_timestamp": None}

    if not ordered:
        return {"eligible": False, "reason": "insufficient_history", "signal_index": None, "entry_reference_index": None, "exit_reference_index": None, "signal_timestamp": None}

    minimum_required_history = max(channel_lookback, 20 if trend_filter in {"close_above_sma20", "close_above_sma20_and_sma20_gt_sma50"} else 0, 50 if trend_filter == "close_above_sma20_and_sma20_gt_sma50" else 0)
    if len(ordered) < minimum_required_history + 1:
        return {"eligible": False, "reason": "insufficient_history", "signal_index": None, "entry_reference_index": None, "exit_reference_index": None, "signal_timestamp": None}

    for signal_index in range(channel_lookback, len(ordered)):
        signal = ordered[signal_index]
        if current_bar_start is not None and signal.interval_start >= current_bar_start:
            return {"eligible": False, "reason": "incomplete_current_bar", "signal_index": None, "entry_reference_index": None, "exit_reference_index": None, "signal_timestamp": None}

        channel_history = ordered[signal_index - channel_lookback:signal_index]
        if len(channel_history) < channel_lookback:
            return {"eligible": False, "reason": "insufficient_history", "signal_index": None, "entry_reference_index": None, "exit_reference_index": None, "signal_timestamp": None}

        channel_high = max(candle.high for candle in channel_history)
        if signal.close <= channel_high:
            continue

        passed, reason, extras = _trend_filter_passes(
            signal_close=signal.close,
            ordered=ordered,
            signal_index=signal_index,
            trend_filter=trend_filter,
        )
        if not passed:
            return {
                "eligible": False,
                "reason": reason,
                "signal_index": signal_index,
                "entry_reference_index": None,
                "exit_reference_index": None,
                "signal_timestamp": signal.interval_end,
                **extras,
            }

        entry_reference_index = signal_index + 1
        exit_reference_index = entry_reference_index + hold_period - 1
        if entry_reference_index >= len(ordered):
            return {"eligible": False, "reason": "incomplete_entry_horizon", "signal_index": signal_index, "entry_reference_index": entry_reference_index, "exit_reference_index": None, "signal_timestamp": signal.interval_end}
        if exit_reference_index >= len(ordered):
            return {"eligible": False, "reason": "incomplete_exit_horizon", "signal_index": signal_index, "entry_reference_index": entry_reference_index, "exit_reference_index": exit_reference_index, "signal_timestamp": signal.interval_end}

        entry_price = ordered[entry_reference_index].open
        exit_price = ordered[exit_reference_index].close
        return {
            "eligible": True,
            "reason": "candidate_signal",
            "signal_index": signal_index,
            "signal_timestamp": signal.interval_end,
            "entry_reference_index": entry_reference_index,
            "exit_reference_index": exit_reference_index,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "channel_high": channel_high,
            "trend_filter": trend_filter,
            **extras,
        }

    return {"eligible": False, "reason": "no_signal", "signal_index": None, "entry_reference_index": None, "exit_reference_index": None, "signal_timestamp": None}


class TrendBreakoutStrategyEngine:
    """Deterministic wrapper around the research-only trend-filtered breakout strategy."""

    def __init__(self, *, symbol: str = "BTC-EUR", channel_lookback: int = 6, trend_filter: str = "none", hold_period: int = 3):
        self.symbol = symbol
        self.channel_lookback = channel_lookback
        self.trend_filter = trend_filter
        self.hold_period = hold_period

    def evaluate(self, candles: list[OHLCVCandle], *, current_bar_start: datetime | None = None) -> dict:
        result = evaluate_price_channel_breakout_signal(
            candles,
            channel_lookback=self.channel_lookback,
            trend_filter=self.trend_filter,
            hold_period=self.hold_period,
            current_bar_start=current_bar_start,
        )
        if not result["eligible"]:
            return {
                "eligible": False,
                "reason": result["reason"],
                "signal_timestamp": None,
                "signal_index": None,
                "entry_reference_index": None,
                "exit_reference_index": None,
                "decision_id": None,
                "symbol": self.symbol,
            }

        decision_payload = (
            f"{self.symbol}|{self.channel_lookback}|{self.trend_filter}|{self.hold_period}|"
            f"{result['signal_index']}|{result['entry_reference_index']}|{result['exit_reference_index']}|"
            f"{result['signal_timestamp'].isoformat()}"
        )
        decision_id = hashlib.sha256(decision_payload.encode("utf-8")).hexdigest()[:16]
        return {
            "eligible": True,
            "signal_index": result["signal_index"],
            "entry_reference_index": result["entry_reference_index"],
            "exit_reference_index": result["exit_reference_index"],
            "signal_timestamp": result["signal_timestamp"],
            "entry_price": result["entry_price"],
            "exit_price": result["exit_price"],
            "reason": result["reason"],
            "decision_id": decision_id,
            "symbol": self.symbol,
            "channel_lookback": self.channel_lookback,
            "trend_filter": self.trend_filter,
            "hold_period": self.hold_period,
        }
