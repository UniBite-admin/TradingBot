from __future__ import annotations

import math
from dataclasses import dataclass

from tools.trend_following.core import TrendStrategyInputError


@dataclass(frozen=True)
class PortfolioState:
    cash_eur: float = 100.0
    btc_qty: float = 0.0
    fees_eur: float = 0.0
    slippage_eur: float = 0.0


@dataclass(frozen=True)
class Execution:
    side: str
    btc_qty: float
    reference_price_eur: float
    fill_price_eur: float
    fill_notional_eur: float
    fee_eur: float
    slippage_eur: float


def marked_equity(state: PortfolioState, mark_price_eur: float) -> float:
    _validate_state(state)
    _positive_finite(mark_price_eur, "mark_price_eur")
    return state.cash_eur + state.btc_qty * mark_price_eur


def rebalance_portfolio(
    state: PortfolioState,
    target_exposure: float,
    reference_price_eur: float,
    *,
    fee_bps_per_side: float = 25.0,
    slippage_bps_per_side: float = 1.5,
) -> tuple[PortfolioState, Execution | None]:
    """Rebalance toward a BTC exposure using adverse slippage and explicit fees.

    Target BTC quantity is based on pre-trade equity marked at the reference
    price. Buys are clipped to the cash available after fee and slippage, so
    cash never becomes negative. BTC is fractional. Fee is charged on fill
    notional; slippage cost is the absolute difference from the reference price.
    """
    _validate_state(state)
    _positive_finite(reference_price_eur, "reference_price_eur")
    if not math.isfinite(target_exposure) or not 0.0 <= target_exposure <= 1.0:
        raise TrendStrategyInputError("target_exposure_must_be_between_zero_and_one")
    for name, value in (
        ("fee_bps_per_side", fee_bps_per_side),
        ("slippage_bps_per_side", slippage_bps_per_side),
    ):
        if not math.isfinite(value) or value < 0:
            raise TrendStrategyInputError(f"{name}_must_be_finite_and_nonnegative")
    fee_rate = fee_bps_per_side / 10_000.0
    slippage_rate = slippage_bps_per_side / 10_000.0
    if slippage_rate >= 1.0:
        raise TrendStrategyInputError("slippage_rate_must_be_less_than_one")

    equity = marked_equity(state, reference_price_eur)
    if equity < 0:
        raise TrendStrategyInputError("portfolio_equity_must_be_nonnegative")
    target_qty = equity * target_exposure / reference_price_eur
    delta = target_qty - state.btc_qty
    if math.isclose(delta, 0.0, rel_tol=0.0, abs_tol=1e-14):
        return state, None

    if delta > 0:
        fill_price = reference_price_eur * (1.0 + slippage_rate)
        affordable_qty = state.cash_eur / (fill_price * (1.0 + fee_rate))
        qty = min(delta, max(0.0, affordable_qty))
        if qty <= 0.0:
            return state, None
        side = "buy"
    else:
        fill_price = reference_price_eur * (1.0 - slippage_rate)
        qty = min(-delta, state.btc_qty)
        if qty <= 0.0:
            return state, None
        side = "sell"

    notional = qty * fill_price
    fee = notional * fee_rate
    slippage_cost = qty * abs(fill_price - reference_price_eur)
    if side == "buy":
        cash = state.cash_eur - notional - fee
        btc = state.btc_qty + qty
        # Avoid a tiny negative residue caused only by floating-point arithmetic.
        if cash < 0.0 and cash > -1e-10:
            cash = 0.0
    else:
        cash = state.cash_eur + notional - fee
        btc = state.btc_qty - qty
        if btc < 0.0 and btc > -1e-12:
            btc = 0.0

    execution = Execution(
        side=side,
        btc_qty=qty,
        reference_price_eur=reference_price_eur,
        fill_price_eur=fill_price,
        fill_notional_eur=notional,
        fee_eur=fee,
        slippage_eur=slippage_cost,
    )
    updated = PortfolioState(
        cash_eur=cash,
        btc_qty=btc,
        fees_eur=state.fees_eur + fee,
        slippage_eur=state.slippage_eur + slippage_cost,
    )
    _validate_state(updated)
    return updated, execution


def _positive_finite(value: float, name: str) -> None:
    if not math.isfinite(value) or value <= 0.0:
        raise TrendStrategyInputError(f"{name}_must_be_finite_and_positive")


def _validate_state(state: PortfolioState) -> None:
    values = (state.cash_eur, state.btc_qty, state.fees_eur, state.slippage_eur)
    if any(not math.isfinite(value) for value in values):
        raise TrendStrategyInputError("portfolio_values_must_be_finite")
    if state.cash_eur < -1e-10 or state.btc_qty < -1e-12:
        raise TrendStrategyInputError("spot_portfolio_quantities_must_be_nonnegative")
    if state.fees_eur < 0.0 or state.slippage_eur < 0.0:
        raise TrendStrategyInputError("cumulative_costs_must_be_nonnegative")
