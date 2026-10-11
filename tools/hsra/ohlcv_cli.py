from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from .emitter import write_metadata, write_ohlcv_jsonl
from .merger import HSRAError
from .ohlcv import build_ohlcv_window


def _parse_iso(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(timezone.utc)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build OHLCV candles from raw trade events.")
    parser.add_argument("--trades", required=True, help="Path to raw trade CSV file")
    parser.add_argument("--start", required=True, help="Start timestamp in ISO-8601 format")
    parser.add_argument("--end", required=True, help="End timestamp in ISO-8601 format")
    parser.add_argument("--outdir", required=True, help="Directory to write candle JSONL and metadata")
    parser.add_argument("--interval-minutes", type=int, default=5, help="Bucket size in minutes")
    args = parser.parse_args(argv)

    trades = Path(args.trades)
    start = _parse_iso(args.start)
    end = _parse_iso(args.end)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    try:
        candles = build_ohlcv_window(
            trades,
            requested_start=start,
            requested_end=end,
            interval_minutes=args.interval_minutes,
        )
    except HSRAError as exc:
        try:
            metadata = json.loads(str(exc))
        except Exception:
            metadata = {"status": "REJECTED", "reason": str(exc)}
        write_metadata(metadata, outdir / "metadata.json")
        print(f"HSRA: OHLCV build blocked; metadata written to {outdir / 'metadata.json'}")
        return 2

    write_ohlcv_jsonl(candles, outdir / "ohlcv.jsonl")
    metadata = {
        "status": "OK",
        "interval_minutes": args.interval_minutes,
        "requested_start": start.isoformat(),
        "requested_end": end.isoformat(),
        "candle_count": len(candles),
    }
    write_metadata(metadata, outdir / "metadata.json")
    print(f"HSRA: OHLCV build succeeded; candles written to {outdir / 'ohlcv.jsonl'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
