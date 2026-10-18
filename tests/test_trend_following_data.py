from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from tools.trend_following.kraken_hourly import (
    TrendDataError,
    build_complete_utc_daily_candles,
    load_kraken_hourly,
    split_contiguous_daily_segments,
    split_contiguous_hourly_segments,
)


def _epoch(dt: datetime) -> int:
    return int(dt.timestamp())


def _row(timestamp: int, *, open_price: float = 100.0, high: float = 102.0,
         low: float = 99.0, close: float = 101.0, volume: float = 1.25,
         trade_count: int = 7) -> str:
    return f"{timestamp},{open_price},{high},{low},{close},{volume},{trade_count}"


def _write(path: Path, rows: list[str]) -> None:
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def test_hourly_reader_uses_volume_column_not_trade_count(tmp_path):
    path = tmp_path / "XBTEUR_60.csv"
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    _write(path, [
        _row(_epoch(start), volume=12.5, trade_count=47),
        _row(_epoch(start + timedelta(hours=1)), volume=3.25, trade_count=9),
    ])

    candles = load_kraken_hourly(path)

    assert candles[0].interval_start == start
    assert candles[0].interval_end == start + timedelta(hours=1)
    assert candles[0].volume == 12.5
    assert candles[0].trade_count == 47
    assert candles[1].volume == 3.25
    assert candles[1].trade_count == 9


def test_hourly_reader_preserves_gaps_and_segments_them(tmp_path):
    path = tmp_path / "XBTEUR_60.csv"
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    _write(path, [
        _row(_epoch(start)),
        _row(_epoch(start + timedelta(hours=1))),
        _row(_epoch(start + timedelta(hours=3))),
    ])

    candles = load_kraken_hourly(path)

    assert len(candles) == 3
    assert [len(segment) for segment in split_contiguous_hourly_segments(candles)] == [2, 1]


@pytest.mark.parametrize(
    ("rows", "reason"),
    [
        ([_row(1704067200), _row(1704067200)], "duplicate_timestamp"),
        ([_row(1704070800), _row(1704067200)], "timestamps_not_strictly_increasing"),
        (["1704067201,100,102,99,101,1.0,2"], "timestamp_not_utc_hour_aligned"),
        (["1704067200,100,99,101,101,1.0,2"], "invalid_ohlc_relationship"),
        (["1704067200,100,102,99,101,-1.0,2"], "negative_volume"),
        (["1704067200,100,102,99,101,1.0"], "invalid_column_count"),
    ],
)
def test_hourly_reader_rejects_invalid_rows(tmp_path, rows, reason):
    path = tmp_path / "XBTEUR_60.csv"
    _write(path, rows)

    with pytest.raises(TrendDataError, match=reason):
        load_kraken_hourly(path)


def test_daily_aggregation_uses_only_complete_utc_days(tmp_path):
    path = tmp_path / "XBTEUR_60.csv"
    first_day = datetime(2024, 1, 1, tzinfo=timezone.utc)
    rows = []
    for hour in range(24):
        rows.append(_row(
            _epoch(first_day + timedelta(hours=hour)),
            open_price=100 + hour,
            high=200 + hour,
            low=50 + hour,
            close=150 + hour,
            volume=hour + 0.5,
            trade_count=hour + 1,
        ))
    # The second day is deliberately missing one hour and must not be synthesized.
    for hour in range(24):
        if hour == 7:
            continue
        rows.append(_row(
            _epoch(first_day + timedelta(days=1, hours=hour)),
            open_price=200 + hour,
            high=300 + hour,
            low=150 + hour,
            close=250 + hour,
            volume=2.0,
            trade_count=2,
        ))
    _write(path, rows)

    hourly = load_kraken_hourly(path)
    daily = build_complete_utc_daily_candles(hourly)

    assert len(daily) == 1
    candle = daily[0]
    assert candle.interval_start == first_day
    assert candle.interval_end == first_day + timedelta(days=1)
    assert candle.open == 100
    assert candle.high == 223
    assert candle.low == 50
    assert candle.close == 173
    assert candle.volume == sum(hour + 0.5 for hour in range(24))
    assert candle.trade_count == sum(range(1, 25))


def test_daily_segments_do_not_bridge_missing_days():
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    daily = [
        # Only the fields used by the segmentation function are relevant here.
        type("Candle", (), {"interval_start": start})(),
        type("Candle", (), {"interval_start": start + timedelta(days=1)})(),
        type("Candle", (), {"interval_start": start + timedelta(days=3)})(),
    ]

    assert [len(segment) for segment in split_contiguous_daily_segments(daily)] == [2, 1]
