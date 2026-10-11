from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LiveReadinessChecklist:
    is_spot_only: bool = False
    no_withdrawal_permission: bool = False
    risk_engine_final_authority: bool = False
    emergency_stop_tested: bool = False
    max_notional_eur: float = 0.0
    human_approval: bool = False

    def evaluate(self) -> dict:
        evidence_ok = all(
            [
                self.is_spot_only,
                self.no_withdrawal_permission,
                self.risk_engine_final_authority,
                self.emergency_stop_tested,
                self.max_notional_eur > 0,
            ]
        )

        if not evidence_ok or not self.human_approval:
            return {
                "status": "blocked",
                "reason": "live_test_requires_all_guards_and_human_approval",
                "requires_human_approval": True,
                "live_test_allowed": False,
                "max_notional_eur": self.max_notional_eur,
                "live_test_scope": "spot-only" if self.is_spot_only else "not-approved",
            }

        return {
            "status": "ready",
            "reason": "all_live_test_guards_present",
            "requires_human_approval": False,
            "live_test_allowed": True,
            "max_notional_eur": self.max_notional_eur,
            "live_test_scope": "spot-only",
        }
