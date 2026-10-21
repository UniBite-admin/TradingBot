# Kraken Multi-Pair Sudden-Move Pattern Research Baseline

- **Status:** Research scope, initial event labels, and core validation protocol approved; unresolved operational definitions and quantitative acceptance criteria remain blocking gates before outcome analysis.
- **Baseline date:** 2026-10-21
- **Research branch:** `research/kraken-sudden-move-patterns`
- **Data location:** `data/kraken_5/`
- **Research mode:** Historical, read-only, exploratory discovery followed by chronological out-of-sample validation.
- **Authority:** This document records the human-approved scope and research baseline for this separate study. It does not amend or replace `STRATEGY_SPECIFICATION.md`, and it does not change the active BTC/EUR trend-following strategy.

## 1. Human-approved decisions

1. Investigate sudden upward **and** downward price moves across the Kraken 5-minute pair files in `data/kraken_5/`.
2. Compare fixed-percentage and volatility-normalized event definitions over 15-, 30-, and 60-minute horizons.
3. Fixed-percentage thresholds are **±0.5%, ±1%, and ±2%**, measured from the start candle close to the horizon-end close.
4. Volatility-normalized candidate thresholds are **2× and 3× prior 24-hour volatility**, with the estimator and forward-horizon scaling defined in Section 4 below.
5. Label upward and downward events separately. Use only pre-event information for candidate predictors.
6. Keep this research separate from the active BTC/EUR trend-following strategy and all legacy strategy reports. Do not combine their signals, samples, or performance claims.
7. Use the existing Kraken files read-only. Do not repair, drop, rename, overwrite, or regenerate source data as part of this study.
8. Report timestamp gaps and missing candles. For each analysis, exclude only observations whose required past or future candles are missing/invalid under that analysis's frozen window; report exclusion counts and reasons. Do not automatically exclude an entire file.
9. Historical research only. This approval does **not** authorize paper trading, real-money orders, exchange integration, or scaling.

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

## 4. Approved initial event-label parameters

Horizons:
- 15 minutes = 3 five-minute candles
- 30 minutes = 6 five-minute candles
- 60 minutes = 12 five-minute candles

For a candidate start candle at time `t`, define the primary horizon return using the close at `t` and the close exactly 3, 6, or 12 candles later, provided the required sequence is valid under the yet-to-be-frozen gap rule. Label upward and downward directions separately.

Fixed-percentage event candidates for every horizon:
- Upward: horizon return ≥ +0.5%, +1%, or +2%.
- Downward: horizon return ≤ −0.5%, −1%, or −2%.

Volatility-normalized event candidates for every horizon:
- Upward: horizon return ≥ +2× or +3× the prior 24-hour volatility measure.
- Downward: horizon return ≤ −2× or −3× the prior 24-hour volatility measure.
- The volatility estimator and forward-horizon scaling are specified in Section 5. Do not calculate volatility-normalized labels until the remaining return convention, warm-up eligibility, and missing-candle rules are explicitly frozen.

This protocol uses close-to-close horizon return as the primary event measurement. High/low excursion is not part of this approved label definition and must not be substituted into the primary analysis. It may only be added later as a separately documented analysis.

**Still unresolved before event-label calculations:** exact return convention used inside the volatility estimator (simple or log returns); warm-up eligibility; exact gap/missing-candle validity checks; overlap-dependence method; minimum-history and any liquidity eligibility rule; exact chronological calendar boundaries and whether boundaries are shared globally across pairs; control-window matching; exact feature windows; and quantitative acceptance thresholds. Freeze these before inspecting comparative outcomes. Do not tune against the final test period.

## 5. Approved validation protocol and candidate pre-event features

The human approved the following protocol on 2026-10-21:

- **Volatility candidate:** calculate the standard deviation of the prior 288 five-minute close-to-close returns (a trailing 24-hour window), then scale it to 15-, 30-, and 60-minute horizons using square-root-of-time scaling. The precise return convention (simple vs. log returns), warm-up eligibility, and missing-candle rules must still be frozen before labels are computed.
- **Missing data/gaps:** exclude an individual observation from a particular analysis when its required historical or forward candles are missing/invalid; report counts and reasons. Do not silently discard entire files.
- **Overlapping events:** retain otherwise eligible overlapping events. Statistical evaluation must account for temporal dependence; the method must be specified before outcome analysis. Do not count overlapping observations as independent evidence.
- **Chronological split:** allocate 60% to discovery/training, 20% to validation, and 20% to an untouched final test, in chronological order. Exact calendar boundaries and whether the same global boundaries apply across all pairs remain to be frozen before labels/features/results are inspected.
- **Candidate feature families:** prior returns/momentum, realized volatility, volume, candle bodies and wicks, and distance to prior highs/lows. Each feature must use only data available at the event start. Exact windows and calculations remain to be frozen.
- **Evaluation principle:** compare candidate predictors against a declared baseline on the untouched test set, account for multiple testing, and report effect sizes and uncertainty. A concrete numerical definition of “meaningful predictive improvement” and the exact test/statistical procedure remain unresolved and must be frozen before outcome analysis.

These choices define a research protocol, not evidence of predictive power or profitability. They do not authorize trading.

## 6. Controls and validation

1. Build event labels without using future information in predictors.
2. Compare event windows with non-event control windows from the same pair where practical; define matching rules before examining outcomes.
3. Split data chronologically into 60% discovery/training, 20% validation, and 20% untouched final test periods. Exact calendar boundaries and cross-pair boundary policy must be frozen before analysis. Do not randomly mix future and past observations.
4. Address overlapping event horizons and temporal dependence; do not treat highly overlapping observations as independent evidence.
5. Account for multiple testing across many pairs, horizons, thresholds, and features. Report how many hypotheses were tested and use a declared correction or other predeclared control. The correction method and numerical acceptance threshold must be frozen before outcome analysis.
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

**Next gate:** Freeze the remaining definitions listed in Sections 4–6: return convention and warm-up for volatility, exact gap validity checks, overlap-dependence method, minimum-history/liquidity eligibility, chronological calendar boundaries and cross-pair policy, control-window matching, exact feature windows, multiple-testing method, and quantitative acceptance criteria. Do not calculate comparative event or feature outcomes before that gate is satisfied.

No source data, strategy implementation, authoritative active strategy specification, or trading permissions are changed by this baseline.
