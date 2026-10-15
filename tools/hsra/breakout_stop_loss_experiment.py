from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .breakout_zero_cost_experiment import (
    BREAKOUT_ZERO_COST_CONFIG,
    _candidate_signals_for_period,
)
from .zero_cost_experiment import (
    DATA_PATH,
    _assert_accounting_invariants,
    _assert_period_batch,
    sample_periods,
)

STOP_LOSS_FRACTION = 0.02
WEEKLY_SEED = 20261015
MONTHLY_SEED = 20261016
BASELINE_REPORT = Path("reports/kraken_breakout_zero_cost_20periods_2026-10-15.json")


def _max_drawdown_pct(initial_equity: float, trades: list[dict]) -> float:
    equity = float(initial_equity)
    peak = equity
    max_drawdown = 0.0
    for trade in trades:
        equity += float(trade["net_pnl_eur"])
        peak = max(peak, equity)
        if peak > 0:
            max_drawdown = max(max_drawdown, (peak - equity) / peak * 100.0)
    return max_drawdown


def run_breakout_stop_loss_period(
    candles: list,
    *,
    period_id: str,
    initial_cash_eur: float = 100.0,
    stop_loss_fraction: float = STOP_LOSS_FRACTION,
) -> dict:
    """Run the existing breakout rules with a fixed entry-price stop, zero costs."""
    if not 0 < stop_loss_fraction < 1:
        raise ValueError("stop_loss_fraction_must_be_between_zero_and_one")

    ordered = sorted(candles, key=lambda candle: candle.interval_start)
    cash_eur = float(initial_cash_eur)
    completed_trades: list[dict] = []
    last_exit_reference_index = -1
    stop_hit_count = 0

    for signal in _candidate_signals_for_period(ordered):
        if signal["signal_index"] < last_exit_reference_index:
            continue

        entry_index = int(signal["entry_reference_index"])
        scheduled_exit_index = int(signal["exit_reference_index"])
        entry_price = float(signal["entry_price"])
        if entry_price <= 0 or cash_eur <= 0:
            continue

        stop_price = entry_price * (1.0 - stop_loss_fraction)
        actual_exit_index = scheduled_exit_index
        actual_exit_price = float(signal["exit_price"])
        exit_reason = "hold_period_exit"

        # Evaluate from the entry candle through the scheduled exit candle.
        # OHLC data cannot resolve intrabar ordering beyond open/high/low/close;
        # gap-through uses the observed open, otherwise the stop price is used.
        for candle_index in range(entry_index, scheduled_exit_index + 1):
            candle = ordered[candle_index]
            candle_open = float(candle.open)
            candle_low = float(candle.low)
            if candle_open <= stop_price:
                actual_exit_index = candle_index
                actual_exit_price = candle_open
                exit_reason = "stop_loss_gap_exit"
                break
            if candle_low <= stop_price:
                actual_exit_index = candle_index
                actual_exit_price = stop_price
                exit_reason = "stop_loss_exit"
                break
            if candle_index == scheduled_exit_index:
                actual_exit_index = candle_index
                actual_exit_price = float(candle.close)

        commitment = min(cash_eur, float(initial_cash_eur))
        quantity = commitment / entry_price
        if quantity <= 0 or actual_exit_price <= 0:
            continue

        gross_pnl = (actual_exit_price - entry_price) * quantity
        cash_after_entry = cash_eur - commitment
        cash_eur = cash_after_entry + quantity * actual_exit_price
        if exit_reason != "hold_period_exit":
            stop_hit_count += 1

        completed_trades.append({
            "period_id": period_id,
            "setup_index": int(signal["signal_index"]),
            "confirmation_index": int(signal["signal_index"]),
            "entry_reference_index": entry_index,
            "exit_reference_index": actual_exit_index,
            "entry_price": entry_price,
            "stop_price": stop_price,
            "exit_price": actual_exit_price,
            "quantity": quantity,
            "gross_pnl_eur": gross_pnl,
            "entry_cost_eur": 0.0,
            "exit_cost_eur": 0.0,
            "total_cost_eur": 0.0,
            "net_pnl_eur": gross_pnl,
            "signal_timestamp": signal["signal_timestamp"].isoformat(),
            "exit_reason": exit_reason,
            "cash_after_entry_eur": cash_after_entry,
        })
        last_exit_reference_index = actual_exit_index

    realized_pnl = sum(float(trade["net_pnl_eur"]) for trade in completed_trades)
    winning = sum(float(trade["net_pnl_eur"]) > 0 for trade in completed_trades)
    losing = sum(float(trade["net_pnl_eur"]) < 0 for trade in completed_trades)
    breakeven = len(completed_trades) - winning - losing
    end_equity = cash_eur
    result = {
        "period_id": period_id,
        "initial_cash_eur": float(initial_cash_eur),
        "cash_eur": cash_eur,
        "position_qty": 0.0,
        "entry_price_eur": 0.0,
        "open_position": None,
        "realized_gross_pnl_eur": realized_pnl,
        "realized_pnl_eur": realized_pnl,
        "unrealized_pnl_eur": 0.0,
        "costs_total_eur": 0.0,
        "completed_trades": completed_trades,
        "trades_count": len(completed_trades),
        "winning_trades": winning,
        "losing_trades": losing,
        "break_even_trades": breakeven,
        "total_equity_eur": end_equity,
        "start_equity_eur": float(initial_cash_eur),
        "end_equity_eur": end_equity,
        "percentage_return": ((end_equity - initial_cash_eur) / initial_cash_eur) * 100.0 if initial_cash_eur else 0.0,
        "signals_count": len(completed_trades),
        "entries_count": len(completed_trades),
        "completed_exits_count": len(completed_trades),
        "win_rate": winning / len(completed_trades) if completed_trades else 0.0,
        "stop_hit_count": stop_hit_count,
        "stop_loss_fraction": stop_loss_fraction,
        "max_drawdown_pct": _max_drawdown_pct(initial_cash_eur, completed_trades),
    }
    _assert_accounting_invariants(result)
    return result


