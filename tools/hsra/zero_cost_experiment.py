from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .backtest import HistoricalBacktestHarness
from .kraken_ohlcv import extract_contiguous_kraken_windows, load_kraken_ohlcv


DATA_PATH = Path("data/kraken/XBTEUR_5.csv")


def _period_candle_count(period_days: int) -> int:
    return int((timedelta(days=period_days).total_seconds() / 300.0))


def _assert_accounting_invariants(result: dict) -> None:
    trades = result.get("completed_trades", [])
    trade_count = int(result.get("trades_count", len(trades)))
    winning_trades = int(result.get("winning_trades", sum(1 for trade in trades if float(trade.get("net_pnl_eur", 0.0)) > 0.0)))
    losing_trades = int(result.get("losing_trades", sum(1 for trade in trades if float(trade.get("net_pnl_eur", 0.0)) < 0.0)))
    break_even_trades = int(result.get("break_even_trades", sum(1 for trade in trades if abs(float(trade.get("net_pnl_eur", 0.0))) < 1e-9)))

    assert winning_trades + losing_trades + break_even_trades == trade_count, (
        f"trade counts inconsistent: winning={winning_trades}, losing={losing_trades}, break_even={break_even_trades}, trades_count={trade_count}"
    )

    realized_gross = float(result.get("realized_gross_pnl_eur", sum(float(trade.get("gross_pnl_eur", 0.0)) for trade in trades)))
    realized_net = float(result.get("realized_pnl_eur", sum(float(trade.get("net_pnl_eur", 0.0)) for trade in trades)))
    assert abs(realized_gross - sum(float(trade.get("gross_pnl_eur", 0.0)) for trade in trades)) < 1e-9
    assert abs(realized_net - sum(float(trade.get("net_pnl_eur", 0.0)) for trade in trades)) < 1e-9

    cash_eur = float(result.get("cash_eur", 0.0))
    position_qty = float(result.get("position_qty", 0.0))
    entry_price_eur = float(result.get("entry_price_eur", 0.0))
    end_equity_eur = float(result.get("end_equity_eur", cash_eur + position_qty * entry_price_eur))
    assert abs(end_equity_eur - (cash_eur + position_qty * entry_price_eur)) < 1e-9

    percentage_return = float(result.get("percentage_return", 0.0))
    initial_cash_eur = float(result.get("initial_cash_eur", 0.0))
    if initial_cash_eur > 0:
        expected_percentage = ((end_equity_eur - initial_cash_eur) / initial_cash_eur) * 100.0
        assert abs(percentage_return - expected_percentage) < 1e-9, (
            f"return mismatch: percentage_return={percentage_return}, expected={expected_percentage}"
        )

    if result.get("period_start_utc") and result.get("period_end_utc"):
        start_dt = datetime.fromisoformat(result["period_start_utc"])
        end_dt = datetime.fromisoformat(result["period_end_utc"])
        assert end_dt - start_dt == timedelta(days=result.get("period_days", 0)), (
            f"period duration mismatch: {result['period_id']} spans {end_dt - start_dt} instead of {timedelta(days=result.get('period_days', 0))}"
        )


