from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class CandidateWindow:
    valid: bool
    reason: str | None = None
    start: datetime | None = None
    end: datetime | None = None


def _as_utc(ts: datetime) -> datetime:
    if ts.tzinfo is None:
        return ts.replace(tzinfo=timezone.utc)
    return ts.astimezone(timezone.utc)


def _read_timestamp_csv(path: str | Path, *, ts_field: str = "timestamp") -> list[datetime]:
    csv_path = Path(path)
    if not csv_path.exists():
        return []
    timestamps: list[datetime] = []
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            value = row.get(ts_field)
            if not value:
                continue
            try:
                text = value.strip()
                if text.endswith("Z"):
                    text = text[:-1] + "+00:00"
                timestamps.append(datetime.fromisoformat(text).astimezone(timezone.utc))
            except ValueError:
                continue
    return timestamps


def evaluate_candidate(quotes_path: str | Path, trades_path: str | Path, start: datetime, end: datetime) -> CandidateWindow:
    low = _as_utc(start)
    high = _as_utc(end)

    quotes = _read_timestamp_csv(quotes_path)
    trades = _read_timestamp_csv(trades_path)
    if not quotes or not trades:
        return CandidateWindow(valid=False, reason="missing_quotes_or_trades", start=low, end=high)

    window_quotes = [ts for ts in quotes if low <= ts <= high]
    window_trades = [ts for ts in trades if low <= ts <= high]
    if not window_trades:
        return CandidateWindow(valid=False, reason="no_trades_in_window", start=low, end=high)

    first_trade = min(window_trades)
    if any(ts < first_trade for ts in window_quotes):
        return CandidateWindow(valid=False, reason="pre_first_trade_quotes_present", start=low, end=high)

    post_trade_quotes = [ts for ts in window_quotes if ts >= first_trade]
    if not post_trade_quotes:
        return CandidateWindow(valid=False, reason="no_post_trade_quotes", start=low, end=high)

    return CandidateWindow(valid=True, reason=None, start=first_trade, end=max(post_trade_quotes))


def find_largest_valid_window(quotes_path: str | Path, trades_path: str | Path) -> CandidateWindow | None:
    quotes = _read_timestamp_csv(quotes_path)
    trades = _read_timestamp_csv(trades_path)
    if not quotes or not trades:
        return None

    best: CandidateWindow | None = None
    for trade_ts in sorted(trades):
        post_trade_quotes = [ts for ts in quotes if ts >= trade_ts]
        if not post_trade_quotes:
            continue
        candidate = CandidateWindow(valid=True, reason="valid", start=trade_ts, end=max(post_trade_quotes))
        if best is None or (candidate.end - candidate.start) > (best.end - best.start):
            best = candidate

    return best
