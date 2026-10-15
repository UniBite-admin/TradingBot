from __future__ import annotations

import json
from datetime import timedelta
from pathlib import Path

from .backtest import HistoricalBacktestHarness
from .kraken_ohlcv import extract_contiguous_kraken_windows, load_kraken_ohlcv

DATA_PATH = Path("data/kraken/XBTEUR_5.csv")
REPORT_PATH = Path("reports/kraken_segmented_7d_2026-10-15.json")
WEEK_CANDLES = 7 * 24 * 12


def find_latest_complete_week(candles):
    windows = extract_contiguous_kraken_windows(candles)
    eligible = [window for window in windows if len(window) >= WEEK_CANDLES]
    if not eligible:
        raise ValueError("No contiguous Kraken window is large enough for a complete seven-day evaluation.")

    latest_window = max(eligible, key=lambda window: window[-1].interval_end)
    period_end = latest_window[-1].interval_end
    period_start = period_end - timedelta(days=7)
    selected = [
        candle
        for candle in latest_window
        if candle.interval_start >= period_start and candle.interval_start < period_end
    ]
    if len(selected) != WEEK_CANDLES:
        raise ValueError(
            f"Expected {WEEK_CANDLES} candles in the selected week but found {len(selected)}."
        )

    return {
        "period_start_utc": period_start.isoformat(),
        "period_end_utc": period_end.isoformat(),
        "selected_candle_count": len(selected),
        "selected_candles": selected,
        "window_start_utc": latest_window[0].interval_start.isoformat(),
        "window_end_utc": latest_window[-1].interval_end.isoformat(),
        "window_candle_count": len(latest_window),
    }


def summarize_trades(trades):
    if not trades:
        return {
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate": 0.0,
            "gross_pnl_eur": 0.0,
            "total_cost_eur": 0.0,
            "net_pnl_eur": 0.0,
            "modeled_cost_components": {
                "entry_fee_eur": 0.0,
                "exit_fee_eur": 0.0,
                "spread_eur": 0.0,
                "slippage_eur": 0.0,
                "latency_eur": 0.0,
            },
        }

    winning = sum(1 for trade in trades if trade["net_pnl_eur"] > 0)
    losing = sum(1 for trade in trades if trade["net_pnl_eur"] < 0)
    total_cost = sum(trade["entry_cost_eur"] + trade["exit_cost_eur"] for trade in trades)
    gross = sum(trade["gross_pnl_eur"] for trade in trades)
    net = sum(trade["net_pnl_eur"] for trade in trades)
    return {
        "winning_trades": winning,
        "losing_trades": losing,
        "win_rate": (winning / len(trades)) if trades else 0.0,
        "gross_pnl_eur": gross,
        "total_cost_eur": total_cost,
        "net_pnl_eur": net,
        "modeled_cost_components": {
            "entry_fee_eur": sum(trade["entry_cost_eur"] for trade in trades),
            "exit_fee_eur": sum(trade["exit_cost_eur"] for trade in trades),
            "spread_eur": 0.0,
            "slippage_eur": 0.0,
            "latency_eur": 0.0,
        },
    }


def main() -> dict:
    candles = load_kraken_ohlcv(DATA_PATH)
    window_info = find_latest_complete_week(candles)
    harness = HistoricalBacktestHarness(symbol="BTC-EUR", lookback=3, hold_period=3, notional_eur=100.0)
    result = harness.run_segmented(window_info["selected_candles"])

    summary = result["summary"]
    trades = result["trades"]
    trade_summary = summarize_trades(trades)
    payload = {
        "dataset": {
            "identity": {
                "dataset_name": "kraken_btc_eur_5m_ohlcv",
                "dataset_path": str(DATA_PATH),
                "market": "BTC-EUR",
                "interval_minutes": 5,
                "raw_sha256": None,
                "raw_identity_blocker": "sha256 is null in manifest; exact raw-byte identity is not cryptographically established.",
            },
            "selected_period_utc": {
                "start": window_info["period_start_utc"],
                "end": window_info["period_end_utc"],
                "candles": window_info["selected_candle_count"],
            },
            "contiguous_window_utc": {
                "start": window_info["window_start_utc"],
                "end": window_info["window_end_utc"],
                "candles": window_info["window_candle_count"],
            },
        },
        "config": result["config"],
        "assumptions": {
            "segment_boundaries_reset_state": True,
            "gaps_not_backfilled": True,
            "no_position_carry_across_segments": True,
            "entry_price_rule": "entry based on next executable open after signal, as implemented in HistoricalBacktestHarness._candidate_signals",
            "exit_price_rule": "exit based on configured hold period close, as implemented in HistoricalBacktestHarness._candidate_signals",
            "status": "bounded_historical_research_only",
        },
        "results": {
            "segment_count": summary["segment_count"],
            "rejected_segments": summary["rejected_segments"],
            "candles_evaluated": summary["candles"],
            "decision_count": summary["decision_count"],
            "signal_count": summary["decision_count"],
            "completed_trade_count": summary["trade_count"],
            "winning_trades": trade_summary["winning_trades"],
            "losing_trades": trade_summary["losing_trades"],
            "win_rate": trade_summary["win_rate"],
            "gross_pnl_eur": summary["gross_pnl_eur"],
            "modeled_costs_eur": {
                "entry_cost_eur": sum(trade["entry_cost_eur"] for trade in trades),
                "exit_cost_eur": sum(trade["exit_cost_eur"] for trade in trades),
                "total_cost_eur": trade_summary["total_cost_eur"],
                "fee_eur": sum(trade["entry_cost_eur"] + trade["exit_cost_eur"] for trade in trades),
                "spread_eur": None,
                "slippage_eur": None,
                "latency_cost_eur": None,
            },
            "net_pnl_eur": summary["net_pnl_eur"],
            "starting_equity_eur": None,
            "ending_equity_eur": None,
            "exclusion_summary": {
                "gaps_rejected": summary["rejected_segments"] > 0,
                "unfinished_trades": None,
                "exit_reasons": None,
            },
            "trades": trades,
        },
        "limitations": [
            "This is a bounded 7-day historical run using only the existing repo strategy and cost model.",
            "No position sizing ledger or cash-accounting model is implemented for starting/ending equity in this harness.",
            "The strategy is not optimized or re-parameterized for this week.",
            "This report is for descriptive research only and does not imply profitability or execution realism.",
        ],
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


if __name__ == "__main__":
    main()
