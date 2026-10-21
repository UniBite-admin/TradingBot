# Kraken Multi-Pair Sudden-Move Pattern Research Baseline

- **Status:** Research definitions approved for the first historical discovery run. Results remain exploratory until the untouched chronological test and predeclared statistical checks are completed.
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

For a candidate start candle at time `t`, define the primary horizon return using the close at `t` and the close exactly 3, 6, or 12 candles later, provided the required sequence passes the validity rules in Section 5. Label upward and downward directions separately.

Fixed-percentage event candidates for every horizon:
- Upward: horizon return ≥ +0.5%, +1%, or +2%.
- Downward: horizon return ≤ −0.5%, −1%, or −2%.

Volatility-normalized event candidates for every horizon:
- Upward: horizon return ≥ +2× or +3× the prior 24-hour volatility measure.
- Downward: horizon return ≤ −2× or −3× the prior 24-hour volatility measure.
- The volatility estimator and forward-horizon scaling are specified in Section 5.

This protocol uses close-to-close horizon return as the primary event measurement. High/low excursion is not part of this approved label definition and must not be substituted into the primary analysis. It may only be added later as a separately documented analysis.



## 5. Approved validation protocol and candidate pre-event features

The human approved the following protocol on 2026-10-21:

- **Volatility candidate:** use log returns, `ln(close_t / close_(t-1))`. Calculate the sample standard deviation (`ddof=1`) of the previous 288 valid five-minute log returns, excluding the current candle's return. Scale the standard deviation by `sqrt(horizon_candles)` for 3, 6, and 12 candles. The event threshold is `2×` or `3×` this horizon-scaled volatility.
- **Warm-up:** a candidate event time is eligible for volatility-normalized labels and full-window features only after 288 consecutive valid prior five-minute returns are available. Fixed-threshold event counts may be reported separately without volatility warm-up, but their feature comparisons must use the same eligible sample as the corresponding model comparison.
- **Candle validity:** timestamps must be strictly increasing and exactly five minutes apart within a required sequence; timestamps must be parseable and unique. OHLC values must be finite and positive, `high >= max(open, close, low)`, and `low <= min(open, close, high)`; volume and trade count must be finite and non-negative. Do not interpolate or repair source data.
- **Missing data/gaps:** exclude an individual observation from a particular analysis when any required historical or forward candle is missing/invalid; report counts by reason and file. Do not silently discard entire files. A valid forward horizon requires all intervening five-minute candles and the exact endpoint candle.
- **Overlapping events:** retain otherwise eligible overlapping events. Estimate uncertainty with a moving-block bootstrap using 288-candle (24-hour) time blocks, synchronized by UTC time across pairs so common market-wide moves are not treated as independent. Use 2,000 resamples and fixed seed `20261021`; report 95% confidence intervals. Overlapping events are not independent observations.
- **Chronological split:** derive one set of shared UTC calendar boundaries from the minimum and maximum valid timestamps across the complete input inventory: first 60% of elapsed time for discovery/training, next 20% for validation, final 20% for untouched test. Apply the same boundaries to every pair. Do not randomly split rows or move observations between periods.
- **Candidate feature families and windows:** use trailing windows of 3, 6, 12, and 288 five-minute candles, with no current/future horizon data. Momentum is cumulative close-to-close log return over each window; realized volatility is sample standard deviation of log returns; volume is the mean and sum of volume; candle anatomy is body size and upper/lower wick size normalized by close, measured for the latest candle and averaged over 3/6/12 candles; distance to prior highs/lows is the percentage distance from event-start close to the prior-window high/low over 12 and 288 candles. A window must be fully valid under Section 5.
- **Control windows:** for each event definition/horizon, sample non-event controls from the same pair and same chronological partition, with the same horizon and the same prior-volatility quintile. A control must not meet either upward or downward event threshold for that event definition/horizon. Use deterministic 1:1 sampling without replacement and fixed seed `20261021`; report eligible pool counts. If a volatility quintile cannot be estimated in discovery data, mark the control unmatched rather than using future data.
- **Multiple testing:** apply Benjamini–Hochberg false-discovery-rate correction at `q = 0.05` to the full predeclared family of feature × event definition × horizon × direction hypotheses. Derive two-sided p-values from the moving-block-bootstrap null distribution and report raw and adjusted p-values.
- **Statistical acceptance:** a candidate is statistically supported only if the untouched-test effect is in the hypothesized direction, its 95% moving-block-bootstrap confidence interval excludes zero, and its Benjamini–Hochberg adjusted p-value is below 0.05. Always report absolute effect size and relative lift; do not equate statistical significance with practical profitability. No fixed minimum economic effect is asserted by this research protocol.

These choices define a research protocol, not evidence of predictive power or profitability. They do not authorize trading.

## 6. Controls and validation

1. Build event labels without using future information in predictors.
2. Compare event windows with deterministic non-event controls matched by pair, chronological partition, horizon, and prior-volatility quintile, as specified in Section 5.
3. Apply the shared UTC chronological split defined in Section 5: 60% discovery/training, 20% validation, and 20% untouched final test.
4. Address overlapping event horizons with the synchronized 24-hour moving-block bootstrap defined in Section 5; do not treat highly overlapping observations as independent evidence.
5. Account for multiple testing using Benjamini–Hochberg FDR `q = 0.05`; report the hypothesis family and raw/adjusted p-values.
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

**Current phase:** First-run operational definitions frozen. No event labels, comparative outcomes, predictive patterns, or profitability have yet been computed or validated.

**Next step:** Implement the frozen definitions with focused tests, run a read-only input audit, then calculate discovery results. Validation must preserve the untouched final test set and use the acceptance procedure in Section 5. No liquidity filter is applied in this first descriptive study; liquidity constraints belong to a later, separately specified tradability study.

No source data, strategy implementation, authoritative active strategy specification, or trading permissions are changed by this baseline.
