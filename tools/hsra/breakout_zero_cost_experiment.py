from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path

from .breakout_strategy import evaluate_price_channel_breakout_signal
from .zero_cost_experiment import (
    DATA_PATH,
    _assert_accounting_invariants,
    _assert_period_batch,
    sample_periods,
)

BREAKOUT_ZERO_COST_CONFIG = {
    "channel_lookback": 6,
    "trend_filter": "close_above_sma20_and_sma20_gt_sma50",
    "hold_period": 6,
    "entry_reference": "next_candle_open",
    "exit_reference": "final_candle_close",
    "initial_cash_eur": 100.0,
}


def _period_candle_count(period_days: int) -> int:
    return int((timedelta(days=period_days).total_seconds() / 300.0))


def _trend_filter_passes(*, signal_close: float, candles: list, signal_index: int, trend_filter: str) -> bool:
    if trend_filter == "none":
        return True
    lookback_20 = candles[max(0, signal_index - 20):signal_index]
    if len(lookback_20) < 20:
        return False
    sma_20 = sum(float(candle.close) for candle in lookback_20) / len(lookback_20)
    if trend_filter == "close_above_sma20":
        return signal_close > sma_20
    lookback_50 = candles[max(0, signal_index - 50):signal_index]
    if len(lookback_50) < 50:
        return False
    sma_50 = sum(float(candle.close) for candle in lookback_50) / len(lookback_50)
    return signal_close > sma_20 and sma_20 > sma_50


def _candidate_signals_for_period(candles: list, *, channel_lookback: int = 6, trend_filter: str = "close_above_sma20_and_sma20_gt_sma50", hold_period: int = 6):
    minimum_required_history = max(
        channel_lookback,
        20 if trend_filter in {"close_above_sma20", "close_above_sma20_and_sma20_gt_sma50"} else 0,
        50 if trend_filter == "close_above_sma20_and_sma20_gt_sma50" else 0,
    )
    for signal_index in range(minimum_required_history, len(candles) - 1):
        signal = candles[signal_index]
        channel_window = candles[signal_index - channel_lookback:signal_index]
        if len(channel_window) < channel_lookback:
            continue
        channel_high = max(float(candle.high) for candle in channel_window)
        if float(signal.close) <= channel_high:
            continue
        if not _trend_filter_passes(signal_close=float(signal.close), candles=candles, signal_index=signal_index, trend_filter=trend_filter):
            continue
        entry_reference_index = signal_index + 1
        exit_reference_index = entry_reference_index + hold_period - 1
        if exit_reference_index >= len(candles):
            continue
        entry_price = float(candles[entry_reference_index].open)
        exit_price = float(candles[exit_reference_index].close)
        if entry_price <= 0 or exit_price <= 0:
            continue
        yield {
            "signal_index": signal_index,
            "entry_reference_index": entry_reference_index,
            "exit_reference_index": exit_reference_index,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "signal_timestamp": signal.interval_end,
        }


