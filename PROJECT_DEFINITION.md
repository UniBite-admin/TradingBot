# Trading Bot - Project Definition and Governing Principles

## 1. Project Mission

Build a research-driven cryptocurrency trading bot focused on short-term, candlestick-based market analysis and scalping.

The objective is to identify whether a simple, testable trading strategy can generate positive returns after realistic trading costs and execution constraints.

The system must prioritize measurable results, capital protection, reproducibility, and operational reliability over complexity.

## 2. Financial Objective

The initial capital target is EUR 50, with an aspirational goal of reaching EUR 5,000 within 3-7 days.

This is an extremely aggressive 100x return objective, not a guaranteed or assumed achievable outcome. The system must never manipulate research results, weaken risk controls, or claim profitability without sufficient evidence to pursue this target.

If testing shows that the objective is not realistically supported by the evidence, report that conclusion honestly.

## 3. Core Operating Principles

The development and research process follows:

**DATA -> ANALYZE -> TEST -> VALIDATE -> PAPER TRADE -> CONTROLLED LIVE TEST -> EVALUATE -> SCALE**

Each stage must produce verifiable evidence before progressing to the next.

A strategy is not accepted merely because its code runs or a backtest produces a positive result.

## 4. Multi-Asset Market Monitoring

The bot should be designed to monitor multiple cryptocurrency markets concurrently and identify potential trading opportunities.

The intended capabilities include:

- Collecting reliable market data from the selected exchange.
- Processing candlestick data consistently.
- Evaluating eligible assets using the approved strategy.
- Comparing and ranking potential opportunities using documented rules.
- Rejecting opportunities that fail strategy or risk requirements.
- Sending an order only when the required conditions are satisfied and the Risk Engine approves it.

The number of markets, exchange, data sources, and candle intervals must be established in the technical plan rather than silently assumed.

## 5. Candlestick-Based Trading Strategy

The trading strategy will be based on candlestick analysis and must have its own explicit, testable specification.

Every strategy rule must define its inputs, conditions, timing, outputs, and invalidation conditions where applicable.

Strategy development must distinguish between:

- A hypothesis that needs testing.
- A rule that has been specified.
- A rule that has been implemented.
- A rule whose implementation has been verified.
- A strategy whose profitability has been validated.

No strategy rule, indicator, timeframe, threshold, entry condition, exit condition, or parameter may be silently invented or treated as approved.

The strategy specification must be established separately before implementation.

## 6. Deterministic Decision-Making

Trading decisions should primarily use deterministic code and appropriately validated models.

The system must produce traceable decisions with sufficient information to establish:

- Which market data was used.
- Which strategy rules were evaluated.
- Why an opportunity was accepted or rejected.
- Which risk checks were performed.
- Why an order was approved or blocked.
- What execution outcome occurred.

An LLM may assist with research, documentation, code review, and hypothesis generation. AI-generated hypotheses are not evidence of profitability and must not autonomously change live trading rules.

## 7. Risk and Capital Protection

Initial trading scope is **SPOT ONLY**.

The system must not use leverage, margin, futures, or perpetual contracts.

Risk management has final authority over the strategy and any AI-supported decision. A BUY or SELL signal does not guarantee that an order will be placed.

The design must provide for controls covering:

- Maximum position size.
- Risk limits per trade.
- Entry and exit authorization.
- Maximum daily loss.
- Maximum consecutive losses.
- Maximum simultaneous positions.
- Abnormal market conditions.
- Data, network, and exchange API failures.
- Failed, rejected, and partially filled orders.
- An emergency trading stop.

Exact numerical limits must be explicitly specified and approved before they govern live trading.

Exchange API credentials must never have withdrawal permission. Secrets must not be committed to the repository or exposed in logs.

## 8. Research and Validation Standards

All performance claims must be supported by reproducible experiments.

Backtesting and validation must address realistic trading fees, spread, slippage, latency, liquidity, partial fills, failed orders, exchange constraints, and minimum order sizes where relevant.

The research process must prevent look-ahead bias, data leakage, and uncontrolled parameter tuning.

Datasets, strategy versions, configurations, test periods, and evaluation criteria must be recorded so that results can be reproduced.

A strategy that appears profitable only before realistic costs must not be classified as profitable.

The required progression is historical research, backtesting, paper trading, a controlled small live test, and only then consideration of scaling.

## 9. Engineering Principles

Follow these principles:

- **Simplicity before complexity:** implement only what the current research question requires.
- **Correctness before optimization:** understand and verify behavior before improving performance.
- **Inspect before modifying:** review relevant source code, tests, data, and documentation first.
- **Small changes, tight feedback loops:** make focused changes, test them, inspect the results, and continue.
- **Root-cause debugging:** investigate why something failed instead of randomly trying fixes.
- **Evidence over intuition:** measure claims such as profitability, accuracy, and robustness.
- **No premature abstraction:** do not introduce frameworks or infrastructure without a demonstrated need.
- **Verification before completion:** code existing is not proof that it works.

## 10. No-Assumptions Governance

Do not guess, invent, or silently choose undocumented requirements.

When critical information is missing, ambiguous, contradictory, or unsupported by authoritative evidence:

1. State what is known.
2. Identify what is unknown.
3. Explain why the uncertainty matters.
4. State which decision or action is blocked.
5. Ask the human for the required decision.

Do not proceed with a critical decision by disguising an assumption as a recommendation or implementation detail.

The human has final authority over unresolved requirements and important project decisions.

Important approved decisions must be recorded in the project's authoritative documentation. Chat history alone is not the project specification.

## 11. Repository and Documentation Structure

Keep the project simple, organized, and easy to maintain.

Create only the files and directories required by the actual project needs. Maintain one authoritative project definition and one authoritative roadmap.

The repository must make it clear:

- What the system is intended to do.
- Which requirements are approved.
- What has been implemented.
- What has been tested.
- What evidence supports current conclusions.
- What remains incomplete or blocked.

Do not create an agent framework, multi-agent hierarchy, agent orchestration system, or unnecessary governance scaffolding.

Do not introduce duplicate specifications, competing roadmaps, redundant reports, or generated artifacts without a clear purpose.

## 12. Definition of Done

A task is complete only when:

1. The requirement is understood.
2. The implementation matches the approved requirement.
3. Relevant tests have been executed.
4. Actual behavior has been verified.
5. Results and failures have been inspected.
6. Acceptance criteria have been satisfied.
7. Necessary documentation has been updated.
8. The evidence supports the completion claim.

If a critical requirement or acceptance criterion remains unresolved, the task must be reported as incomplete.

## 13. Scope of This Definition

This document defines the project's mission, boundaries, engineering principles, and governance.

It does not approve a specific trading strategy, exchange, market universe, timeframe, indicator, numerical risk limit, execution algorithm, or profitability claim.

Those decisions must be established through the appropriate specification and planning work before implementation.

**Primary objective: Build the simplest reliable system that can test whether a trading strategy has genuine, repeatable positive expectancy after realistic costs. Preserve capital, measure results honestly, and never substitute assumptions for evidence.**