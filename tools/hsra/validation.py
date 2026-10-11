from __future__ import annotations

from dataclasses import dataclass

from .cost import CostModel


@dataclass
class ValidationReport:
    symbol: str
    gross_pnl_eur: float
    cost_drag_eur: float
    net_pnl_eur: float
    passes_realistic_gate: bool
    status: str


class HistoricalValidationStressRunner:
    """Conservative cost-aware validation layer for historical research only."""

    def __init__(self, *, cost_model: CostModel):
        self.cost_model = cost_model

    def run_signal_stress(self, *, symbol: str, entry_price: float, exit_price: float, notional: float, direction: str) -> dict:
        if entry_price <= 0 or exit_price <= 0:
            raise ValueError("entry_price and exit_price must be positive")
        if notional <= 0:
            raise ValueError("notional must be positive")
        if direction not in {"long", "short"}:
            raise ValueError("direction must be 'long' or 'short'")

        quantity = notional / entry_price
        if direction == "long":
            gross_pnl = (exit_price - entry_price) * quantity
            entry_side = "buy"
            exit_side = "sell"
        else:
            gross_pnl = (entry_price - exit_price) * quantity
            entry_side = "sell"
            exit_side = "buy"

        entry_cost = self.cost_model.estimate_trade_cost(price=entry_price, notional=notional, side=entry_side)
        exit_cost = self.cost_model.estimate_trade_cost(price=exit_price, notional=notional, side=exit_side)
        cost_drag = entry_cost["total_cost_eur"] + exit_cost["total_cost_eur"]
        net_pnl = gross_pnl - cost_drag
        passes = net_pnl > 0

        report = ValidationReport(
            symbol=symbol,
            gross_pnl_eur=gross_pnl,
            cost_drag_eur=cost_drag,
            net_pnl_eur=net_pnl,
            passes_realistic_gate=passes,
            status="pass_under_realistic_costs" if passes else "reject_under_realistic_costs",
        )

        return {
            "symbol": report.symbol,
            "gross_pnl_eur": report.gross_pnl_eur,
            "cost_drag_eur": report.cost_drag_eur,
            "net_pnl_eur": report.net_pnl_eur,
            "passes_realistic_gate": report.passes_realistic_gate,
            "status": report.status,
        }
