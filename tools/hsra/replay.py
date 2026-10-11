from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable, Sequence

from .ohlcv import OHLCVCandle


class ReplayError(ValueError):
    """Raised when replay chronology or completeness guards fail."""


@dataclass(frozen=True)
class ReplayStep:
    decision_time: datetime
    available_candles: list[OHLCVCandle]
    completed_candles: list[OHLCVCandle]
    current_bar: OHLCVCandle | None = None


def _order_candles(candles: Iterable[OHLCVCandle]) -> list[OHLCVCandle]:
    ordered = sorted(candles, key=lambda candle: candle.interval_start)
    seen: set[datetime] = set()
    for candle in ordered:
        if candle.interval_start in seen:
            raise ReplayError(f"duplicate_interval_start:{candle.interval_start.isoformat()}")
        seen.add(candle.interval_start)
    for previous, current in zip(ordered, ordered[1:]):
        expected = previous.interval_start + timedelta(minutes=5)
        if current.interval_start != expected:
            raise ReplayError(
                f"missing_interval: expected {expected.isoformat()} after {previous.interval_start.isoformat()}, "
                f"got {current.interval_start.isoformat()}"
            )
    return ordered


def replay_candles(
    candles: Sequence[OHLCVCandle],
    *,
    current_bar_start: datetime | None = None,
) -> list[ReplayStep]:
    """Return a deterministic replay sequence for a consecutive set of completed candles.

    A decision is emitted only when the replay has enough completed history to evaluate the
    current interval without using a still-forming bar. If a current bar is supplied, it is
    explicitly excluded from the evaluable set and represented by a boundary step instead.
    """
    ordered = _order_candles(candles)
    if not ordered:
        return []

    if current_bar_start is None:
        current_bar_start = ordered[-1].interval_start

    steps: list[ReplayStep] = []
    completed_candles: list[OHLCVCandle] = []

    for candle in ordered:
        if candle.interval_start >= current_bar_start:
            if candle.interval_start == current_bar_start:
                steps.append(
                    ReplayStep(
                        decision_time=current_bar_start,
                        available_candles=list(completed_candles),
                        completed_candles=list(completed_candles),
                        current_bar=None,
                    )
                )
            break

        completed_candles.append(candle)
        if len(completed_candles) > 1:
            steps.append(
                ReplayStep(
                    decision_time=candle.interval_start,
                    available_candles=list(completed_candles),
                    completed_candles=list(completed_candles),
                    current_bar=candle,
                )
            )

    return steps
