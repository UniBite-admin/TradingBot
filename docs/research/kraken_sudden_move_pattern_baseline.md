# Kraken Multi-Pair Sudden-Move Pattern Research Baseline

- **Status:** Approved research direction; detailed event thresholds and acceptance criteria remain to be frozen before outcome analysis.
- **Baseline date:** 2026-10-21
- **Research branch:** `research/kraken-sudden-move-patterns`
- **Data location:** `data/kraken_5/`
- **Research mode:** Historical, read-only, exploratory discovery followed by chronological out-of-sample validation.
- **Authority:** This document records the human-approved scope and research baseline for this separate study. It does not amend or replace `STRATEGY_SPECIFICATION.md`, and it does not change the active BTC/EUR trend-following strategy.

## 1. Human-approved decisions

1. Investigate sudden upward **and** downward price moves across the Kraken 5-minute pair files in `data/kraken_5/`.
2. Test both event-definition families:
   - **Fixed-percentage thresholds:** future price movement exceeds a predeclared percentage threshold.
   - **Volatility-normalized thresholds:** future movement is unusually large relative to volatility estimated using information available before the event.
3. Examine pre-event candle/market features for repeatable signals, rather than merely describing the move after it happened.
4. Keep this research separate from the active BTC/EUR trend-following strategy and all legacy strategy reports. Do not combine their signals, samples, or performance claims.
5. Use the existing Kraken files read-only. Do not repair, drop, rename, overwrite, or regenerate source data as part of this study.
6. Historical research only. This approval does **not** authorize paper trading, real-money orders, exchange integration, or scaling.

## 2. Current inventory and preliminary audit evidence

A read-only helper was run by the user against `data/kraken_5/`. The summarized output reported:

| Item | Observed result |
|---|---:|
| CSV files | 670 |
| Total rows | 43,835,296 |
| Total bytes | 2,422,987,165 |
| Empty files | 0 |
| Single-row files | 1 |
| Median rows per file | 20,970.5 |
| Files flagged for close-to-close moves over 50% | 432 |

The audit also reported filename-derived quote suffixes (not authoritative pair metadata): EUR 649, USD 6, USDC 3, USDT 2, AUD/CAD/CHF/GBP/JPY one each, and five unknown.

**Interpretation limits:**
- The user states that the source files were obtained from Kraken's official site. This study accepts that stated provenance; the goal is not to re-litigate the source.
- The audit helper treated the seven positional fields as timestamp, open, high, low, close, volume, and trade count. That positional mapping was a working hypothesis in the helper, not independently established by the audit itself. Confirm field semantics from the relevant Kraken export documentation only if needed to interpret a feature correctly.
- A greater-than-50% close-to-close change is a review flag, not proof of corruption or a genuine tradable move.
- Sparse history and timestamp gaps are present in some files. They should be measured and reported, not used as an automatic exclusion rule without a predeclared reason.
- The inventory/audit has **not** yet established predictive patterns, statistical significance, or tradability.

Example flagged file from the audit: `WFBEUR_5.csv` had 249 rows and a reported maximum absolute close-to-close return of 94,821.689606%. This is a review case, not a conclusion about its cause.

## 3. Research question

Can information available **before** a sudden move distinguish future upward or downward events from comparable non-event periods, across pairs and across later unseen time periods?

The primary unit of analysis is a pair-specific 5-minute candle sequence. Upward and downward events must be labeled and analyzed separately. No feature may use data from the event's future horizon or later.

## 4. Candidate horizons and event families

Candidate forward horizons are:
- 15 minutes = 3 five-minute candles
- 30 minutes = 6 five-minute candles
- 60 minutes = 12 five-minute candles

These horizons are approved as research candidates, not yet frozen event rules.

For each horizon, compare:
1. Fixed-percentage upward and downward thresholds.
2. Volatility-normalized upward and downward thresholds, with volatility calculated only from prior data.

**Not yet frozen:** exact percentage thresholds, volatility estimator/lookback, event price anchor, whether event size uses close-to-close return or high/low excursion, event overlap/de-duplication rules, and minimum history/liquidity requirements. These must be specified before inspecting comparative test outcomes. Do not silently select them or tune them against the final test period.

## 5. Candidate pre-event features

Only features computed from candles available at the decision time may be used. Candidate families for the discovery phase:

- Recent returns/momentum over explicitly defined prior windows.
- Realized volatility and volatility compression/expansion.
- Volume level and volume change relative to that pair's past.
- Candle body, upper/lower wick, and full range, normalized where appropriate.
- Distance to prior-window highs/lows and recent range boundaries.
- Time-of-day and day-of-week context.
- Broad-market/BTC context only where timestamps align and the required data are available.

This list is a candidate feature inventory, not a claim that any feature predicts events. Exact windows and calculations must be frozen before evaluation.

## 6. Controls and validation

1. Build event labels without using future information in predictors.
2. Compare event windows with non-event control windows from the same pair where practical; define matching rules before examining outcomes.
3. Split data chronologically into discovery/training, validation, and untouched final test periods. Do not randomly mix future and past observations.
4. Address overlapping event horizons and temporal dependence; do not treat highly overlapping observations as independent evidence.
5. Account for multiple testing across many pairs, horizons, thresholds, and features. Report how many hypotheses were tested and use a declared correction or other predeclared control.
6. Report per-pair and cross-pair results so one extreme or dominant pair cannot conceal broad failure. Preserve weak-data cases in the inventory and label their uncertainty.
7. Keep predictive association separate from trading profitability. No profitability claim can be made without a separately specified execution and cost model, including fees, spread, slippage, latency, and liquidity constraints.

## 7. Required reporting

For every frozen experiment, record:
- Dataset/file inventory and exact input selection.
- Event-definition version, horizon, thresholds, anchor, overlap policy, and feature definitions.
- Chronological date boundaries and exclusion/eligibility rules.
- Event counts by direction, pair, and period.
- Baseline event rates and control comparison.
- Effect sizes with uncertainty, multiple-testing treatment, and per-pair dispersion.
- Performance on untouched periods, including failures and limitations.
- Reproducible command, code/version identifier, and report location.

Do not present a discovery-set result as validated evidence. If no candidate passes the predeclared criteria on the untouched test set, report that no candidate passed; do not weaken criteria after seeing results.

## 8. Current phase and next gate

**Current phase:** Research contract/baseline recorded; implementation and event study have not been approved as completed or validated.

**Next gate:** Write and review a compact, explicit event-labeling protocol that fixes the thresholds, price anchor, volatility estimator/lookback, overlap policy, and chronological split before calculating comparative pattern results.

No source data, strategy implementation, authoritative active strategy specification, or trading permissions are changed by this baseline.
