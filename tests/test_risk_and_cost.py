import math

import pytest

from tools.hsra.cost import CostModel
from tools.hsra.ledger import Ledger
from tools.hsra.risk import RiskEngine


def test_cost_model_estimates_realistic_trade_costs():
    model = CostModel(
        maker_fee=0.001,
        taker_fee=0.0015,
        spread_bps=4.0,
        slippage_bps=2.0,
        latency_ms=150,
        min_order_eur=10.0,
    )

    result = model.estimate_trade_cost(price=100.0, notional=100.0, side="buy")

    assert result["fee_eur"] > 0
    assert result["spread_eur"] > 0
    assert result["slippage_eur"] > 0
    assert result["latency_cost_eur"] > 0
    assert result["total_cost_eur"] > 0


def test_risk_engine_blocks_over_exposure_and_duplicate_symbol_orders():
    engine = RiskEngine(max_open_exposure=1000.0, max_position_per_symbol=0.5)

    decision1 = engine.evaluate(
        symbol="BTC-EUR",
        proposed_notional=700.0,
        current_positions={"BTC-EUR": 0.4},
        open_orders={"BTC-EUR": 0.0},
    )
    assert decision1["approved"] is True

    decision2 = engine.evaluate(
        symbol="BTC-EUR",
        proposed_notional=700.0,
        current_positions={"BTC-EUR": 0.5},
        open_orders={"BTC-EUR": 0.0},
    )
    assert decision2["approved"] is False
    assert decision2["reason"] == "position_limit"

    decision3 = engine.evaluate(
        symbol="BTC-EUR",
        proposed_notional=900.0,
        current_positions={"BTC-EUR": 0.1},
        open_orders={"BTC-EUR": 0.2},
    )
    assert decision3["approved"] is False
    assert decision3["reason"] == "pending_order_conflict"


def test_ledger_partial_sell_uses_weighted_average_cost_basis():
    ledger = Ledger()

    ledger.record_fill(symbol="BTC-EUR", side="buy", quantity=1.0, price=100.0, fee=0.0, trade_id="b-1")
    ledger.record_fill(symbol="BTC-EUR", side="sell", quantity=0.6, price=110.0, fee=0.0, trade_id="s-1")

    assert ledger.position_qty == pytest.approx(0.4)
    assert ledger.realized_pnl == pytest.approx(6.0)
    assert ledger.cost_basis == pytest.approx(40.0)
    assert ledger.average_cost_basis == pytest.approx(100.0)
    assert ledger.total_fee == pytest.approx(0.0)
    assert len(ledger.trades) == 2


def test_ledger_full_sell_below_cost_basis_records_loss():
    ledger = Ledger()

    ledger.record_fill(symbol="BTC-EUR", side="buy", quantity=1.0, price=100.0, fee=0.0, trade_id="b-1")
    ledger.record_fill(symbol="BTC-EUR", side="sell", quantity=1.0, price=90.0, fee=0.0, trade_id="s-1")

    assert ledger.position_qty == pytest.approx(0.0)
    assert ledger.realized_pnl == pytest.approx(-10.0)
    assert ledger.cost_basis == pytest.approx(0.0)
    assert ledger.average_cost_basis == pytest.approx(0.0)
    assert ledger.total_fee == pytest.approx(0.0)


def test_ledger_partial_sell_with_multiple_buys_uses_weighted_average_cost():
    ledger = Ledger()

    ledger.record_fill(symbol="BTC-EUR", side="buy", quantity=1.0, price=100.0, fee=0.0, trade_id="b-1")
    ledger.record_fill(symbol="BTC-EUR", side="buy", quantity=1.0, price=120.0, fee=0.0, trade_id="b-2")
    ledger.record_fill(symbol="BTC-EUR", side="sell", quantity=1.0, price=130.0, fee=0.0, trade_id="s-1")

    assert ledger.position_qty == pytest.approx(1.0)
    assert ledger.realized_pnl == pytest.approx(20.0)
    assert ledger.cost_basis == pytest.approx(110.0)
    assert ledger.average_cost_basis == pytest.approx(110.0)
    assert ledger.total_fee == pytest.approx(0.0)


