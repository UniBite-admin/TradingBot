from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import timezone
from pathlib import Path

from .box_theory import BoxTheoryConfig, default_cost_scenarios, run_box_theory_segmented
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
    parser.add_argument("--taker-fee-rate", type=float, default=0.0025, help="Illustrative fee rate per side; unverified")
    parser.add_argument("--spread-bps", type=float, default=4.0, help="Illustrative spread cost per side")
    parser.add_argument("--slippage-bps", type=float, default=2.0, help="Illustrative slippage cost per side")
    args = parser.parse_args(argv)

    for name, value in (("notional-eur", args.notional_eur), ("zone-fraction", args.zone_fraction),
                        ("stop-buffer-bps", args.stop_buffer_bps), ("taker-fee-rate", args.taker_fee_rate),
                        ("spread-bps", args.spread_bps), ("slippage-bps", args.slippage_bps)):
        if not math.isfinite(value) or value < 0:
            parser.error(f"--{name} must be finite and non-negative")
    if args.notional_eur <= 0 or not 0 < args.zone_fraction < 0.5:
        parser.error("--notional-eur must be positive and --zone-fraction must be between 0 and 0.5")

    source = Path(args.input).resolve()
    output = Path(args.output).resolve()
    if source == output:
        parser.error("output path must not overwrite the input source")
    if not source.is_file():
        parser.error(f"input file does not exist: {source}")

    source_sha256 = _sha256(source)
    candles = load_kraken_ohlcv(source)
    if not candles:
        parser.error("input contains no valid candles")
    scenarios = default_cost_scenarios(
        taker_fee_rate=args.taker_fee_rate, spread_bps=args.spread_bps, slippage_bps=args.slippage_bps
    )
    config = BoxTheoryConfig(
        symbol="BTC-EUR",
        interval_minutes=5,
        zone_fraction=args.zone_fraction,
        stop_buffer_bps=args.stop_buffer_bps,
        notional_eur=args.notional_eur,
    )
    # Parameters are fixed before this chronological evaluation. Trades and strategy
    # state are not allowed to cross the partition boundaries.
    train_end = int(len(candles) * 0.60)
    validation_end = int(len(candles) * 0.80)
    partitions = {
        "training": candles[:train_end],
        "validation": candles[train_end:validation_end],
        "final_test": candles[validation_end:],
    }
    partition_reports = {}
    for name, partition_candles in partitions.items():
        partition_reports[name] = {
            "start_utc": partition_candles[0].interval_start.astimezone(timezone.utc).isoformat() if partition_candles else None,
            "end_utc": partition_candles[-1].interval_end.astimezone(timezone.utc).isoformat() if partition_candles else None,
            "candle_count": len(partition_candles),
            "result": run_box_theory_segmented(partition_candles, config=config, cost_scenarios=scenarios),
        }

    result = {
        "strategy": "box_theory",
        "report_status": "RESEARCH_ONLY_NOT_VALIDATED",
        "config": {
            "symbol": config.symbol,
            "interval_minutes": config.interval_minutes,
            "zone_fraction": config.zone_fraction,
            "stop_buffer_bps": config.stop_buffer_bps,
            "notional_eur": config.notional_eur,
        },
        "research_protocol": {
            "chronological_split": "60% training / 20% validation / 20% final test by sorted candle index",
            "parameters_fixed_before_evaluation": True,
            "trades_or_state_cross_partition_boundaries": False,
            "final_test_used_for_parameter_selection": False,
            "note": "Each partition is processed independently; complete prior-day boxes must be available inside a contiguous segment in that partition.",
        },
        "partition_reports": partition_reports,
        "full_sample_descriptive_result": run_box_theory_segmented(candles, config=config, cost_scenarios=scenarios),
        "cost_policy": {
            "gross_pnl_reported_separately": True,
            "illustrative_scenario_is_verified_venue_data": False,
            "latency_cost_eur": None,
            "latency_status": "not_priced",
            "scenarios": [scenario.__dict__ for scenario in scenarios],
        },
        "interpretation": "historical research only; no profitability or execution-readiness claim",
        "known_limitations": [
            "Illustrative fee, spread, and slippage values are assumptions, not verified Kraken or Bitvavo execution costs.",
            "The next-candle-open entry is a bar-level simulation, not evidence of an executable fill.",
            "Latency is not converted to EUR because no validated model is available.",
            "A full previous UTC day must exist inside one contiguous segment; data gaps can exclude candidate days.",
        ],
    }
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
        "partition_summaries": {
            name: report["result"]["summary"]
            for name, report in partition_reports.items()
        },
        "full_sample_descriptive_summary": result["full_sample_descriptive_result"]["summary"],
        "interpretation": result["interpretation"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
