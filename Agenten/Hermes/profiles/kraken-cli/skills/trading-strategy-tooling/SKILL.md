---
name: trading-strategy-tooling
description: "Use when building a trading strategy tool for kraken-cli."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [trading, strategy, backtest, indicators, paper-trading, parameters, overfitting, verification]
    related_skills: [grill-me, contract-drift-audit, test-driven-development]
---

# Trading Strategy Tooling

Build the layer that turns market data into orders for a CLI trading backend
(`kraken-cli`): a signal generator, a backtester, a runner, a strategy variant.

The backend's command reference, safety rules, and workspace/session/lab model
live in the repo's own `AGENTS.md` / `CONTEXT.md` — read those there. This skill
is the *strategy layer's* workflow and its traps; it does not restate them.

## When to Use

- "Build a strategy / signal generator / backtester for <pair or indicator>"
- A strategy hunch needs to become runnable code
- Extending or repairing an existing generator or runner
- Deciding whether a strategy result can be trusted at all

Not for: placing or reviewing individual orders, reading account state, or
auditing a contract surface (`contract-drift-audit`).

## Step 0 — Align before building

A strategy is a set of free parameters wearing a hypothesis. If the plan has
unresolved decisions, run `grill-me` first: the interview is where the
parameters get frozen and the discretionary components get cut or mechanised.
Building before that is how a strategy gets overfit to a hunch.

## Procedure

### 1. Freeze every parameter as a REQUIRED argument

Every number that shapes a decision is a CLI argument with **no default** —
pair, interval, indicator periods, multipliers, thresholds, capital, risk per
trade, fee and slippage assumptions. A default is a decision made silently,
and a silently-made decision cannot be audited or re-run against. A missing
parameter must fail loudly, naming the parameter.

The only exception is operational plumbing (`--loop`, `--max-iterations`,
binary path, workspace name) — those are not strategy decisions.

### 2. Mechanise the discretionary components

A component is **deterministic** (fully specified by the data) or
**discretionary** (a human chooses). Discretionary components cannot be
backtested at all, whatever variant is picked:

- indicator values, ATR, SuperTrend — deterministic
- a swing / pivot definition — deterministic *only once the pivot rule is
  fixed*; "ZigZag" with no threshold is a free parameter, not a definition
- Elliott-wave counts, "the trend looks right" — discretionary

For each discretionary component pick exactly one: drop it, reduce it to a
mechanical proxy, or run it as a variant beside the deterministic version. Do
not ask which discretionary variant the user prefers — ask which of those
three.

### 3. Fix the entry type per signal

Entry type decides which fee class the fill lands in, so it belongs to the
strategy definition, not to execution:

- confirmation signals (moving-average cross, SuperTrend flip) → **market
  order**; you want to be in the position, and a resting order adds non-fill
  risk for nothing
- level signals (Fibonacci retracement, support/resistance) → **resting limit
  order at the level**; resting *is* the setup

### 4. Build the generator, verify the math offline

Pure functions for indicators and signals, no I/O. Unit-test them against
hand-computed fixtures before anything touches the market: a wrong ATR or a
look-ahead in ZigZag is invisible inside a P&L number and expensive to find
later. The tests must run with no network and no CLI.

### 5. Run against paper only, then score it

Point the backend at a paper workspace (`KRAKEN_WORKSPACE`), never the real
account. A generator that *can* reach a live account is a generator that
eventually will.

Score the run against criteria fixed **before** the run — the repo's
lab/session loop exists for exactly this. Criteria chosen after seeing the
result are not criteria.

### 6. Quantify the model's bias before trusting any result

The simulated engine is a *taker* model. A strategy whose fills are mostly
resting limit orders is charged more on paper than it would pay live, so the
paper result is pessimistic by roughly:

```
expected resting fills x (fee_rate - your maker rate)
```

Report that number beside the result. A result that is only marginally
profitable with fees on is not a result.

## Pitfalls

1. **Trusting a paper result without pricing the model's bias.** The simulated
   fill model is deliberately simple; the gap between it and live execution is
   a number, not a shrug. Compute it and state it, or the result cannot be
   acted on. See `references/paper-model-quirks.md`.
2. **Defaults as silent decisions.** A defaulted parameter is a choice the user
   never made and cannot audit. If a number shapes a decision, it is required.
3. **Treating a discretionary component as a strategy.** A wave count or a
   hand-drawn level is not reproducible, so it cannot be tested — it can only
   be traded. Drop it, proxy it, or run it as a labelled variant.
4. **Leaving a free parameter unfixed because the indicator name sounds
   precise.** "ZigZag", "swing high", "trend" all hide a rule choice that moves
   the result more than the fee does. Fix the rule and freeze it in the same
   change as the strategy.
5. **Testing the generator against the market instead of the math.** Indicator
   and signal logic is pure and cheap to test offline with hand-computed
   fixtures. Debugging it through a paper run is slow and inconclusive.
6. **Letting the generator reach a live workspace.** Verify the paper-only path
   is the only reachable one, and never point a new or unproven generator at a
   real account — including while "just checking".
7. **Scoring after the fact.** Pre-register the thresholds before the run; the
   backend's lab exists so the goalposts cannot move.
8. **Reporting a single run as a result.** Consistency across runs in different
   conditions is the signal; one run is an anecdote.

## Verification

- [ ] Every strategy parameter is a required argument; no defaults
- [ ] Every discretionary component is dropped, proxied, or labelled as a variant
- [ ] Entry type is fixed per signal and matches the signal's intent
- [ ] Indicator and signal logic has offline unit tests with hand-computed fixtures
- [ ] The generator cannot reach a live workspace
- [ ] Scoring criteria were fixed before the run
- [ ] The model-bias number is computed and reported beside the result

## Support Files

- `references/paper-model-quirks.md` — the simulated execution model: fees,
  fill rules, slippage, and what it cannot represent.
