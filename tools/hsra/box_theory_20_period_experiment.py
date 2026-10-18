from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    from .box_theory import BoxTheoryConfig, run_box_theory_cash_account_period
    from .kraken_ohlcv import load_kraken_ohlcv
except ImportError:  # pragma: no cover - allows direct script execution
    from tools.hsra.box_theory import BoxTheoryConfig, run_box_theory_cash_account_period
    from tools.hsra.kraken_ohlcv import load_kraken_ohlcv


DEFAULT_SOURCE_PATH = Path("data/kraken/XBTEUR_5.csv")
DEFAULT_MANIFEST_PATH = Path("reports/kraken_breakout_zero_cost_20periods_2026-10-15_manifest.json")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def load_period_manifest(path: str | Path | None = None) -> dict:
    manifest_path = Path(path) if path is not None else DEFAULT_MANIFEST_PATH
    if not manifest_path.is_file():
        raise FileNotFoundError(f"period manifest not found: {manifest_path}")
    with manifest_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _summarize(period_records: list[dict]) -> dict:
    closed = sum(item["summary"]["closed_trades"] for item in period_records)
    eligible = sum(item["summary"]["eligible_signals"] for item in period_records)
    rejected = sum(item["summary"]["rejected_signals"] for item in period_records)
    unresolved = sum(item["summary"]["unresolved_positions"] for item in period_records)
    gross_profit = sum(item["summary"]["realized_gross_profit_eur"] for item in period_records)
    gross_loss = sum(item["summary"]["realized_gross_loss_eur"] for item in period_records)
    net = sum(item["summary"]["net_realized_pnl_eur"] for item in period_records)
    ending_cash = sum(item["summary"]["ending_cash_eur"] for item in period_records)
    ending_equity = sum(item["summary"]["ending_equity_eur"] for item in period_records)
    return {
        "period_count": len(period_records),
        "eligible_signals": eligible,
        "rejected_signals": rejected,
        "closed_trades": closed,
        "unresolved_positions": unresolved,
        "realized_gross_profit_eur": gross_profit,
        "realized_gross_loss_eur": gross_loss,
        "net_realized_pnl_eur": net,
        "ending_cash_eur": ending_cash,
        "ending_equity_eur": ending_equity,
        "transaction_costs_zeroed": True,
        "initial_cash_eur": 100.0 * len(period_records),
    }


def _build_period_record(candles: list, period_entry: dict) -> dict:
    period_start = _parse_utc(period_entry["start"])
    period_end = _parse_utc(period_entry["end"])
    context_start = period_start - timedelta(days=1)
    context_candles = [
        candle for candle in candles
        if context_start <= candle.interval_start.astimezone(timezone.utc) <= period_end
    ]
    result = run_box_theory_cash_account_period(
        context_candles,
        period_start=period_start,
        period_end=period_end,
        config=BoxTheoryConfig(symbol="BTC-EUR", interval_minutes=5, zone_fraction=0.25, stop_buffer_bps=5.0, notional_eur=100.0),
    )

    trade_records = []
    for trade in result["trades"]:
        trade_records.append({
            "entry_timestamp_utc": trade["entry_timestamp_utc"],
            "exit_timestamp_utc": trade["exit_timestamp_utc"],
            "entry_price": trade["entry_price"],
            "exit_price": trade["exit_price"],
            "quantity": trade["quantity"],
            "exit_reason": trade["exit_reason"],
            "gross_pnl_eur": trade["gross_pnl_eur"],
            "entry_notional_eur": trade["entry_notional_eur"],
            "exit_notional_eur": trade["exit_notional_eur"],
            "transaction_costs_zeroed": True,
        })

    open_position = None
    if result["open_position"] is not None:
        open_position = {
            "quantity": result["open_position"]["quantity"],
            "entry_price": result["open_position"]["entry_price"],
            "mark_to_market_value_eur": result["open_position"]["mark_to_market_value_eur"],
            "unrealized_pnl_eur": result["open_position"]["unrealized_pnl_eur"],
            "entry_notional_eur": result["open_position"]["entry_notional_eur"],
            "status": result["open_position"]["status"],
        }

    period_summary = {
        "initial_cash_eur": 100.0,
        "eligible_signals": result["summary"]["eligible_signals"],
        "rejected_signals": result["summary"]["rejected_signals"],
        "closed_trades": result["summary"]["closed_trades"],
        "winning_trades": result["summary"]["winning_trades"],
        "losing_trades": result["summary"]["losing_trades"],
        "unresolved_positions": result["summary"]["unresolved_positions"],
        "realized_gross_profit_eur": result["summary"]["realized_gross_profit_eur"],
        "realized_gross_loss_eur": result["summary"]["realized_gross_loss_eur"],
        "net_realized_pnl_eur": result["summary"]["net_realized_pnl_eur"],
        "ending_cash_eur": result["summary"]["ending_cash_eur"],
        "ending_equity_eur": result["summary"]["ending_equity_eur"],
        "realized_return_pct": result["summary"]["realized_return_pct"],
        "equity_return_pct": result["summary"]["equity_return_pct"],
        "transaction_costs_zeroed": True,
    }
    return {
        "period_id": period_entry["period_id"],
        "category": period_entry["type"],
        "period_start_utc": period_start.isoformat(),
        "period_end_utc": period_end.isoformat(),
        "initial_cash_eur": 100.0,
        "eligible_signals": result["summary"]["eligible_signals"],
        "rejected_signals": result["summary"]["rejected_signals"],
        "closed_trades": result["summary"]["closed_trades"],
        "winning_trades": result["summary"]["winning_trades"],
        "losing_trades": result["summary"]["losing_trades"],
        "unresolved_positions": result["summary"]["unresolved_positions"],
        "trades": trade_records,
        "total_realized_gross_profit_eur": result["summary"]["realized_gross_profit_eur"],
        "total_realized_gross_loss_eur": result["summary"]["realized_gross_loss_eur"],
        "net_realized_pnl_eur": result["summary"]["net_realized_pnl_eur"],
        "ending_cash_eur": result["summary"]["ending_cash_eur"],
        "open_position": open_position,
        "ending_equity_eur": result["summary"]["ending_equity_eur"],
        "realized_return_pct": result["summary"]["realized_return_pct"],
        "equity_return_pct": result["summary"]["equity_return_pct"],
        "transaction_costs_zeroed": True,
        "summary": period_summary,
        "accounting": {
            "cash_eur": result["cash_eur"],
            "ending_cash_eur": result["summary"]["ending_cash_eur"],
            "ending_equity_eur": result["summary"]["ending_equity_eur"],
            "open_position_mark_to_market_value_eur": open_position["mark_to_market_value_eur"] if open_position else 0.0,
            "equity_formula": "ending_cash_eur + open_position.mark_to_market_value_eur",
        },
    }


