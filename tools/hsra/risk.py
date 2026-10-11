from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RiskDecision:
    approved: bool
    reason: str | None = None
    details: dict | None = None


class RiskEngine:
    def __init__(self, *, max_open_exposure: float, max_position_per_symbol: float):
        self.max_open_exposure = max_open_exposure
        self.max_position_per_symbol = max_position_per_symbol

    def evaluate(self, *, symbol: str, proposed_notional: float, current_positions: dict, open_orders: dict) -> dict:
        if proposed_notional <= 0:
            raise ValueError("proposed_notional must be positive")

        current_position = float(current_positions.get(symbol, 0.0))
        open_order = float(open_orders.get(symbol, 0.0))

        if open_order > 0:
            return {"approved": False, "reason": "pending_order_conflict", "details": {"symbol": symbol}}

        if current_position >= self.max_position_per_symbol:
            return {"approved": False, "reason": "position_limit", "details": {"symbol": symbol, "current_position": current_position}}

        if proposed_notional > self.max_open_exposure:
            return {"approved": False, "reason": "exposure_limit", "details": {"symbol": symbol, "proposed_notional": proposed_notional}}

        return {"approved": True, "reason": None, "details": {"symbol": symbol, "current_position": current_position}}
