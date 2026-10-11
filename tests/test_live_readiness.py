from tools.hsra.live import LiveReadinessChecklist


def test_live_readiness_blocks_without_spot_only_and_no_withdrawal_guards():
    checklist = LiveReadinessChecklist(
        is_spot_only=True,
        no_withdrawal_permission=False,
        risk_engine_final_authority=True,
        emergency_stop_tested=True,
        max_notional_eur=10.0,
        human_approval=True,
    )

    result = checklist.evaluate()

    assert result["status"] == "blocked"
    assert result["requires_human_approval"] is True
    assert result["live_test_allowed"] is False


def test_live_readiness_allows_tiny_spot_test_only_when_all_guards_hold():
    checklist = LiveReadinessChecklist(
        is_spot_only=True,
        no_withdrawal_permission=True,
        risk_engine_final_authority=True,
        emergency_stop_tested=True,
        max_notional_eur=10.0,
        human_approval=True,
    )

    result = checklist.evaluate()

    assert result["status"] == "ready"
    assert result["live_test_allowed"] is True
    assert result["max_notional_eur"] == 10.0
    assert result["live_test_scope"] == "spot-only"