def run_breakout_zero_cost_period(candles: list, *, period_id: str, initial_cash_eur: float = 100.0) -> dict:
    ordered = sorted(candles, key=lambda candle: candle.interval_start)
    cash_eur = float(initial_cash_eur)
    position_qty = 0.0
    entry_price_eur = 0.0
    open_position = None
    realized_gross_pnl_eur = 0.0
    realized_pnl_eur = 0.0
    unrealized_pnl_eur = 0.0
    completed_trades: list[dict] = []
    last_exit_reference_index = -1
    for signal in _candidate_signals_for_period(ordered):
        # The exit occurs at the exit candle's close, so a new signal on that
        # candle may enter on the following candle; earlier signals overlap.
        if signal["signal_index"] < last_exit_reference_index:
            continue
        if open_position is not None:
            continue
        entry_price = float(signal["entry_price"])
        exit_price = float(signal["exit_price"])
        commitment = min(cash_eur, initial_cash_eur)
        if commitment <= 0:
            break
        quantity = commitment / entry_price
        if quantity <= 0:
            continue
        gross_pnl = (exit_price - entry_price) * quantity
        cash_eur -= commitment
        position_qty = quantity
        entry_price_eur = entry_price
        open_position = {
            "entry_reference_index": signal["entry_reference_index"],
            "entry_price": entry_price,
            "entry_quantity": quantity,
            "entry_timestamp": signal["signal_timestamp"].isoformat(),
            "exit_index": signal["exit_reference_index"],
            "exit_price": exit_price,
            "gross_pnl_eur": gross_pnl,
            "net_pnl_eur": gross_pnl,
            "open": True,
        }

        trade = {
            "period_id": period_id,
            "setup_index": signal["signal_index"],
            "confirmation_index": signal["signal_index"],
            "entry_reference_index": signal["entry_reference_index"],
            "entry_price": entry_price,
            "exit_price": exit_price,
            "quantity": quantity,
            "gross_pnl_eur": gross_pnl,
            "entry_cost_eur": 0.0,
            "exit_cost_eur": 0.0,
            "total_cost_eur": 0.0,
            "net_pnl_eur": gross_pnl,
            "signal_timestamp": signal["signal_timestamp"].isoformat(),
            "exit_reason": "hold_period_exit",
            "cash_after_entry_eur": cash_eur,
        }
        completed_trades.append(trade)
        last_exit_reference_index = signal["exit_reference_index"]

        realized_gross_pnl_eur += gross_pnl
        realized_pnl_eur += gross_pnl
        cash_eur += quantity * exit_price
        position_qty = 0.0
        entry_price_eur = 0.0
        open_position = None

    end_equity_eur = cash_eur + (position_qty * entry_price_eur)
    winning_trades = sum(1 for trade in completed_trades if trade["net_pnl_eur"] > 0)
    losing_trades = sum(1 for trade in completed_trades if trade["net_pnl_eur"] < 0)
    break_even_trades = sum(1 for trade in completed_trades if abs(trade["net_pnl_eur"]) < 1e-9)

    result = {
        "period_id": period_id,
        "initial_cash_eur": float(initial_cash_eur),
        "cash_eur": cash_eur,
        "position_qty": position_qty,
        "entry_price_eur": entry_price_eur,
        "open_position": open_position,
        "realized_gross_pnl_eur": realized_gross_pnl_eur,
        "realized_pnl_eur": realized_pnl_eur,
        "unrealized_pnl_eur": unrealized_pnl_eur,
        "costs_total_eur": 0.0,
        "completed_trades": completed_trades,
        "trades_count": len(completed_trades),
        "winning_trades": winning_trades,
        "losing_trades": losing_trades,
        "break_even_trades": break_even_trades,
        "total_equity_eur": end_equity_eur,
        "start_equity_eur": float(initial_cash_eur),
        "end_equity_eur": end_equity_eur,
        "percentage_return": ((end_equity_eur - initial_cash_eur) / initial_cash_eur) * 100.0 if initial_cash_eur else 0.0,
        "signals_count": len(completed_trades),
        "entries_count": len(completed_trades),
        "completed_exits_count": len(completed_trades),
        "win_rate": (winning_trades / len(completed_trades)) if completed_trades else 0.0,
    }
    _assert_accounting_invariants(result)
    return result


def run_period_batch(*, period_days: int, count: int, seed: int, data_path: str | Path = DATA_PATH) -> list[dict]:
    periods = sample_periods(seed=seed, period_days=period_days, count=count, data_path=data_path)
    results = []
    for period in periods:
        selected = list(period["candles"])
        result = run_breakout_zero_cost_period(selected, period_id=period["period_id"])
        result["period_start_utc"] = period["start"].isoformat()
        result["period_end_utc"] = period["end"].isoformat()
        result["period_days"] = period_days
        result["candles_evaluated"] = len(selected)
        result["selection_seed"] = seed
        _assert_accounting_invariants(result)
        results.append(result)
    _assert_period_batch(periods, period_days=period_days, expected_count=count)
    return results


def get_period_ranges(*, data_path: str | Path = DATA_PATH) -> tuple[list[dict], list[dict]]:
    weekly = sample_periods(seed=20261015, period_days=7, count=10, data_path=data_path)
    monthly = sample_periods(seed=20261016, period_days=30, count=10, data_path=data_path)
    normalized_weekly = [
        {
            "period_id": period["period_id"],
            "type": "weekly",
            "start": period["start"].isoformat(),
            "end": period["end"].isoformat(),
            "days": 7,
            "count": len(period["candles"]),
        }
        for period in weekly
    ]
    normalized_monthly = [
        {
            "period_id": period["period_id"],
            "type": "monthly",
            "start": period["start"].isoformat(),
            "end": period["end"].isoformat(),
            "days": 30,
            "count": len(period["candles"]),
        }
        for period in monthly
    ]
    return normalized_weekly, normalized_monthly


