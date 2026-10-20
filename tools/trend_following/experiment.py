from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Sequence

from tools.trend_following.execution import (
    ExecutionConfig,
    WindowSpec,
    select_complete_windows,
    simulate_hourly_execution,
)
from tools.trend_following.kraken_hourly import (
    TrendCandle,
    build_complete_utc_daily_candles,
    load_kraken_hourly,
)


def build_window_plan(
    daily_candles: Sequence[TrendCandle],
    *,
    window_days: int = 30,
    count: int = 20,
    seed: int | None = None,
    selection_method: str = "seeded_stride",
) -> list[WindowSpec]:
    """Select the reproducible 30-day main-experiment windows from complete UTC daily bars."""
    if seed is None:
        raise ValueError("seed must be explicitly set for reproducible window selection")
    day_starts = [candle.interval_start for candle in daily_candles]
    return select_complete_windows(
        day_starts,
        window_days=window_days,
        count=count,
        seed=seed,
        selection_method=selection_method,
    )


def _summarize_window_results(results: Sequence[dict[str, Any]]) -> dict[str, Any]:
    if not results:
        return {
            "window_count": 0,
            "mean_net_return_pct": 0.0,
            "positive_window_ratio": 0.0,
            "mean_buy_and_hold_return_pct": 0.0,
            "mean_fully_liquidated_equity_eur": 0.0,
            "total_fees_eur": 0.0,
            "total_slippage_eur": 0.0,
        }

    returns = [float(item["net_return_pct"]) for item in results]
    buy_hold = [float(item["buy_and_hold_return_pct"]) for item in results]
    liquidated = [float(item["fully_liquidated_equity_eur"]) for item in results]
    fees = [float(item["fees_eur"]) for item in results]
    slippage = [float(item["slippage_eur"]) for item in results]
    positive = sum(1 for value in returns if value > 0.0)

    return {
        "window_count": len(results),
        "mean_net_return_pct": sum(returns) / len(returns),
        "positive_window_ratio": positive / len(results),
        "mean_buy_and_hold_return_pct": sum(buy_hold) / len(buy_hold),
        "mean_fully_liquidated_equity_eur": sum(liquidated) / len(liquidated),
        "total_fees_eur": sum(fees),
        "total_slippage_eur": sum(slippage),
    }


def run_window_experiment(
    *,
    hourly_candles: Sequence[TrendCandle],
    daily_candles: Sequence[TrendCandle],
    window_days: int = 30,
    count: int = 20,
    seed: int | None = None,
    selection_method: str = "seeded_stride",
    delay_hours: int = 0,
    fee_bps_per_side: float = 25.0,
    slippage_bps_per_side: float = 1.5,
    initialization_modes: Sequence[str] = ("WARM", "COLD"),
) -> dict[str, Any]:
    """Execute the approved 20-window main experiment for the WARM/COLD research modes."""
    if seed is None:
        raise ValueError("seed must be explicitly set for reproducible window selection")
    windows = build_window_plan(
        daily_candles,
        window_days=window_days,
        count=count,
        seed=seed,
        selection_method=selection_method,
    )
    config = ExecutionConfig(
        delay_hours=delay_hours,
        fee_bps_per_side=fee_bps_per_side,
        slippage_bps_per_side=slippage_bps_per_side,
        window_days=window_days,
        selection_seed=seed,
        selection_method=selection_method,
    )

    results: dict[str, list[dict[str, Any]]] = {}
    summaries: dict[str, dict[str, Any]] = {}
    for mode in initialization_modes:
        mode_results: list[dict[str, Any]] = []
        for window in windows:
            prepared_window = WindowSpec(
                start=window.start,
                end=window.end,
                initialization=mode,
                selection_seed=seed,
                selection_method=selection_method,
            )
            result = simulate_hourly_execution(
                hourly_candles=hourly_candles,
                daily_candles=daily_candles,
                window=prepared_window,
                config=config,
            )
            mode_results.append(result)
        results[mode] = mode_results
        summaries[mode] = _summarize_window_results(mode_results)

    return {
        "config": {
            "window_days": window_days,
            "count": count,
            "seed": seed,
            "selection_method": selection_method,
            "delay_hours": delay_hours,
            "fee_bps_per_side": fee_bps_per_side,
            "slippage_bps_per_side": slippage_bps_per_side,
            "initialization_modes": list(initialization_modes),
        },
        "selected_windows": [
            {
                "start": window.start.isoformat(),
                "end": window.end.isoformat(),
                "initialization": mode,
                "selection_seed": seed,
                "selection_method": selection_method,
            }
            for mode in initialization_modes
            for window in windows
        ],
        "results": results,
        "summary": summaries,
    }


def _load_and_prepare_data(hourly_path: str | Path) -> tuple[list[TrendCandle], list[TrendCandle]]:
    hourly_candles = load_kraken_hourly(hourly_path)
    daily_candles = build_complete_utc_daily_candles(hourly_candles)
    return hourly_candles, daily_candles


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the approved 20-window BTC/EUR trend-following experiment.")
    parser.add_argument("--hourly", type=Path, default=Path("data/kraken/XBTEUR_60.csv"), help="Path to the validated hourly Kraken OHLCV file.")
    parser.add_argument("--window-days", type=int, default=30)
    parser.add_argument("--count", type=int, default=20)
    parser.add_argument("--seed", type=int, required=True, help="Explicit reproducibility seed for the approved seeded window selection method.")
    parser.add_argument("--delay-hours", type=int, default=0)
    parser.add_argument("--fee-bps", type=float, default=25.0)
    parser.add_argument("--slippage-bps", type=float, default=1.5)
    parser.add_argument("--output", type=Path, default=None, help="Optional path to write the experiment JSON report.")
    args = parser.parse_args()

    hourly_candles, daily_candles = _load_and_prepare_data(args.hourly)
    report = run_window_experiment(
        hourly_candles=hourly_candles,
        daily_candles=daily_candles,
        window_days=args.window_days,
        count=args.count,
        seed=args.seed,
        delay_hours=args.delay_hours,
        fee_bps_per_side=args.fee_bps,
        slippage_bps_per_side=args.slippage_bps,
    )

    rendered = json.dumps(report, indent=2, default=str)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
