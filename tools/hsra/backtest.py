from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path

from .cost import CostModel
from .ledger import Ledger
from .replay import ReplayError, replay_candles
from .risk import RiskEngine
from .strategy import StrategyEngine, evaluate_local_structure_signal


@dataclass(frozen=True)
class BacktestConfig:
    symbol: str = "BTC-EUR"
    lookback: int = 3
    interval_minutes: int = 5
    hold_period: int = 3
    notional_eur: float = 100.0


class HistoricalBacktestHarness:
    """Replay the bounded historical sample and emit deterministic strategy decisions."""

    def __init__(
        self,
        *,
        symbol: str = "BTC-EUR",
        lookback: int = 3,
        interval_minutes: int = 5,
        hold_period: int = 3,
        notional_eur: float = 100.0,
        max_open_exposure: float = 1000.0,
        max_position_per_symbol: float = 1.0,
    ):
        self.config = BacktestConfig(
            symbol=symbol,
            lookback=lookback,
            interval_minutes=interval_minutes,
            hold_period=hold_period,
            notional_eur=notional_eur,
        )
        self.engine = StrategyEngine(symbol=symbol, lookback=lookback)
        self.cost_model = CostModel()
        self.risk_engine = RiskEngine(
            max_open_exposure=max_open_exposure,
            max_position_per_symbol=max_position_per_symbol,
        )

    def _split_contiguous_segments(self, ordered):
        segments: list[list] = []
        current_segment: list = []

        for candle in sorted(ordered, key=lambda item: item.interval_start):
            if not current_segment:
                current_segment = [candle]
                continue

            if candle.interval_start == current_segment[-1].interval_start + timedelta(minutes=self.config.interval_minutes):
                current_segment.append(candle)
            else:
                segments.append(current_segment)
                current_segment = [candle]

        if current_segment:
            segments.append(current_segment)

        return segments

    def _candidate_signals(self, ordered):
        for setup_index in range(self.config.lookback, len(ordered) - 1):
            setup = ordered[setup_index]
            confirmation = ordered[setup_index + 1]
            context = ordered[setup_index - self.config.lookback:setup_index]
            if len(context) < self.config.lookback:
                continue

            prior_low = min(candle.low for candle in context)
            lower_wick = min(setup.open, setup.close) - setup.low
            body = abs(setup.close - setup.open)
            candle_range = setup.high - setup.low
            prev_close_low = context[-1].low

            if not (
                setup.low < prior_low
                and setup.close > prev_close_low
                and lower_wick > body
                and candle_range > 0
                and confirmation.close > setup.high
            ):
                continue

            entry_reference_index = setup_index + 2
            exit_index = entry_reference_index + self.config.hold_period - 1
            if exit_index >= len(ordered):
                continue

            yield {
                "setup_index": setup_index,
                "confirmation_index": setup_index + 1,
                "entry_reference_index": entry_reference_index,
                "entry_reference_time": ordered[entry_reference_index].interval_start,
                "exit_index": exit_index,
                "signal_timestamp": confirmation.interval_end,
                "entry_price": ordered[entry_reference_index].open,
                "exit_price": ordered[exit_index].close,
            }

    def run(self, candles, *, current_bar_start=None) -> dict:
        ordered = sorted(candles, key=lambda candle: candle.interval_start)
        try:
            replay_steps = replay_candles(ordered, current_bar_start=current_bar_start)
        except ReplayError:
            return {
                "config": {
                    "symbol": self.config.symbol,
                    "lookback": self.config.lookback,
                    "interval_minutes": self.config.interval_minutes,
                    "hold_period": self.config.hold_period,
                    "notional_eur": self.config.notional_eur,
                },
                "decisions": [],
                "trades": [],
                "summary": {
                    "candles": len(ordered),
                    "completed_steps": 0,
                    "decision_count": 0,
                    "trade_count": 0,
                    "gross_pnl_eur": 0.0,
                    "net_pnl_eur": 0.0,
                    "symbol": self.config.symbol,
                    "lookback": self.config.lookback,
                    "hold_period": self.config.hold_period,
                    "status": "rejected_gap_in_history",
                },
            }

        decisions: list[dict] = []

        if current_bar_start is None:
            decision = self.engine.evaluate(ordered)
            if decision["eligible"]:
                decisions.append(decision)
        else:
            for step in replay_steps:
                decision = self.engine.evaluate(step.completed_candles, current_bar_start=current_bar_start)
                if decision["eligible"]:
                    decisions.append(decision)

        trades: list[dict] = []
        ledger = Ledger()
        open_trade: dict | None = None
        for signal in self._candidate_signals(ordered):
            if open_trade is not None:
                continue

            entry_price = float(signal["entry_price"])
            if entry_price <= 0:
                continue

            proposed_notional = self.config.notional_eur
            risk = self.risk_engine.evaluate(
                symbol=self.config.symbol,
                proposed_notional=proposed_notional,
                current_positions={self.config.symbol: ledger.position_qty * entry_price},
                open_orders={},
            )
            if not risk["approved"]:
                continue

            quantity = proposed_notional / entry_price
            entry_cost = self.cost_model.estimate_trade_cost(
                price=entry_price,
                notional=proposed_notional,
                side="buy",
            )
            ledger.record_fill(
                symbol=self.config.symbol,
                side="buy",
                quantity=quantity,
                price=entry_price,
                fee=entry_cost["total_cost_eur"],
                trade_id=f"entry-{signal['setup_index']}",
            )

            exit_price = float(signal["exit_price"])
            exit_cost = self.cost_model.estimate_trade_cost(
                price=exit_price,
                notional=proposed_notional,
                side="sell",
            )
            gross_pnl = (exit_price - entry_price) * quantity
            ledger.record_fill(
                symbol=self.config.symbol,
                side="sell",
                quantity=quantity,
                price=exit_price,
                fee=exit_cost["total_cost_eur"],
                trade_id=f"exit-{signal['setup_index']}",
            )

            net_pnl = gross_pnl - entry_cost["total_cost_eur"] - exit_cost["total_cost_eur"]
            open_trade = {
                "setup_index": signal["setup_index"],
                "confirmation_index": signal["confirmation_index"],
                "entry_reference_index": signal["entry_reference_index"],
                "entry_price": entry_price,
                "exit_price": exit_price,
                "gross_pnl_eur": gross_pnl,
                "entry_cost_eur": entry_cost["total_cost_eur"],
                "exit_cost_eur": exit_cost["total_cost_eur"],
                "net_pnl_eur": net_pnl,
                "signal_timestamp": signal["signal_timestamp"].isoformat(),
                "position_qty": quantity,
            }
            trades.append(open_trade)

        summary = {
            "candles": len(ordered),
            "completed_steps": len(replay_steps),
            "decision_count": len(decisions),
            "trade_count": len(trades),
            "gross_pnl_eur": sum(item["gross_pnl_eur"] for item in trades),
            "net_pnl_eur": sum(item["net_pnl_eur"] for item in trades),
            "symbol": self.config.symbol,
            "lookback": self.config.lookback,
            "hold_period": self.config.hold_period,
        }
        return {
            "config": {
                "symbol": self.config.symbol,
                "lookback": self.config.lookback,
                "interval_minutes": self.config.interval_minutes,
                "hold_period": self.config.hold_period,
                "notional_eur": self.config.notional_eur,
            },
            "decisions": decisions,
            "trades": trades,
            "summary": summary,
        }

    def run_segmented(self, candles, *, current_bar_start=None, report_path: str | Path | None = None) -> dict:
        """Run the bounded historical model inside each maximal contiguous 5-minute segment.

        The implementation intentionally keeps each segment independent: no signal, warm-up,
        position, or exit state is carried across a segment boundary, and a non-contiguous run
        is split rather than silently repaired. This preserves the repository contract of fail-
        closed continuous replay while enabling a segment-scoped historical analysis mode.
        """
        ordered = sorted(candles, key=lambda candle: candle.interval_start)
        segments = self._split_contiguous_segments(ordered)

        decisions: list[dict] = []
        trades: list[dict] = []
        segment_results: list[dict] = []
        rejected_segments: list[dict] = []

        for segment_index, segment in enumerate(segments):
            segment_result = {
                "segment_index": segment_index,
                "segment_start": segment[0].interval_start.isoformat() if segment else None,
                "segment_end": segment[-1].interval_end.isoformat() if segment else None,
                "length": len(segment),
                "status": "eligible",
                "reason": None,
                "decision_count": 0,
                "trade_count": 0,
                "gross_pnl_eur": 0.0,
                "net_pnl_eur": 0.0,
                "trades": [],
            }

            try:
                replay_candles(segment, current_bar_start=current_bar_start)
            except ReplayError as exc:
                segment_result["status"] = "rejected_gap_in_history"
                segment_result["reason"] = str(exc)
                rejected_segments.append(segment_result)
                segment_results.append(segment_result)
                continue

            if len(segment) < self.config.lookback + 2:
                segment_result["status"] = "insufficient_history"
                segment_result["reason"] = "missing_context"
                segment_results.append(segment_result)
                continue

            local_decisions: list[dict] = []
            local_trades: list[dict] = []
            ledger = Ledger()

            for signal in self._candidate_signals(segment):
                if signal["exit_index"] >= len(segment):
                    continue

                entry_price = float(signal["entry_price"])
                exit_price = float(signal["exit_price"])
                if entry_price <= 0 or exit_price <= 0:
                    continue

                risk = self.risk_engine.evaluate(
                    symbol=self.config.symbol,
                    proposed_notional=self.config.notional_eur,
                    current_positions={self.config.symbol: ledger.position_qty * entry_price},
                    open_orders={},
                )
                if not risk["approved"]:
                    continue

                quantity = self.config.notional_eur / entry_price
                entry_cost = self.cost_model.estimate_trade_cost(
                    price=entry_price,
                    notional=self.config.notional_eur,
                    side="buy",
                )
                ledger.record_fill(
                    symbol=self.config.symbol,
                    side="buy",
                    quantity=quantity,
                    price=entry_price,
                    fee=entry_cost["total_cost_eur"],
                    trade_id=f"entry-{signal['setup_index']}",
                )

                exit_cost = self.cost_model.estimate_trade_cost(
                    price=exit_price,
                    notional=self.config.notional_eur,
                    side="sell",
                )
                gross_pnl = (exit_price - entry_price) * quantity
                ledger.record_fill(
                    symbol=self.config.symbol,
                    side="sell",
                    quantity=quantity,
                    price=exit_price,
                    fee=exit_cost["total_cost_eur"],
                    trade_id=f"exit-{signal['setup_index']}",
                )

                net_pnl = gross_pnl - entry_cost["total_cost_eur"] - exit_cost["total_cost_eur"]
                trade = {
                    "segment_index": segment_index,
                    "setup_index": signal["setup_index"],
                    "confirmation_index": signal["confirmation_index"],
                    "entry_reference_index": signal["entry_reference_index"],
                    "entry_price": entry_price,
                    "exit_price": exit_price,
                    "gross_pnl_eur": gross_pnl,
                    "entry_cost_eur": entry_cost["total_cost_eur"],
                    "exit_cost_eur": exit_cost["total_cost_eur"],
                    "net_pnl_eur": net_pnl,
                    "signal_timestamp": signal["signal_timestamp"].isoformat(),
                    "position_qty": quantity,
                }
                local_trades.append(trade)
                trades.append(trade)

            decision = self.engine.evaluate(segment)
            if decision["eligible"]:
                local_decisions.append(decision)
                decisions.append(decision)

            segment_result["decision_count"] = len(local_decisions)
            segment_result["trade_count"] = len(local_trades)
            segment_result["gross_pnl_eur"] = sum(item["gross_pnl_eur"] for item in local_trades)
            segment_result["net_pnl_eur"] = sum(item["net_pnl_eur"] for item in local_trades)
            segment_result["trades"] = local_trades
            segment_result["status"] = "eligible" if segment_result["trade_count"] or segment_result["decision_count"] else "eligible_no_trade"
            segment_results.append(segment_result)

        summary = {
            "candles": len(ordered),
            "segment_count": len(segments),
            "segment_lengths": [len(segment) for segment in segments],
            "valid_segments": sum(1 for item in segment_results if item["status"] in {"eligible", "eligible_no_trade"}),
            "rejected_segments": sum(1 for item in segment_results if item["status"] == "rejected_gap_in_history"),
            "decision_count": len(decisions),
            "trade_count": len(trades),
            "gross_pnl_eur": sum(item["gross_pnl_eur"] for item in trades),
            "net_pnl_eur": sum(item["net_pnl_eur"] for item in trades),
            "status": "segmented_historical_research",
            "research_configuration": {
                "lookback": self.config.lookback,
                "hold_period": self.config.hold_period,
                "status": "implemented_research_configuration_not_trade_approved",
            },
            "continuous_replay_status": "fail_closed_on_missing_intervals",
        }

        payload = {
            "config": {
                "symbol": self.config.symbol,
                "lookback": self.config.lookback,
                "interval_minutes": self.config.interval_minutes,
                "hold_period": self.config.hold_period,
                "notional_eur": self.config.notional_eur,
            },
            "summary": summary,
            "segments": segment_results,
            "decisions": decisions,
            "trades": trades,
            "rejected_segments": rejected_segments,
        }

        if report_path is not None:
            report_path = Path(report_path)
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

        return payload
