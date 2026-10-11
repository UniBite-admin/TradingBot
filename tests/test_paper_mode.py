from tools.hsra.paper import PaperTradingMode


def test_paper_mode_is_non_live_by_design():
    mode = PaperTradingMode(
        balance_eur=100.0,
        live_execution_allowed=False,
        human_approval_required=True,
    )

    result = mode.evaluate_order(symbol="BTC-EUR", notional=10.0, action="buy")

    assert result["status"] == "simulated"
    assert result["live_execution_allowed"] is False
    assert result["simulated_notional"] == 10.0


def test_paper_mode_rejects_nonapproved_exit_to_live_trading():
    mode = PaperTradingMode(
        balance_eur=100.0,
        live_execution_allowed=False,
        human_approval_required=True,
    )

    decision = mode.evaluate_transition(target="live")

    assert decision["status"] == "blocked"
    assert decision["requires_human_approval"] is True
    assert decision["can_transition_to_live"] is False