def test_ledger_fees_are_accounted_for_exactly_once_on_entry_and_exit():
    ledger = Ledger()

    ledger.record_fill(symbol="BTC-EUR", side="buy", quantity=1.0, price=100.0, fee=2.0, trade_id="b-1")
    ledger.record_fill(symbol="BTC-EUR", side="sell", quantity=0.6, price=110.0, fee=3.0, trade_id="s-1")

    assert ledger.position_qty == pytest.approx(0.4)
    assert ledger.realized_pnl == pytest.approx(1.8)
    assert ledger.cost_basis == pytest.approx(40.8)
    assert ledger.average_cost_basis == pytest.approx(102.0)
    assert ledger.total_fee == pytest.approx(5.0)


def test_ledger_complete_closure_after_partial_sale_matches_weighted_average_policy():
    ledger = Ledger()

    ledger.record_fill(symbol="BTC-EUR", side="buy", quantity=1.0, price=100.0, fee=1.0, trade_id="b-1")
    ledger.record_fill(symbol="BTC-EUR", side="sell", quantity=0.5, price=120.0, fee=0.5, trade_id="s-1")

    assert ledger.realized_pnl == pytest.approx(9.0)
    assert ledger.position_qty == pytest.approx(0.5)
    assert ledger.cost_basis == pytest.approx(50.5)
    assert ledger.total_fee == pytest.approx(1.5)

    ledger.record_fill(symbol="BTC-EUR", side="sell", quantity=0.5, price=110.0, fee=0.5, trade_id="s-2")

    assert ledger.realized_pnl == pytest.approx(13.0)
    assert ledger.position_qty == pytest.approx(0.0)
    assert ledger.cost_basis == pytest.approx(0.0)
    assert ledger.total_fee == pytest.approx(2.0)
    assert [trade.trade_id for trade in ledger.trades] == ["b-1", "s-1", "s-2"]


def test_ledger_rejects_oversell_without_mutating_state():
    ledger = Ledger()

    ledger.record_fill(symbol="BTC-EUR", side="buy", quantity=1.0, price=100.0, fee=0.0, trade_id="b-1")
    before = ledger.snapshot()

    with pytest.raises(ValueError, match="sell quantity exceeds available position"):
        ledger.record_fill(symbol="BTC-EUR", side="sell", quantity=1.1, price=110.0, fee=0.0, trade_id="s-1")

    assert ledger.snapshot() == before


def test_ledger_rejects_invalid_fill_values_without_mutating_state():
    ledger = Ledger()
    before = ledger.snapshot()

    with pytest.raises(ValueError, match="quantity must be a positive finite number"):
        ledger.record_fill(symbol="BTC-EUR", side="buy", quantity=0.0, price=100.0, fee=0.0, trade_id="b-1")

    with pytest.raises(ValueError, match="price must be a positive finite number"):
        ledger.record_fill(symbol="BTC-EUR", side="buy", quantity=1.0, price=float("nan"), fee=0.0, trade_id="b-2")

    with pytest.raises(ValueError, match="fee must be a finite non-negative number"):
        ledger.record_fill(symbol="BTC-EUR", side="buy", quantity=1.0, price=100.0, fee=-1.0, trade_id="b-3")

    assert ledger.snapshot() == before


def test_ledger_tracks_trade_history_and_realized_pnl():
    ledger = Ledger()

    ledger.record_fill(
        symbol="BTC-EUR",
        side="buy",
        quantity=0.5,
        price=100.0,
        fee=0.1,
        trade_id="t-1",
    )
    ledger.record_fill(
        symbol="BTC-EUR",
        side="sell",
        quantity=0.5,
        price=105.0,
        fee=0.12,
        trade_id="t-2",
    )

    assert ledger.position_qty == pytest.approx(0.0)
    assert ledger.realized_pnl == pytest.approx(2.28)
    assert ledger.total_fee == pytest.approx(0.22)
    assert ledger.cost_basis == pytest.approx(0.0)
    assert len(ledger.trades) == 2