@dataclass
class ZeroCostPeriodAccount:
    period_id: str
    initial_cash_eur: float = 100.0
    cash_eur: float = 100.0
    position_qty: float = 0.0
    entry_price_eur: float = 0.0
    open_position: dict | None = None
    realized_gross_pnl_eur: float = 0.0
    realized_pnl_eur: float = 0.0
    unrealized_pnl_eur: float = 0.0
    costs_total_eur: float = 0.0
    completed_trades: list[dict] = field(default_factory=list)

    @property
    def position_value_eur(self) -> float:
        if self.position_qty <= 0 or self.entry_price_eur <= 0:
            return 0.0
        return self.position_qty * self.entry_price_eur

    @property
    def total_equity_eur(self) -> float:
        return self.cash_eur + self.position_value_eur

    @property
    def positions_open(self) -> int:
        return 1 if self.open_position is not None else 0

    @classmethod
    def from_result(cls, result: dict) -> "ZeroCostPeriodAccount":
        return cls(
            period_id=result["period_id"],
            initial_cash_eur=result["initial_cash_eur"],
            cash_eur=result["cash_eur"],
            position_qty=result["position_qty"],
            entry_price_eur=result["entry_price_eur"],
            open_position=result.get("open_position"),
            realized_gross_pnl_eur=result["realized_gross_pnl_eur"],
            realized_pnl_eur=result["realized_pnl_eur"],
            unrealized_pnl_eur=result["unrealized_pnl_eur"],
            costs_total_eur=result["costs_total_eur"],
            completed_trades=result["completed_trades"],
        )


def _candidate_signals_for_period(candles: list, *, lookback: int = 3, hold_period: int = 3):
    harness = HistoricalBacktestHarness(symbol="BTC-EUR", lookback=lookback, hold_period=hold_period, notional_eur=100.0)
    for signal in harness._candidate_signals(candles):
        if signal["exit_index"] >= len(candles):
            continue
        yield signal


def run_zero_cost_period(candles: list, *, period_id: str, initial_cash_eur: float = 100.0) -> dict:
    ordered = sorted(candles, key=lambda candle: candle.interval_start)
    account = ZeroCostPeriodAccount(period_id=period_id, initial_cash_eur=initial_cash_eur, cash_eur=initial_cash_eur)
    trades: list[dict] = []

    for signal in _candidate_signals_for_period(ordered):
        if account.open_position is not None:
            continue

        entry_price = float(signal["entry_price"])
        if entry_price <= 0:
            continue

        commitment = min(account.cash_eur, initial_cash_eur)
        if commitment <= 0:
            break

        quantity = commitment / entry_price
        if quantity <= 0:
            continue

        exit_price = float(signal["exit_price"])
        if exit_price <= 0:
            continue

        gross_pnl = (exit_price - entry_price) * quantity
        account.cash_eur -= commitment
        account.position_qty = quantity
        account.entry_price_eur = entry_price
        account.open_position = {
            "setup_index": signal["setup_index"],
            "confirmation_index": signal["confirmation_index"],
            "entry_reference_index": signal["entry_reference_index"],
            "entry_price": entry_price,
            "entry_quantity": quantity,
            "entry_timestamp": signal["signal_timestamp"].isoformat(),
            "exit_index": signal["exit_index"],
            "exit_price": exit_price,
            "gross_pnl_eur": gross_pnl,
            "net_pnl_eur": gross_pnl,
            "open": True,
        }

        trade = {
            "period_id": period_id,
            "setup_index": signal["setup_index"],
            "confirmation_index": signal["confirmation_index"],
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
            "cash_after_entry_eur": account.cash_eur,
        }
        trades.append(trade)

        account.realized_gross_pnl_eur += gross_pnl
        account.realized_pnl_eur += gross_pnl
        account.cash_eur += quantity * exit_price
        account.position_qty = 0.0
        account.entry_price_eur = 0.0
        account.open_position = None

    if account.open_position is not None:
        last_price = float(ordered[-1].close)
        account.unrealized_pnl_eur = (last_price - account.entry_price_eur) * account.position_qty

    account.costs_total_eur = 0.0
    account.completed_trades = trades

    winning_trades = sum(1 for trade in trades if trade["net_pnl_eur"] > 0)
    losing_trades = sum(1 for trade in trades if trade["net_pnl_eur"] < 0)
    break_even_trades = sum(1 for trade in trades if abs(trade["net_pnl_eur"]) < 1e-9)
    end_equity_eur = account.cash_eur + (account.position_qty * account.entry_price_eur)

    result = {
        "period_id": period_id,
        "initial_cash_eur": initial_cash_eur,
        "cash_eur": account.cash_eur,
        "position_qty": account.position_qty,
        "entry_price_eur": account.entry_price_eur,
        "open_position": account.open_position,
        "realized_gross_pnl_eur": account.realized_gross_pnl_eur,
        "realized_pnl_eur": account.realized_pnl_eur,
        "unrealized_pnl_eur": account.unrealized_pnl_eur,
        "costs_total_eur": account.costs_total_eur,
        "completed_trades": trades,
        "trades_count": len(trades),
        "winning_trades": winning_trades,
        "losing_trades": losing_trades,
        "break_even_trades": break_even_trades,
        "total_equity_eur": end_equity_eur,
        "start_equity_eur": initial_cash_eur,
        "end_equity_eur": end_equity_eur,
        "percentage_return": ((end_equity_eur - initial_cash_eur) / initial_cash_eur) * 100.0 if initial_cash_eur else 0.0,
        "signals_count": len(trades),
        "entries_count": len(trades),
        "completed_exits_count": len(trades),
        "win_rate": (winning_trades / len(trades)) if trades else 0.0,
    }
    _assert_accounting_invariants(result)
    return result


