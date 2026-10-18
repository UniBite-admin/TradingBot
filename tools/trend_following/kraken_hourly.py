from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path


HOUR = timedelta(hours=1)
DAY = timedelta(days=1)


class TrendDataError(ValueError):
    """Raised when Kraken OHLCV rows violate the trend-research data contract."""


@dataclass(frozen=True)
class TrendCandle:
    interval_start: datetime
    interval_end: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    trade_count: int


def _reject(reason: str, *, source_path: str, line_number: int | None = None, **details: object) -> TrendDataError:
    context = {"reason": reason, "source_path": source_path}
    if line_number is not None:
        context["line_number"] = line_number
    context.update(details)
    return TrendDataError("; ".join(f"{key}={value}" for key, value in context.items()))


def load_kraken_hourly(path: str | Path) -> list[TrendCandle]:
    """Read the repository's headerless 7-column Kraken hourly OHLCV format.

    Expected columns: Unix interval-start timestamp, open, high, low, close,
    base-asset volume, trade count. Missing hours are preserved as gaps; this
    function never sorts, fills, deduplicates, or synthesizes candles.
    """
    file_path = Path(path)
    source_path = str(file_path)
    if not file_path.is_file():
        raise _reject("missing_required_source_file", source_path=source_path)

    candles: list[TrendCandle] = []
    previous_start: datetime | None = None
    with file_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        for line_number, row in enumerate(reader, start=1):
            if not row or not any(cell.strip() for cell in row):
                continue
            if row[0].strip().startswith("#"):
                continue
            if len(row) != 7:
                raise _reject(
                    "invalid_column_count",
                    source_path=source_path,
                    line_number=line_number,
                    actual_columns=len(row),
                    expected_columns=7,
                )

            try:
                timestamp = int(row[0].strip())
                open_price, high_price, low_price, close_price, volume = (
                    float(row[index].strip()) for index in range(1, 6)
                )
                trade_count = int(row[6].strip())
            except (TypeError, ValueError):
                raise _reject(
                    "invalid_numeric_values",
                    source_path=source_path,
                    line_number=line_number,
                ) from None

            numeric_values = (open_price, high_price, low_price, close_price, volume)
            if any(not math.isfinite(value) for value in numeric_values):
                raise _reject(
                    "non_finite_numeric_values",
                    source_path=source_path,
                    line_number=line_number,
                )
            if timestamp % 3600 != 0:
                raise _reject(
                    "timestamp_not_utc_hour_aligned",
                    source_path=source_path,
                    line_number=line_number,
                    timestamp=timestamp,
                )
            if min(open_price, high_price, low_price, close_price) <= 0:
                raise _reject(
                    "non_positive_price",
                    source_path=source_path,
                    line_number=line_number,
                )
            if not (
                low_price <= open_price <= high_price
                and low_price <= close_price <= high_price
            ):
                raise _reject(
                    "invalid_ohlc_relationship",
                    source_path=source_path,
                    line_number=line_number,
                )
            if volume < 0:
                raise _reject(
                    "negative_volume",
                    source_path=source_path,
                    line_number=line_number,
                    volume=volume,
                )
            if trade_count < 0:
                raise _reject(
                    "negative_trade_count",
                    source_path=source_path,
                    line_number=line_number,
                    trade_count=trade_count,
                )

            interval_start = datetime.fromtimestamp(timestamp, tz=timezone.utc)
            if previous_start is not None and interval_start <= previous_start:
                reason = (
                    "duplicate_timestamp"
                    if interval_start == previous_start
                    else "timestamps_not_strictly_increasing"
                )
                raise _reject(
                    reason,
                    source_path=source_path,
                    line_number=line_number,
                    timestamp=interval_start.isoformat(),
                    previous_timestamp=previous_start.isoformat(),
                )

            candles.append(
                TrendCandle(
                    interval_start=interval_start,
                    interval_end=interval_start + HOUR,
                    open=open_price,
                    high=high_price,
                    low=low_price,
                    close=close_price,
                    volume=volume,
                    trade_count=trade_count,
                )
            )
            previous_start = interval_start

    if not candles:
        raise _reject("no_kraken_rows", source_path=source_path)
    return candles


def split_contiguous_hourly_segments(
    candles: list[TrendCandle],
) -> list[list[TrendCandle]]:
    """Split already-validated chronological candles at every missing hour."""
    segments: list[list[TrendCandle]] = []
    current: list[TrendCandle] = []
    for candle in candles:
        if not current:
            current = [candle]
        elif candle.interval_start == current[-1].interval_start + HOUR:
            current.append(candle)
        else:
            segments.append(current)
            current = [candle]
    if current:
        segments.append(current)
    return segments


def build_complete_utc_daily_candles(
    candles: list[TrendCandle],
) -> list[TrendCandle]:
    """Aggregate only complete UTC days containing all 24 hourly intervals.

    Incomplete days are omitted rather than repaired. Callers must split the
    resulting daily series at missing-day boundaries before carrying state.
    """
    if not candles:
        return []

    days: dict[datetime, list[TrendCandle]] = {}
    for candle in candles:
        day_start = candle.interval_start.replace(hour=0, minute=0, second=0, microsecond=0)
        days.setdefault(day_start, []).append(candle)

    daily: list[TrendCandle] = []
    for day_start in sorted(days):
        hours = sorted(days[day_start], key=lambda candle: candle.interval_start)
        expected_starts = [day_start + HOUR * index for index in range(24)]
        if len(hours) != 24 or [c.interval_start for c in hours] != expected_starts:
            continue
        daily.append(
            TrendCandle(
                interval_start=day_start,
                interval_end=day_start + DAY,
                open=hours[0].open,
                high=max(c.high for c in hours),
                low=min(c.low for c in hours),
                close=hours[-1].close,
                volume=sum(c.volume for c in hours),
                trade_count=sum(c.trade_count for c in hours),
            )
        )
    return daily


def split_contiguous_daily_segments(
    candles: list[TrendCandle],
) -> list[list[TrendCandle]]:
    """Split daily candles at missing UTC days so strategy state cannot bridge gaps."""
    segments: list[list[TrendCandle]] = []
    current: list[TrendCandle] = []
    for candle in candles:
        if not current:
            current = [candle]
        elif candle.interval_start == current[-1].interval_start + DAY:
            current.append(candle)
        else:
            segments.append(current)
            current = [candle]
    if current:
        segments.append(current)
    return segments
