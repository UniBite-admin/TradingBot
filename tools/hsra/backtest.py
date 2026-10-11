from __future__ import annotations

from dataclasses import dataclass

from .replay import replay_candles
from .strategy import StrategyEngine


@dataclass(frozen=True)
class BacktestConfig:
    symbol: str = "BTC-EUR"
    lookback: int = 3
    interval_minutes: int = 5


class HistoricalBacktestHarness:
    """Replay the bounded historical sample and emit deterministic strategy decisions."""

    def __init__(self, *, symbol: str = "BTC-EUR", lookback: int = 3, interval_minutes: int = 5):
        self.config = BacktestConfig(symbol=symbol, lookback=lookback, interval_minutes=interval_minutes)
        self.engine = StrategyEngine(symbol=symbol, lookback=lookback)

    def run(self, candles, *, current_bar_start=None) -> dict:
        ordered = sorted(candles, key=lambda candle: candle.interval_start)
        replay_steps = replay_candles(ordered, current_bar_start=current_bar_start)
        decisions: list[dict] = []

        if current_bar_start is None:
            decision = self.engine.evaluate(ordered)
            if decision["eligible"]:
                decisions.append(decision)
        else:
            for step in replay_steps:
                decision = self.engine.evaluate(step.completed_candles, current_bar_start=current_bar_start)
                if decision["eligible"]:
                    decisions.append(decision)

        summary = {
            "candles": len(ordered),
            "completed_steps": len(replay_steps),
            "decision_count": len(decisions),
            "symbol": self.config.symbol,
            "lookback": self.config.lookback,
        }
        return {
            "config": {
                "symbol": self.config.symbol,
                "lookback": self.config.lookback,
                "interval_minutes": self.config.interval_minutes,
            },
            "decisions": decisions,
            "summary": summary,
        }