def _assert_period_batch(periods: list[dict], *, period_days: int, expected_count: int) -> None:
    assert len(periods) == expected_count, f"expected {expected_count} periods, got {len(periods)}"
    seen_ranges: list[tuple[datetime, datetime]] = []
    expected_candle_count = _period_candle_count(period_days)

    for idx, period in enumerate(periods):
        assert period["period_days"] == period_days
        assert len(period["candles"]) == expected_candle_count, (
            f"period {period.get('period_id')} has {len(period['candles'])} candles; expected {expected_candle_count}"
        )
        assert period["end"] - period["start"] == timedelta(days=period_days), (
            f"period {period.get('period_id')} spans {period['end'] - period['start']} instead of {timedelta(days=period_days)}"
        )
        assert period["start"] == period["candles"][0].interval_start
        assert period["end"] == period["candles"][-1].interval_end
        for other_start, other_end in seen_ranges:
            assert not (period["start"] < other_end and period["end"] > other_start), (
                f"overlapping periods found: {period['period_id']} overlaps with another selected range"
            )
        seen_ranges.append((period["start"], period["end"]))


def _periods_from_windows(candles: list, *, period_days: int, count: int, seed: int) -> list[dict]:
    windows = extract_contiguous_kraken_windows(candles)
    expected_candle_count = _period_candle_count(period_days)
    candidates: list[dict] = []

    for window in windows:
        if len(window) < expected_candle_count:
            continue
        for start_index in range(len(window) - expected_candle_count + 1):
            selected = window[start_index:start_index + expected_candle_count]
            first = selected[0]
            last = selected[-1]
            if last.interval_end - first.interval_start != timedelta(days=period_days):
                continue
            candidates.append({
                "start": first.interval_start,
                "end": last.interval_end,
                "candles": selected,
                "period_days": period_days,
            })

    if len(candidates) < count:
        raise ValueError(
            f"Insufficient eligible {period_days}-day periods: need {count}, found {len(candidates)}."
        )

    rng = random.Random(seed)
    shuffled = sorted(candidates, key=lambda item: item["start"])[:]
    rng.shuffle(shuffled)

    chosen: list[dict] = []
    for item in shuffled:
        if len(chosen) >= count:
            break
        if any(item["start"] < existing["end"] and item["end"] > existing["start"] for existing in chosen):
            continue
        chosen.append({
            **item,
            "period_id": f"{period_days}d-{len(chosen) + 1:02d}",
        })

    if len(chosen) < count:
        raise ValueError(f"Could not select {count} non-overlapping {period_days}-day periods from the dataset.")

    return sorted(chosen, key=lambda item: item["start"])