def run_breakout_experiment(*, seed_weekly: int = 20261015, seed_monthly: int = 20261016, data_path: str | Path = DATA_PATH, output_dir: str | Path = "reports") -> dict:
    weekly = run_period_batch(period_days=7, count=10, seed=seed_weekly, data_path=data_path)
    monthly = run_period_batch(period_days=30, count=10, seed=seed_monthly, data_path=data_path)
    weekly_returns = [float(item["percentage_return"]) for item in weekly]
    monthly_returns = [float(item["percentage_return"]) for item in monthly]

    weekly_summary = {
        "period_count": len(weekly),
        "profitable_periods": sum(1 for item in weekly if item["realized_pnl_eur"] > 0),
        "losing_periods": sum(1 for item in weekly if item["realized_pnl_eur"] < 0),
        "zero_trade_periods": sum(1 for item in weekly if item["trades_count"] == 0),
        "mean_percentage_return": (sum(weekly_returns) / len(weekly_returns)) if weekly_returns else 0.0,
        "median_percentage_return": (sorted(weekly_returns)[len(weekly_returns) // 2] if len(weekly_returns) % 2 else (sorted(weekly_returns)[len(weekly_returns) // 2 - 1] + sorted(weekly_returns)[len(weekly_returns) // 2]) / 2.0) if weekly_returns else 0.0,
        "best_period": max(weekly, key=lambda item: item["percentage_return"], default=None),
        "worst_period": min(weekly, key=lambda item: item["percentage_return"], default=None),
        "total_completed_trades": sum(item["trades_count"] for item in weekly),
    }
    monthly_summary = {
        "period_count": len(monthly),
        "profitable_periods": sum(1 for item in monthly if item["realized_pnl_eur"] > 0),
        "losing_periods": sum(1 for item in monthly if item["realized_pnl_eur"] < 0),
        "zero_trade_periods": sum(1 for item in monthly if item["trades_count"] == 0),
        "mean_percentage_return": (sum(monthly_returns) / len(monthly_returns)) if monthly_returns else 0.0,
        "median_percentage_return": (sorted(monthly_returns)[len(monthly_returns) // 2] if len(monthly_returns) % 2 else (sorted(monthly_returns)[len(monthly_returns) // 2 - 1] + sorted(monthly_returns)[len(monthly_returns) // 2]) / 2.0) if monthly_returns else 0.0,
        "best_period": max(monthly, key=lambda item: item["percentage_return"], default=None),
        "worst_period": min(monthly, key=lambda item: item["percentage_return"], default=None),
        "total_completed_trades": sum(item["trades_count"] for item in monthly),
    }

    source_path = Path(data_path)
    raw_sha256 = hashlib.sha256(source_path.read_bytes()).hexdigest()
    payload = {
        "experiment": {
            "name": "breakout_zero_cost_20_period_research",
            "config": {
                "selection_seed": seed_weekly,
                "weekly_selection_seed": seed_weekly,
                "monthly_selection_seed": seed_monthly,
                "periods": [
                    {"type": "weekly", "days": 7, "count": 10},
                    {"type": "monthly", "days": 30, "count": 10},
                ],
                "initial_cash_eur": 100.0,
                "transaction_costs_zeroed": True,
                "strategy_rules_preserved": True,
                "notional_eur": 100.0,
                "symbol": "BTC-EUR",
                "strategy": {
                    "name": "trend_filtered_breakout",
                    "channel_lookback": 6,
                    "trend_filter": "close_above_sma20_and_sma20_gt_sma50",
                    "hold_period": 6,
                    "entry_reference": "next_candle_open",
                    "exit_reference": "final_candle_close",
                },
            },
            "data": {
                "dataset_path": str(Path(data_path)),
                "dataset_name": "kraken_btc_eur_5m_ohlcv",
                "market": "BTC-EUR",
                "interval_minutes": 5,
                "continuity_rule": "only contiguous windows used; no gaps bridged or fabricated",
                "raw_sha256": raw_sha256,
            },
            "methodology": {
                "date_ranges_preserved": "Same 20 period ranges and sampling seeds as the previous zero-cost 20-period experiment.",
                "risk_model": "Zero-cost spot research only; no fees, spread, slippage, or live execution assumptions.",
                "position_management": "One trade at a time per period; no overlapping positions; position is closed at the breakout exit horizon.",
                "selection_rule": "Frozen strategy parameters were fixed before running this experiment; no optimization against these periods.",
            },
        },
        "weekly_runs": weekly,
        "monthly_runs": monthly,
        "weekly_summary": weekly_summary,
        "monthly_summary": monthly_summary,
        "period_ranges": {
            "weekly": get_period_ranges(data_path=data_path)[0],
            "monthly": get_period_ranges(data_path=data_path)[1],
        },
        "selected_parameters": {
            "channel_lookback": BREAKOUT_ZERO_COST_CONFIG["channel_lookback"],
            "trend_filter": BREAKOUT_ZERO_COST_CONFIG["trend_filter"],
            "hold_period": BREAKOUT_ZERO_COST_CONFIG["hold_period"],
        },
    }

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "kraken_breakout_zero_cost_20periods_2026-10-15.json"
    manifest_path = output_dir / "kraken_breakout_zero_cost_20periods_2026-10-15_manifest.json"
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    manifest_path.write_text(json.dumps({
        "report_path": str(out_path),
        "source_sha256": raw_sha256,
        "selected_parameters": payload["selected_parameters"],
        "period_ranges": payload["period_ranges"],
        "weekly_runs": len(weekly),
        "monthly_runs": len(monthly),
    }, indent=2, sort_keys=True), encoding="utf-8")
    return payload


if __name__ == "__main__":
    result = run_breakout_experiment()
    print(f"Wrote reports/kraken_breakout_zero_cost_20periods_2026-10-15.json")
    print(f"Weekly periods: {len(result['weekly_runs'])}")
    print(f"Monthly periods: {len(result['monthly_runs'])}")