def run_box_theory_20_period_experiment(
    *,
    source_path: str | Path = DEFAULT_SOURCE_PATH,
    manifest_path: str | Path = DEFAULT_MANIFEST_PATH,
    output_path: str | Path | None = None,
) -> dict:
    source = Path(source_path)
    manifest = load_period_manifest(manifest_path)
    candles = load_kraken_ohlcv(source)
    weekly_records = []
    monthly_records = []
    all_records = []

    for period_type in ("weekly", "monthly"):
        for period_entry in manifest["period_ranges"][period_type]:
            record = _build_period_record(candles, period_entry)
            record["period_type"] = period_type
            if period_type == "weekly":
                weekly_records.append(record)
            else:
                monthly_records.append(record)
            all_records.append(record)

    report = {
        "experiment_name": "box_theory_20_periods_research_only",
        "strategy": "box_theory",
        "source_file": str(source),
        "source_sha256": _sha256(source),
        "source_bytes": source.stat().st_size,
        "manifest_path": str(Path(manifest_path)),
        "manifest_status": "RESEARCH_ONLY_PERIOD_BOUNDARIES_REUSED_FROM_LEGACY_MANIFEST",
        "notes": {
            "conflict": "The historical 20-period manifest belongs to the legacy breakout study, so only its UTC period boundaries are reused; the Box Theory signal, entry, stop, target, and exit rules remain unchanged.",
            "strategy_rules_preserved": True,
            "transaction_costs_zeroed": True,
            "live_trading_not_authorized": True,
        },
        "period_count": 20,
        "weekly_runs": len(weekly_records),
        "monthly_runs": len(monthly_records),
        "periods": all_records,
        "weekly_summary": _summarize(weekly_records),
        "monthly_summary": _summarize(monthly_records),
        "combined_summary": _summarize(all_records),
    }

    if output_path is not None:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the dedicated Box Theory 20-period backtest using the archived period boundaries.")
    parser.add_argument("--source", default=str(DEFAULT_SOURCE_PATH), help="Kraken BTC/EUR 5-minute OHLCV CSV")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST_PATH), help="20-period UTC manifest to reuse for exact period boundaries")
    parser.add_argument("--output", default="reports/box_theory_20_periods_2026-10-16.json", help="Path for the new Box Theory report")
    args = parser.parse_args(argv)

    report = run_box_theory_20_period_experiment(
        source_path=args.source,
        manifest_path=args.manifest,
        output_path=args.output,
    )
    print(json.dumps({
        "status": "completed",
        "period_count": report["period_count"],
        "weekly_runs": report["weekly_runs"],
        "monthly_runs": report["monthly_runs"],
        "source_sha256": report["source_sha256"],
        "output": args.output,
        "combined_summary": report["combined_summary"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
