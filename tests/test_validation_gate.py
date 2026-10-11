from tools.hsra.gate import ValidationGate


def test_validation_gate_blocks_without_human_approval_or_complete_evidence():
    gate = ValidationGate(
        has_cost_model=True,
        has_risk_engine=True,
        has_ledger=True,
        has_strategy_engine=True,
        has_human_approval=False,
    )

    decision = gate.evaluate_for_paper()

    assert decision["status"] == "blocked"
    assert decision["requires_human_approval"] is True


def test_validation_gate_allows_paper_mode_only_when_evidence_and_approval_match():
    gate = ValidationGate(
        has_cost_model=True,
        has_risk_engine=True,
        has_ledger=True,
        has_strategy_engine=True,
        has_human_approval=True,
    )

    decision = gate.evaluate_for_paper()

    assert decision["status"] == "ready"
    assert decision["paper_mode_allowed"] is True
    assert decision["live_trading_allowed"] is False
