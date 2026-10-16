# Technical Plan — Box Theory Research

## Status
- Scope: historical research only.
- Active strategy: Box Theory; old strategy runners are not part of the active path.
- Branch: `strategy/box-theory-research`.
- Tests and full historical run: pending execution and evidence review.
- Paper/live/scaling: not authorized.

## Runtime path
```text
Kraken BTC/EUR 5m CSV
  -> OHLCV validation
  -> contiguous segments (gaps are barriers)
  -> complete previous UTC-day box
  -> lower-zone rejection signal
  -> next-candle-open entry candidate
  -> stop/target simulation
  -> gross P&L + explicit fee/spread/slippage scenarios
  -> provenance-rich JSON report
```

Active implementation:
- `tools/hsra/kraken_ohlcv.py`: Kraken OHLCV loading and validation.
- `tools/hsra/ohlcv.py`: shared candle structures and validation primitives.
- `tools/hsra/box_theory.py`: strategy rules, segmentation, trade simulation, and cost scenarios.
- `tools/hsra/box_theory_experiment.py`: CLI, chronological split, provenance, and JSON report.
- `tests/test_box_theory.py`: focused strategy and cost-policy tests.

The legacy shared `tools/hsra/cost.py` model is not used by Box Theory because its latency-to-EUR formula and maker/taker assumptions are not validated for this execution model. Historical strategy code is obsolete; historical reports are retained.

## Cost accounting contract
For each completed trade:
- Quantity = entry notional / entry price.
- Gross P&L = (exit price − entry price) × quantity.
- Record entry and exit notionals separately.
- Each scenario applies fee rate, spread bps, and slippage bps to both entry and exit notionals.
- Net P&L = gross P&L − fees − spread cost − slippage cost.
- `gross_only` is a diagnostic, not executable net P&L.
- `illustrative_taker_spread_slippage` is a configurable, unverified sensitivity case.
- Latency is reported as `not_priced`; no EUR latency charge is silently included.
- No maker fill is inferred from a next-open bar simulation.

## Data and simulation safeguards
- A complete prior UTC day requires all 288 expected 5-minute candles in the same contiguous segment.
- Invalid OHLCV rows fail closed in the loader.
- Missing intervals split segments; duplicate timestamps reject segmented input.
- No state or position crosses a gap or partition.
- Stop-gap exits use the bar open; target-gap exits use the target. If stop and target are both touched within one candle, stop wins.
- Positions open at segment end remain unresolved; no boundary fill is invented.
- Entry/stop/target geometry must satisfy stop < entry < target.
- At most one open position per segment; long-only.

## Verification plan
1. Run `python -m pytest -q tests/test_box_theory.py`.
2. Run the CLI against the actual `data/kraken/XBTEUR_5.csv` to a new report path.
3. Inspect JSON structure, source hash, bounds, segment/partition counts, signals/trades, unresolved positions, and cost scenarios.
4. Independently hand-calculate a trade's gross P&L and each scenario's fees/spread/slippage/net P&L.
5. Confirm latency has no EUR cost and no generic legacy CostModel is called.
6. Run relevant Kraken loader/data-quality tests.
7. Record exact commands, test counts, report path, source hash, and limitations before marking verification complete.

## Acceptance criteria
Focused tests actually pass; the actual report is generated and inspected; cost arithmetic is independently verified; provenance and boundaries are explicit; no look-ahead, gap bridging, duplicate auto-removal, or boundary-crossing state; all results are research-only.

## Known limitations / blockers
- GitHub edits do not execute Python tests or the full dataset runner.
- Illustrative fee/spread/slippage defaults are not verified current exchange data.
- Kraken OHLCV cannot prove Bitvavo execution prices, spread, depth, or fills.
- No latency-to-EUR model has been validated.
- Sample adequacy and final-test interpretation remain open until the actual report is reviewed.
- Paper trading, live orders, and scaling require separate explicit authorization.
