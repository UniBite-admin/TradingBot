from __future__ import annotations

import hashlib
from datetime import datetime

from .ohlcv import OHLCVCandle


class StrategyEngine:
    """Deterministic wrapper around the approved local-structure rule set."""

    def __init__(self, *, symbol: str = "BTC-EUR", lookback: int = 3):
        self.symbol = symbol
        self.lookback = lookback

    def evaluate(self, candles: list[OHLCVCandle], *, current_bar_start: datetime | None = None) -> dict:
        result = evaluate_local_structure_signal(
            candles,
            lookback=self.lookback,
            current_bar_start=current_bar_start,
        )
        if not result["eligible"]:
            return {
                "eligible": False,
                "reason": result["reason"],
                "signal_timestamp": None,
                "decision_id": None,
                "symbol": self.symbol,
            }

        decision_payload = (
            f"{self.symbol}|{self.lookback}|{result['setup_index']}|{result['confirmation_index']}|"
            f"{result['signal_timestamp'].isoformat()}"
        )
        decision_id = hashlib.sha256(decision_payload.encode("utf-8")).hexdigest()[:16]
        return {
            "eligible": True,
            "setup_index": result["setup_index"],
            "confirmation_index": result["confirmation_index"],
            "signal_timestamp": result["signal_timestamp"],
            "reason": result["reason"],
            "decision_id": decision_id,
            "symbol": self.symbol,
        }


def evaluate_local_structure_signal(
    candles: list[OHLCVCandle],
    *,
    lookback: int = 3,
    current_bar_start: datetime | None = None,
) -> dict:
    """Evaluate the approved local-structure signal rules on completed candles.

    The function is intentionally conservative: it only emits an eligible signal when the
    required completed context and confirmation candle are available, and it rejects any
    evaluation that depends on a still-forming current bar.
    """
    ordered = sorted(candles, key=lambda candle: candle.interval_start)

    if lookback < 1:
        return {"eligible": False, "reason": "invalid_lookback"}

    if current_bar_start is not None:
        if current_bar_start >= ordered[-1].interval_start:
            return {"eligible": False, "reason": "incomplete_current_bar"}
        for candle in ordered:
            if candle.interval_start == current_bar_start:
                return {"eligible": False, "reason": "incomplete_current_bar"}

    if len(ordered) < lookback + 2:
        return {"eligible": False, "reason": "missing_context"}

    for setup_index in range(lookback, len(ordered) - 1):
        setup = ordered[setup_index]
        confirmation = ordered[setup_index + 1]

        if current_bar_start is not None and confirmation.interval_start >= current_bar_start:
            return {"eligible": False, "reason": "incomplete_current_bar"}

        context = ordered[setup_index - lookback:setup_index]
        if len(context) < lookback:
            return {"eligible": False, "reason": "missing_context"}

        prior_low = min(candle.low for candle in context)
        lower_wick = min(setup.open, setup.close) - setup.low
        body = abs(setup.close - setup.open)
        candle_range = setup.high - setup.low
        prev_close_low = context[-1].low

        if not (setup.low < prior_low):
            continue
        if not (setup.close > prev_close_low):
            continue
        if not (lower_wick > body):
            continue
        if not (candle_range > 0):
            continue
        if not (confirmation.close > setup.high):
            continue

        return {
            "eligible": True,
            "setup_index": setup_index,
            "confirmation_index": setup_index + 1,
            "signal_timestamp": confirmation.interval_end,
            "reason": "candidate_signal",
        }

    return {"eligible": False, "reason": "no_signal"}
