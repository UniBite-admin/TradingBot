from tools.hsra.final_eval import FinalEvaluationReport


def test_final_evaluation_rejects_scale_or_live_claims_without_explicit_evidence():
    report = FinalEvaluationReport(
        historical_ok=True,
        validation_ok=True,
        paper_ok=True,
        live_ok=False,
        human_approval=False,
        evidence_sufficient=False,
        scale_approved=False,
    )

    decision = report.evaluate()

    assert decision["status"] == "blocked"
    assert decision["live_test_allowed"] is False
    assert decision["scale_allowed"] is False
    assert decision["must_not_claim_profitability"] is True


def test_final_evaluation_allows_only_honest_small_scale_if_evidence_and_approval_are_present():
    report = FinalEvaluationReport(
        historical_ok=True,
        validation_ok=True,
        paper_ok=True,
        live_ok=True,
        human_approval=True,
        evidence_sufficient=True,
        scale_approved=True,
    )

    decision = report.evaluate()

    assert decision["status"] == "ready_for_controlled_scale"
    assert decision["scale_allowed"] is True
    assert decision["live_test_allowed"] is True
    assert decision["must_not_claim_profitability"] is True
