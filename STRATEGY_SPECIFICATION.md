# Strategy Specification — Box Theory

## Status and authority
- **Active strategy:** Box Theory only.
- **State:** research candidate; implementation and profitability are not yet validated by this document.
- **Market scope:** Kraken BTC/EUR historical OHLCV, 5-minute candles, long-only SPOT simulation.
- **Trading permission:** none. Paper trading, live orders, and scaling are not authorized.
- **Parameters:** research defaults, not live-approved settings.

This is the sole authoritative strategy specification. Previous Experiment A, Experiment B, breakout, and zero-cost strategy specifications are obsolete for active development. Their reports remain historical comparison evidence only.

## Research question
Does a deterministic prior-day range rejection strategy show robust positive expectancy on the available historical sample after transparent fee, spread, and slippage sensitivity analysis? No result is presumed.

## Data contract
- Input: Kraken BTC/EUR 5-minute OHLCV under `data/kraken/`.
- Timestamps represent candle interval starts and are interpreted in UTC by the existing Kraken loader.
- Candles must be structurally valid, finite, positive-price OHLC, non-negative volume, aligned to 5-minute boundaries, and correctly ordered.
- Missing intervals split data into independent contiguous segments. Never backfill, synthesize, or bridge missing candles.
- Duplicate timestamps reject segmented input; do not silently deduplicate.
- A prior UTC day is eligible only if all 288 expected 5-minute candles are present within the same contiguous segment.
- Every report records source SHA-256, byte size, candle count, first/last timestamp, and partition bounds.

## Candidate mechanics
Research defaults: `zone_fraction=0.25`, `stop_buffer_bps=5`, `notional_eur=50`, `interval_minutes=5`. These are not optimized or live-approved.

1. For each UTC date, define the box from the previous complete UTC day's candles: `box_low=min(low)`, `box_high=max(high)`, `box_mid=(box_low+box_high)/2`.
2. Define the lower-zone boundary as `zone_high=box_low + zone_fraction*(box_high-box_low)`.
3. After a signal candle completes, create a long candidate only when its low is at or below `zone_high`, its close is strictly above `zone_high`, and its close remains between `box_low` and `box_high`.
4. Enter at the next candle's open. This is a bar-level simulation price, not evidence of an executable fill.
5. Stop is the signal candle low minus the configured buffer in basis points. Target is the previous day's box midpoint.
6. Require `stop < entry < target`; otherwise reject the candidate.
7. Simulate at most one position at a time within each contiguous segment. No short selling.
8. If the exit candle opens at or below stop, exit at that open. If it opens at or above target, exit at target. Otherwise, if stop and target are touched in the same candle, assume stop first.
9. If no exit occurs before the contiguous segment ends, mark the position unresolved/open at segment end. Do not invent a boundary exit.
10. Reset all strategy state at every data gap and every train/validation/test partition boundary.

## Cost model — approved approach
Gross P&L is reported separately from cost scenarios. Box Theory must not use the legacy shared CostModel's EUR latency formula or unverified maker/taker execution assumptions.

- `gross_only`: zero-cost diagnostic baseline, not executable net P&L.
- `illustrative_taker_spread_slippage`: configurable sensitivity case with default assumptions of 0.25% fee per side, 4 bps spread cost per side, and 2 bps slippage per side. These are illustrative assumptions, not verified current Kraken or Bitvavo execution costs.
- Fees, spread, and slippage are calculated separately on entry and exit notionals, then totaled to calculate net P&L.
- Latency is recorded as unpriced uncertainty. No EUR latency cost is added without a validated model.
- No maker scenario is assumed because bar-level fills do not prove maker execution.
- Before any profitability conclusion, verify venue-specific costs, order type, fee tier, spread/depth, and actual fills for the intended venue.

## Chronological evaluation protocol
- Split the validated sorted candle sequence 60% / 20% / 20% into training, validation, and final test by candle index.
- Run each partition independently; no state, daily box, signal, or trade may cross boundaries.
- Current implementation does not tune parameters. Do not describe the defaults as selected or optimized.
- Record exact timestamp bounds and counts for each partition; review boundary behavior and complete-day eligibility.
- Do not use final-test outcomes to select parameters. Any future selection procedure must be documented before final-test evaluation.
- Full-sample results are descriptive only and must not replace final-test results.

## Required output
Every report includes strategy name/version, configuration, source hash and bounds, split protocol, segment counts, signals, trades, exit reasons, unresolved segment-end positions, gross P&L, per-scenario fee/spread/slippage assumptions and costs, net P&L, wins/losses, latency status, and known limitations.

## Acceptance criteria and blockers
1. Execute Box Theory unit tests and review failures.
2. Run the report on the actual Kraken CSV and inspect the full JSON and provenance.
3. Verify cost arithmetic with hand-calculated examples and confirm no latency EUR charge appears.
4. Review data validity, partition boundaries, segment behavior, and unresolved trades.
5. Compare against legacy reports only as context unless a controlled common-protocol comparison is separately approved.
6. Do not progress to paper/live trading or scaling without new evidence and explicit human authorization.

A positive gross or modeled net result alone does not establish profitability. Sample adequacy, execution realism, out-of-sample robustness, and actual venue-cost evidence remain open validation requirements.
