# SDD ledger - plan: Agenten/Handel/docs/superpowers/plans/2026-10-25-autonome-zweiwochen-optimierung.md

## Preflight conflict scan

| Pair/task | Interface or files | Finding and ruling |
|---|---|---|
| Task 1 -> Task 2 | Kandidat, GateErgebnis, bewertung | Compatible dependency. Task 2 must only consume the gate API defined by Task 1. |
| Task 1 -> Task 3 | GateErgebnis | Compatible dependency; paper isolation and promotion reuse fail-closed gate. |
| Task 2 -> Task 4 | fuehre_zyklus_aus, ZyklusBericht | Compatible dependency; reporting consumes completed cycle. |
| Task 3 -> Task 4 | paper readiness / promotion outcome | Compatible; automation cannot activate until isolated paper path is demonstrably safe. |
| Task 1 self-check | data models/gate tests | Plan leaves schema and numeric thresholds underspecified. Ruling: reject promotion until thresholds are grounded in existing house rules and versioned; unknown thresholds fail closed. |
| Task 2 self-check | adapters/rotation/tests | Insufficient data must produce explicit status and reason; no strategy without adapter can be marked successful. |
| Task 2 adapter review | Discovery-only output is not a measured candidate. Existing trace evaluators require per-format pairing/cost validation; static source parsing is not a technical improvement assessment. Ruling: status unsupported traces as `datenarm`/`nicht_auswertbar`, keep candidate lists empty absent validated paired closed-round evidence, and leave adapter/evaluator implementation explicitly open. |
| Task 3 self-check | worktree/paper isolation | Promotion target and rollback must be paper-only and distinct from shared live-capable worktree. Any unproven isolation blocks. |
| Task 4 self-check | report/automation | Codex heartbeat must not be created before the flow is complete, verified, and existing schedules inventoried. |

## Progress

Task 2 discovery/orchestration is implemented, but Plan Task 2 remains incomplete: no existing evaluation source is yet adapted into promotion-capable strategy candidates, and no before/after technical experiment adapter exists. All traces remain visible with a reason; no runners are invoked. Worktree: C:/Users/faupe/Documents/Handel-trading-hub-design, branch arbeit/trading-hub-design.

### Task 1: complete
Commits: ff381a49, f413412e, ef03365a. Gate-focused tests reported 12/12, then 15/15, then 17/17. Reviewer findings across first two passes: bool round counts, malformed window/candidate/base input exceptions, and invalid drawdown-cap diagnostics; code/tests updated. Controller reviewed latest scoped diff and tests; all findings are covered. No numerical thresholds were invented; family rules stay required inputs.

### Task 2: incomplete
Commits: 07df3d44, 43cc43cf. Discovery/orchestration reads registry and source metadata, keeps strategy and engineering findings separate, and reports unsupported traces explicitly. Eight focused tests reported passing. Per-trace validated journal/cost/OOS adapters and technical before/after experiments remain open as Task 2B; no candidates are generated.

### Task 3: incomplete
Commits: 4eaf0640, dbd64063. Worktree and isolation checks are implemented; candidate registration is append-only, explicitly `aktiviert=False`. Worktree tests 4/4 and paper-registration tests 11/11 reported passing. Runtime activation and end-to-end paper readiness remain open as Task 3B; no pilot was run.

### Task 4: partial
Commit: 3ba5e127. Deterministic report renderer/writer added with no-overwrite behavior. Nine tests are specified but were not executable in this shell because no Linux Python is installed and Windows executables return `Exec format error`. Codex automation tool is not exposed in this session, so the every-14-days heartbeat was not created. No Windows scheduled task was changed.
