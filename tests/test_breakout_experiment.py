from __future__ import annotations

from datetime import datetime, timedelta, timezone

from tools.hsra.breakout_experiment import (
    BREAKOUT_PARAMETER_GRID,
    build_chronological_partitions,
    select_breakout_parameters,
)


def _bar(start: datetime, close: float) -> dict:
    return {
        "interval_start": start,
        "interval_end": start + timedelta(minutes=5),
        "open": close * 0.99,
        "high": close * 1.02,
        "low": close * 0.98,
        "close": close,
    }


def _series(start: datetime, count: int) -> list[dict]:
    candles = []
    for idx in range(count):
        candles.append(_bar(start + timedelta(minutes=5 * idx), float(100 + idx)))
    return candles


def test_build_chronological_partitions_uses_exact_60_20_20_split():
    start = datetime(2020, 1, 1, tzinfo=timezone.utc)
    candles = _series(start, 100)

    partitions = build_chronological_partitions(candles)

    assert [len(partitions["train"]), len(partitions["validation"]), len(partitions["test"])] == [60, 20, 20]
    assert partitions["train"][-1]["interval_end"] <= partitions["validation"][0]["interval_start"]
    assert partitions["validation"][-1]["interval_end"] <= partitions["test"][0]["interval_start"]


def test_select_breakout_parameters_uses_validation_return_and_tie_breaks():
    candles = _series(datetime(2020, 1, 1, tzinfo=timezone.utc), 250)
    records = {
        (6, "none", 3): 0.10,
        (12, "none", 3): 0.15,
        (12, "close_above_sma20", 3): 0.15,
        (48, "close_above_sma20_and_sma20_gt_sma50", 12): 0.18,
    }

    selected = select_breakout_parameters(records, grid=BREAKOUT_PARAMETER_GRID)

    assert selected == {"channel_lookback": 48, "trend_filter": "close_above_sma20_and_sma20_gt_sma50", "hold_period": 12}
    assert selected in [
        {"channel_lookback": 48, "trend_filter": "close_above_sma20_and_sma20_gt_sma50", "hold_period": 12},
        {"channel_lookback": 12, "trend_filter": "close_above_sma20", "hold_period": 3},
    ]
