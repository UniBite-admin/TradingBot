from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ValidationGate:
    has_cost_model: bool = False
    has_risk_engine: bool = False
    has_ledger: bool = False
    has_strategy_engine: bool = False
    has_human_approval: bool = False

    def evaluate_for_paper(self) -> dict:
        evidence_ok = all(
            [
                self.has_cost_model,
                self.has_risk_engine,
                self.has_ledger,
                self.has_strategy_engine,
            ]
        )

        if not evidence_ok:
            return {
                "status": "blocked",
                "reason": "missing_validation_evidence",
                "requires_human_approval": True,
                "paper_mode_allowed": False,
                "live_trading_allowed": False,
            }

        if not self.has_human_approval:
            return {
                "status": "blocked",
                "reason": "human_approval_required",
                "requires_human_approval": True,
                "paper_mode_allowed": False,
                "live_trading_allowed": False,
            }

        return {
            "status": "ready",
            "reason": "validation_evidence_and_human_approval_present",
            "requires_human_approval": False,
            "paper_mode_allowed": True,
            "live_trading_allowed": False,
        }