def sample_periods(*, seed: int, period_days: int, count: int, data_path: str | Path = DATA_PATH) -> list[dict]:
    candles = load_kraken_ohlcv(Path(data_path))
    periods = _periods_from_windows(candles, period_days=period_days, count=count, seed=seed)
    _assert_period_batch(periods, period_days=period_days, expected_count=count)
    return periods


def run_period_batch(*, period_days: int, count: int, seed: int, data_path: str | Path = DATA_PATH) -> list[dict]:
    periods = sample_periods(seed=seed, period_days=period_days, count=count, data_path=data_path)
    results = []
    for period in periods:
        selected = list(period["candles"])
        assert len(selected) == _period_candle_count(period_days)
        result = run_zero_cost_period(selected, period_id=period["period_id"])
        result["period_start_utc"] = period["start"].isoformat()
        result["period_end_utc"] = period["end"].isoformat()
        result["period_days"] = period_days
        result["candles_evaluated"] = len(selected)
        result["selection_seed"] = seed
        _assert_accounting_invariants(result)
        results.append(result)
    _assert_period_batch(periods, period_days=period_days, expected_count=count)
    return results


def _assert_experiment_invariants(payload: dict) -> None:
    for key in ("weekly_runs", "monthly_runs"):
        runs = payload[key]
        assert len(runs) == 10, f"{key} must contain exactly 10 runs; got {len(runs)}"
        for item in runs:
            _assert_accounting_invariants(item)
            assert item["period_days"] in {7, 30}
            assert item["period_end_utc"] > item["period_start_utc"]
            assert item["candles_evaluated"] == _period_candle_count(item["period_days"])

    for name, runs in (("weekly", payload["weekly_runs"]), ("monthly", payload["monthly_runs"])):
        starts = [datetime.fromisoformat(item["period_start_utc"]) for item in runs]
        ends = [datetime.fromisoformat(item["period_end_utc"]) for item in runs]
        for start, end in zip(starts, ends):
            assert end - start == timedelta(days=7 if name == "weekly" else 30)

    for batch_name in ("weekly_summary", "monthly_summary"):
        assert isinstance(payload[batch_name]["median_percentage_return"], float)


def run_full_experiment(*, seed: int = 20261015, data_path: str | Path = DATA_PATH) -> dict:
    weekly = run_period_batch(period_days=7, count=10, seed=seed, data_path=data_path)
    monthly = run_period_batch(period_days=30, count=10, seed=seed + 1, data_path=data_path)

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

    payload = {
        "experiment": {
            "name": "zero_cost_20_period_research",
            "config": {
                "selection_seed": seed,
                "weekly_selection_seed": seed,
                "monthly_selection_seed": seed + 1,
                "periods": [
                    {"type": "weekly", "days": 7, "count": 10},
                    {"type": "monthly", "days": 30, "count": 10},
                ],
                "utc_interval_convention": "interval_start is first candle start; interval_end is final candle interval_end, so the exact span is [start, end) and equals exactly 7 or 30 days",
                "initial_cash_eur": 100.0,
                "transaction_costs_zeroed": True,
                "strategy_rules_preserved": True,
                "notional_eur": 100.0,
                "lookback": 3,
                "hold_period": 3,
                "symbol": "BTC-EUR",
            },
            "data": {
                "dataset_path": str(Path(data_path)),
                "dataset_name": "kraken_btc_eur_5m_ohlcv",
                "market": "BTC-EUR",
                "interval_minutes": 5,
                "continuity_rule": "only contiguous windows used; no gaps bridged or fabricated",
                "raw_sha256": None,
            },
        },
        "weekly_runs": weekly,
        "monthly_runs": monthly,
        "weekly_summary": weekly_summary,
        "monthly_summary": monthly_summary,
    }
    _assert_experiment_invariants(payload)
    return payload


if __name__ == "__main__":
    out_path = Path("reports/kraken_zero_cost_20periods_2026-10-15_fixed.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    result = run_full_experiment()
    out_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote {out_path}")
