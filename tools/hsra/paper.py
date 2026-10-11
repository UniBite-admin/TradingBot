from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PaperTradingMode:
    balance_eur: float = 0.0
    live_execution_allowed: bool = False
    human_approval_required: bool = True

    def evaluate_order(self, *, symbol: str, notional: float, action: str) -> dict:
        if notional <= 0:
            raise ValueError("notional must be positive")
        if action not in {"buy", "sell"}:
            raise ValueError("action must be 'buy' or 'sell'")

        simulated_notional = float(notional)
        return {
            "status": "simulated",
            "symbol": symbol,
            "action": action,
            "simulated_notional": simulated_notional,
            "balance_eur": self.balance_eur,
            "live_execution_allowed": self.live_execution_allowed,
            "requires_human_approval": self.human_approval_required,
        }

    def evaluate_transition(self, *, target: str) -> dict:
        if target != "live":
            return {
                "status": "allowed",
                "reason": "non_live_transition_only",
                "requires_human_approval": self.human_approval_required,
                "can_transition_to_live": False,
            }

        if not self.live_execution_allowed and self.human_approval_required:
            return {
                "status": "blocked",
                "reason": "human_approval_required_to_leave_paper_mode",
                "requires_human_approval": True,
                "can_transition_to_live": False,
            }

        return {
            "status": "ready",
            "reason": "paper_mode_transition_approved",
            "requires_human_approval": False,
            "can_transition_to_live": True,
        }