def _run_period_batch(*, period_days: int, seed: int, data_path: str | Path) -> list[dict]:
    periods = sample_periods(seed=seed, period_days=period_days, count=10, data_path=data_path)
    results = []
    for period in periods:
        candles = list(period["candles"])
        result = run_breakout_stop_loss_period(candles, period_id=period["period_id"])
        result["period_start_utc"] = period["start"].isoformat()
        result["period_end_utc"] = period["end"].isoformat()
        result["period_days"] = period_days
        result["candles_evaluated"] = len(candles)
        result["selection_seed"] = seed
        _assert_accounting_invariants(result)
        results.append(result)
    _assert_period_batch(periods, period_days=period_days, expected_count=10)
    return results


def _period_key(run: dict) -> tuple[str, str]:
    return str(run["period_start_utc"]), str(run["period_end_utc"])


def _add_baseline_comparison(runs: list[dict], baseline_runs: list[dict]) -> dict:
    baseline_by_range = {_period_key(item): item for item in baseline_runs}
    for run in runs:
        baseline = baseline_by_range.get(_period_key(run))
        if baseline is None:
            raise ValueError(f"baseline_period_missing:{_period_key(run)}")
        baseline_return = float(baseline["percentage_return"])
        run["baseline_percentage_return"] = baseline_return
        run["return_change_percentage_points"] = float(run["percentage_return"]) - baseline_return
        baseline_trades = baseline.get("completed_trades", [])
        run["baseline_max_drawdown_pct"] = _max_drawdown_pct(
            float(baseline.get("initial_cash_eur", 100.0)), baseline_trades
        )
        run["max_drawdown_change_percentage_points"] = (
            float(run["max_drawdown_pct"]) - float(run["baseline_max_drawdown_pct"])
        )

    baseline_worst_four = sorted(baseline_runs, key=lambda item: float(item["percentage_return"]))[:4]
    variant_by_range = {_period_key(item): item for item in runs}
    worst_four_comparison = []
    for baseline in baseline_worst_four:
        variant = variant_by_range[_period_key(baseline)]
        worst_four_comparison.append({
            "period_id": baseline["period_id"],
            "period_start_utc": baseline["period_start_utc"],
            "period_end_utc": baseline["period_end_utc"],
            "baseline_return_pct": float(baseline["percentage_return"]),
            "stop_loss_return_pct": float(variant["percentage_return"]),
            "return_change_percentage_points": float(variant["return_change_percentage_points"]),
            "baseline_max_drawdown_pct": float(variant["baseline_max_drawdown_pct"]),
            "stop_loss_max_drawdown_pct": float(variant["max_drawdown_pct"]),
        })
    return {
        "baseline_periods_matched": len([run for run in runs if "baseline_percentage_return" in run]),
        "worst_four_baseline_periods": worst_four_comparison,
        "worst_four_improved_return_count": sum(item["return_change_percentage_points"] > 0 for item in worst_four_comparison),
        "worst_four_lower_drawdown_count": sum(
            item["stop_loss_max_drawdown_pct"] < item["baseline_max_drawdown_pct"]
            for item in worst_four_comparison
        ),
    }


