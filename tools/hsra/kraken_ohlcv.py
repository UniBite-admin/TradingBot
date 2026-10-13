from __future__ import annotations

import csv
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .merger import HSRAError
from .ohlcv import OHLCVCandle


def _read_kraken_rows(path: str | Path) -> list[list[str]]:
    file_path = Path(path)
    if not file_path.exists() or not file_path.is_file():
        raise HSRAError(json.dumps({
            "status": "REJECTED",
            "reason": "missing_required_source_file",
            "source": "kraken_ohlcv",
            "source_path": str(file_path),
        }))

    rows: list[list[str]] = []
    with file_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        for line_number, row in enumerate(reader, start=1):
            if not row or not any(cell.strip() for cell in row):
                continue
            if row[0].startswith("#"):
                continue
            rows.append([cell.strip() for cell in row])
    if not rows:
        raise HSRAError(json.dumps({
            "status": "REJECTED",
            "reason": "no_kraken_rows",
            "source_path": str(file_path),
        }))
    return rows


def _parse_kraken_row(row: list[str], *, source_path: str, line_number: int) -> OHLCVCandle:
    if len(row) < 5:
        raise HSRAError(json.dumps({
            "status": "REJECTED",
            "reason": "invalid_kraken_row",
            "source_path": source_path,
            "line_number": line_number,
            "row": row,
        }))

    try:
        ts = int(float(row[0]))
        open_price = float(row[1])
        high_price = float(row[2])
        low_price = float(row[3])
        close_price = float(row[4])
        volume = float(row[6]) if len(row) > 6 else 0.0
    except (TypeError, ValueError):
        raise HSRAError(json.dumps({
            "status": "REJECTED",
            "reason": "invalid_kraken_numeric_values",
            "source_path": source_path,
            "line_number": line_number,
            "row": row,
        })) from None

    values = (ts, open_price, high_price, low_price, close_price, volume)
    if any(not math.isfinite(value) for value in values):
        raise HSRAError(json.dumps({
            "status": "REJECTED",
            "reason": "non_finite_kraken_values",
            "source_path": source_path,
            "line_number": line_number,
            "row": row,
        }))

    if ts % 300 != 0:
        raise HSRAError(json.dumps({
            "status": "REJECTED",
            "reason": "non_utc_5m_alignment",
            "source_path": source_path,
            "line_number": line_number,
            "timestamp": ts,
        }))

    if not (low_price <= open_price <= high_price and low_price <= close_price <= high_price):
        raise HSRAError(json.dumps({
            "status": "REJECTED",
            "reason": "invalid_ohlcv_relationship",
            "source_path": source_path,
            "line_number": line_number,
            "open": open_price,
            "high": high_price,
            "low": low_price,
            "close": close_price,
        }))

    interval_start = datetime.fromtimestamp(ts, tz=timezone.utc)
    return OHLCVCandle(
        interval_start=interval_start,
        interval_end=interval_start + timedelta(minutes=5),
        open=open_price,
        high=high_price,
        low=low_price,
        close=close_price,
        volume=volume,
        trade_count=0,
    )


def load_kraken_ohlcv(path: str | Path) -> list[OHLCVCandle]:
    rows = _read_kraken_rows(path)
    candles = [
        _parse_kraken_row(row, source_path=str(path), line_number=index)
        for index, row in enumerate(rows, start=1)
    ]
    ordered = sorted(candles, key=lambda candle: candle.interval_start)

    seen_timestamps: set[datetime] = set()
    for candle in ordered:
        if candle.interval_start in seen_timestamps:
            raise HSRAError(json.dumps({
                "status": "REJECTED",
                "reason": "duplicate_kraken_timestamp",
                "source_path": str(path),
                "timestamp": candle.interval_start.isoformat(),
            }))
        seen_timestamps.add(candle.interval_start)

    for previous, current in zip(ordered, ordered[1:]):
        if current.interval_start - previous.interval_start != timedelta(minutes=5):
            continue
    return ordered


def extract_contiguous_kraken_windows(candles: list[OHLCVCandle]) -> list[list[OHLCVCandle]]:
    ordered = sorted(candles, key=lambda candle: candle.interval_start)
    windows: list[list[OHLCVCandle]] = []
    current: list[OHLCVCandle] = []
    for candle in ordered:
        if not current:
            current = [candle]
            continue
        if candle.interval_start == current[-1].interval_start + timedelta(minutes=5):
            current.append(candle)
        else:
            if current:
                windows.append(current)
            current = [candle]
    if current:
        windows.append(current)
    return windows
