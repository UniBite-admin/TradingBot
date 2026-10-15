from __future__ import annotations

import argparse
import hashlib
import json
from datetime import timezone
from pathlib import Path

from .box_theory import BoxTheoryConfig, run_box_theory_segmented
from .kraken_ohlcv import load_kraken_ohlcv


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the research-only Box Theory backtest on Kraken 5m OHLCV.")
    parser.add_argument("--input", required=True, help="Path to the validated Kraken OHLCV CSV, e.g. data/kraken/XBTEUR_5.csv")
    parser.add_argument("--output", required=True, help="JSON report path; must not overwrite the source file")
    parser.add_argument("--notional-eur", type=float, default=50.0)
    parser.add_argument("--zone-fraction", type=float, default=0.25)
    parser.add_argument("--stop-buffer-bps", type=float, default=5.0)
    args = parser.parse_args(argv)

    source = Path(args.input).resolve()
    output = Path(args.output).resolve()
    if source == output:
        parser.error("output path must not overwrite the input source")
    if not source.is_file():
        parser.error(f"input file does not exist: {source}")

    source_sha256 = _sha256(source)
    candles = load_kraken_ohlcv(source)
    config = BoxTheoryConfig(
        symbol="BTC-EUR",
        interval_minutes=5,
        zone_fraction=args.zone_fraction,
        stop_buffer_bps=args.stop_buffer_bps,
        notional_eur=args.notional_eur,
    )
    result = run_box_theory_segmented(candles, config=config)
    result["provenance"] = {
        "source_type": "Kraken BTC/EUR 5-minute OHLCV",
        "source_path": str(source),
        "source_sha256": source_sha256,
        "source_bytes": source.stat().st_size,
        "candle_count": len(candles),
        "first_interval_start_utc": candles[0].interval_start.astimezone(timezone.utc).isoformat() if candles else None,
        "last_interval_start_utc": candles[-1].interval_start.astimezone(timezone.utc).isoformat() if candles else None,
        "execution_mode": "historical_research_only",
        "live_trading_authorized": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "completed",
        "output": str(output),
        "source_sha256": source_sha256,
        "summary": result["summary"],
        "interpretation": result["interpretation"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