def run_stop_loss_experiment(
    *,
    data_path: str | Path = DATA_PATH,
    output_dir: str | Path = "reports",
    baseline_report_path: str | Path = BASELINE_REPORT,
) -> dict:
    baseline_path = Path(baseline_report_path)
    if not baseline_path.exists():
        raise FileNotFoundError(f"baseline_report_required:{baseline_path}")
    baseline_payload = json.loads(baseline_path.read_text(encoding="utf-8"))

    weekly = _run_period_batch(period_days=7, seed=WEEKLY_SEED, data_path=data_path)
    monthly = _run_period_batch(period_days=30, seed=MONTHLY_SEED, data_path=data_path)
    comparison = {
        "weekly": _add_baseline_comparison(weekly, baseline_payload["weekly_runs"]),
        "monthly": _add_baseline_comparison(monthly, baseline_payload["monthly_runs"]),
    }
    source_sha256 = hashlib.sha256(Path(data_path).read_bytes()).hexdigest()
    payload = {
        "experiment": {
            "name": "breakout_fixed_2pct_stop_loss_zero_cost_20_period_research",
            "status": "experimental_hypothesis_not_approved_for_live_trading",
            "stop_loss_fraction": STOP_LOSS_FRACTION,
            "initial_cash_eur": 100.0,
            "symbol": "BTC-EUR",
            "interval_minutes": 5,
            "transaction_costs_zeroed": True,
            "strategy_rules_preserved_except_stop_loss": True,
            "strategy": dict(BREAKOUT_ZERO_COST_CONFIG),
            "data_path": str(Path(data_path)),
            "source_sha256": source_sha256,
            "period_selection": {
                "weekly_seed": WEEKLY_SEED,
                "monthly_seed": MONTHLY_SEED,
                "weekly_count": 10,
                "monthly_count": 10,
                "baseline_report": str(baseline_path),
            },
            "limitations": [
                "Zero fees, spread, and slippage; this is not a live profitability result.",
                "OHLC candles cannot determine actual stop order fills or intrabar liquidity.",
                "A gap-through stop is modeled at the observed candle open, not at the stop price.",
                "The 2% stop is a research hypothesis and is not an approved live-trading rule.",
            ],
        },
        "weekly_runs": weekly,
        "monthly_runs": monthly,
        "comparison": comparison,
    }
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "kraken_breakout_stop_loss_2pct_20periods_2026-10-15.json"
    manifest_path = output_dir / "kraken_breakout_stop_loss_2pct_20periods_2026-10-15_manifest.json"
    report_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    manifest_path.write_text(json.dumps({
        "report_path": str(report_path),
        "baseline_report_path": str(baseline_path),
        "source_sha256": source_sha256,
        "stop_loss_fraction": STOP_LOSS_FRACTION,
        "weekly_runs": len(weekly),
        "monthly_runs": len(monthly),
        "comparison": comparison,
    }, indent=2, sort_keys=True), encoding="utf-8")
    return payload


if __name__ == "__main__":
    result = run_stop_loss_experiment()
    print("Wrote reports/kraken_breakout_stop_loss_2pct_20periods_2026-10-15.json")
    print(f"Weekly periods: {len(result['weekly_runs'])}")
    print(f"Monthly periods: {len(result['monthly_runs'])}")
