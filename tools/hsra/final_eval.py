from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FinalEvaluationReport:
    historical_ok: bool = False
    validation_ok: bool = False
    paper_ok: bool = False
    live_ok: bool = False
    human_approval: bool = False
    evidence_sufficient: bool = False
    scale_approved: bool = False

    def evaluate(self) -> dict:
        if not self.historical_ok or not self.validation_ok or not self.paper_ok:
            return {
                "status": "blocked",
                "reason": "preconditions_not_met",
                "live_test_allowed": False,
                "scale_allowed": False,
                "requires_human_approval": True,
                "must_not_claim_profitability": True,
            }

        if not self.human_approval or not self.evidence_sufficient:
            return {
                "status": "blocked",
                "reason": "human_approval_and_evidence_required",
                "live_test_allowed": False,
                "scale_allowed": False,
                "requires_human_approval": True,
                "must_not_claim_profitability": True,
            }

        if not self.live_ok:
            return {
                "status": "blocked",
                "reason": "live_test_not_ready",
                "live_test_allowed": False,
                "scale_allowed": False,
                "requires_human_approval": True,
                "must_not_claim_profitability": True,
            }

        if not self.scale_approved:
            return {
                "status": "ready_for_live_test",
                "reason": "live_test_permitted_without_scale",
                "live_test_allowed": True,
                "scale_allowed": False,
                "requires_human_approval": False,
                "must_not_claim_profitability": True,
            }

        return {
            "status": "ready_for_controlled_scale",
            "reason": "all_evidence_and_human_approval_present",
            "live_test_allowed": True,
            "scale_allowed": True,
            "requires_human_approval": False,
            "must_not_claim_profitability": True,
        }
