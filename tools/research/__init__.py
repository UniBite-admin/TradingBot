"""Research utilities kept separate from the active BTC/EUR strategy.

This package holds historical, read-only investigations such as the
Kraken sudden-move pattern baseline. It must not affect the live strategy
implementation or trading execution code.
"""

from .kraken_sudden_move import (
    benjamini_hochberg,
    build_event_labels,
    compute_chronological_split,
    deterministic_match_controls,
    moving_block_bootstrap,
    summarize_window_features,
)

__all__ = [
    "benjamini_hochberg",
    "build_event_labels",
    "compute_chronological_split",
    "deterministic_match_controls",
    "moving_block_bootstrap",
    "summarize_window_features",
]
