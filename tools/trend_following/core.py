from __future__ import annotations

import math
import statistics
from dataclasses import dataclass
from typing import Sequence


LOOKBACKS: tuple[int, ...] = (5, 10, 20, 30, 60, 90, 150, 250, 360)
VOLATILITY_RETURN_COUNT = 90
MIN_PRIOR_DAILY_BARS = 450
ANNUALIZATION_DAYS = 365.0
VOLATILITY_TARGET = 0.25
SPOT_EXPOSURE_CAP = 1.0
REBALANCE_THRESHOLD = 0.20


@dataclass(frozen=True)
class SubmodelState:
    long: bool = False
    stop: float | None = None


@dataclass(frozen=True)
class StrategyDecision:
    valid: bool
    states: tuple[SubmodelState, ...]
    annualized_volatility: float | None
    target_exposure: float
    state_changed: bool
    reason: str


class TrendStrategyInputError(ValueError):
    """Raised when strategy inputs violate the deterministic core contract."""


def _valid_closes(closes: Sequence[float]) -> bool:
    return all(math.isfinite(value) and value > 0 for value in closes)


def annualized_volatility(closes: Sequence[float]) -> float | None:
    """Sample standard deviation of the trailing 90 close-to-close returns.

    Requires 91 valid closes in one contiguous daily segment. Returns None when
    inputs are insufficient or the result is non-finite.
    """
    if len(closes) < VOLATILITY_RETURN_COUNT + 1:
        return None
    trailing_closes = closes[-(VOLATILITY_RETURN_COUNT + 1):]
    if not _valid_closes(trailing_closes):
        return None
    returns = [
        trailing_closes[index] / trailing_closes[index - 1] - 1.0
        for index in range(1, len(trailing_closes))
    ]
    if not all(math.isfinite(value) for value in returns):
        return None
    value = statistics.stdev(returns) * math.sqrt(ANNUALIZATION_DAYS)
    return value if math.isfinite(value) else None


def update_submodel(
    closes: Sequence[float],
    lookback: int,
    state: SubmodelState,
) -> SubmodelState:
    """Apply one completed daily close to one submodel.

    Channel bounds include the current completed close. Entry uses exact
    equality, as specified; the existing stop is checked before ratcheting.
    """
    if lookback not in LOOKBACKS:
        raise TrendStrategyInputError(f"unsupported_lookback={lookback}")
    if len(closes) < lookback:
        return state
    window = closes[-lookback:]
    if not _valid_closes(window):
        raise TrendStrategyInputError("invalid_or_non_finite_close")
    upper = max(window)
    lower = min(window)
    midpoint = (upper + lower) / 2.0
    close = window[-1]

    if state.long:
        if state.stop is None or not math.isfinite(state.stop):
            raise TrendStrategyInputError("long_state_requires_finite_stop")
        if close <= state.stop:
            return SubmodelState()
        return SubmodelState(long=True, stop=max(state.stop, midpoint))

    if state.stop is not None:
        raise TrendStrategyInputError("flat_state_must_not_have_stop")
    if close == upper:
        return SubmodelState(long=True, stop=midpoint)
    return state


def target_exposure(states: Sequence[SubmodelState], volatility: float | None) -> float:
    """Return mean submodel weight, with zero exposure for invalid volatility."""
    if len(states) != len(LOOKBACKS):
        raise TrendStrategyInputError(f"expected_{len(LOOKBACKS)}_submodels")
    if volatility is None or not math.isfinite(volatility) or volatility <= 0:
        return 0.0
    scale = min(VOLATILITY_TARGET / volatility, SPOT_EXPOSURE_CAP)
    return sum((scale if state.long else 0.0) for state in states) / len(states)


def evaluate_daily_close(
    closes: Sequence[float],
    states: Sequence[SubmodelState] | None = None,
) -> StrategyDecision:
    """Evaluate the current completed daily close using prior contiguous closes.

    closes includes the current completed daily close. At least 450 preceding
    valid daily bars are required before an evaluation is considered valid.
    """
    current_states = tuple(states) if states is not None else tuple(
        SubmodelState() for _ in LOOKBACKS
    )
    if len(current_states) != len(LOOKBACKS):
        raise TrendStrategyInputError(f"expected_{len(LOOKBACKS)}_submodels")
    if any(not math.isfinite(value) or value <= 0 for value in closes):
        raise TrendStrategyInputError("closes_must_be_finite_and_positive")
    if len(closes) - 1 < MIN_PRIOR_DAILY_BARS:
        return StrategyDecision(
            valid=False,
            states=current_states,
            annualized_volatility=None,
            target_exposure=0.0,
            state_changed=False,
            reason="insufficient_prior_daily_bars",
        )

    new_states = tuple(
        update_submodel(closes, lookback, state)
        for lookback, state in zip(LOOKBACKS, current_states)
    )
    volatility = annualized_volatility(closes)
    exposure = target_exposure(new_states, volatility)
    return StrategyDecision(
        valid=True,
        states=new_states,
        annualized_volatility=volatility,
        target_exposure=exposure,
        state_changed=new_states != current_states,
        reason="ok" if volatility is not None and volatility > 0 else "invalid_volatility_target_zero",
    )


def volatility_rebalance_required(target_btc_qty: float, current_btc_qty: float) -> bool:
    """Apply the approved strict >20% current-position-relative rule.

    A zero current position is deliberately excluded from this rule; signal-driven
    state changes and window-boundary initialization are separate triggers.
    """
    if not math.isfinite(target_btc_qty) or not math.isfinite(current_btc_qty):
        raise TrendStrategyInputError("btc_quantities_must_be_finite")
    if target_btc_qty < 0 or current_btc_qty < 0:
        raise TrendStrategyInputError("spot_btc_quantities_must_be_nonnegative")
    if current_btc_qty == 0:
        return False
    return abs(target_btc_qty - current_btc_qty) / abs(current_btc_qty) > REBALANCE_THRESHOLD
