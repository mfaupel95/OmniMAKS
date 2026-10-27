---
name: contract-drift-audit
description: "Use when a machine contract drifts from its code."
version: 1.1.1
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [contract, drift, audit, catalog, mcp, schema, docs, verification, pin-test]
    related_skills: [codebase-inspection, requesting-code-review, grill-me]
---

# Contract Drift Audit

A project ships a **contract** — a machine-readable catalog, an agent-facing
integration guide, a documented default, a safety annotation — and the
**implementation** drifts from it. The contract is what every consumer reads, so
the drift is silent: nothing fails, the consumer just gets a wrong answer.

This skill audits one contract surface against the implementation it describes,
classifies each gap, repairs it in the direction that makes the error honest, and
pins the result so the next drift fails a test instead of a reader.

## When to Use

- "Do the docs match what this actually does?" / "Is the catalog still accurate?"
- A documented surface (command list, tool list, schema, flag set, default)
  needs verifying against the code
- An error message or doc claims something the implementation contradicts
- Adding a machine-readable contract file to a repo that will have to keep up
  with the code
- Before trusting a contract file for automation: measure it, don't assume it

## Procedure

### 1. Read the contract and enumerate the declared surface

Parse the contract file with a script — do not eyeball it. Get the exact count
and the exact identifiers. Note which fields are load-bearing for consumers
(safety flags, auth requirements, defaults, enumerated values).

```bash
python3 -c "import json; c=json.load(open('agents/tool-catalog.json')); \
print(len(c['commands'])); print(sorted({x['group'] for x in c['commands']}))"
```

### 2. Measure the ACTUAL surface by running the thing

The implementation is the only authority. Where the surface is exposed over a
protocol, drive the protocol — a request/response tool cannot be counted from
source. For an MCP server, speak JSON-RPC over stdio: `initialize`, then
`notifications/initialized`, then `tools/list`. See
`scripts/mcp_tools_probe.py`.

```bash
python3 scripts/mcp_tools_probe.py --command kraken --args mcp -s all
```

**Never infer the exposed surface from the contract file, the source tree, or
`--help` text.** Each of those describes something adjacent to the truth.

### 3. Diff the two sets and classify every gap by reason

Build the set difference in code and count it, per group. A gap with no reason
is not a finding — it is an unfinished audit. Classify:

- **Deliberate and documented** — the code has an explicit exclusion with a
  comment or a clear message. Leave it, record it.
- **Deliberate but silent** — excluded with no reason given. The error message
  is the repair site.
- **Accidental** — a real surface that was never registered. This is the bug.

Find the code's own exclusion table (a `const` listing what is excluded and why)
before deciding a gap is accidental: it is where intent is recorded.

### 4. Sweep the docs for the same claim

The same wrong claim is usually copy-pasted across several files — a guide, a
runtime context file, per-integration skills, a setup skill. Grep for the exact
string rather than reading files one by one:

```bash
grep -rn "<the claimed value>" --include=*.md .
```

Count the hits and fix them all. A doc fix that lands in one of four places is
worse than none: the remaining three keep teaching the wrong value.

If a target doc is a protected agent-instruction file (`AGENTS.md`, `CLAUDE.md`),
the write blocks on an approval card. That card is not delivered on every platform,
and silence is not consent — do not retry the same edit in a loop. Hand the user
the exact one-line change (file, line, old text, new text) and report it as the
one remaining manual step; the guard test will stay red until they apply it, and
that is the correct outcome rather than a reason to keep retrying.

### 5. Distinguish every distinct "default" before fixing one

A doc that says "the default" may describe a different default than the
binary's. Shipped artifacts — marketplace manifests, package metadata,
per-client configs — frequently carry their own deliberately narrower list.
Get the binary's own default from source (the clap `default_value` attribute,
not the `--help` rendering) and check whether each doc claim is about the
binary or about a shipped artifact. Fixing only one leaves the drift in the
other.

### 6. Repair toward the honest error

When a surface is unavailable, the error must name what was requested and why,
not report it as a caller typo. A generic "unknown X" message blames the user
for asking for something that exists.

- Add the excluded thing to the parse/validate path so a mixed request list is
  not rejected outright, then filter it with the same mechanism as the other
  exclusions.
- Keep one table mapping excluded name → reason, so the parser, the filter, and
  the error message cannot drift apart.
- Emit a warning on the diagnostics channel (stderr for a protocol server) when
  a requested surface yields nothing. Silently dropping a request is the
  failure mode that started the audit.

### 7. Pin the derived artifact

A one-off audit decays on the next change. Make the audit a test:

- An asserting test that derives the truth from the implementation and compares
  it to the checked-in artifact (counts, identifiers, and the reason strings —
  an unexplained gap is the failure mode the artifact exists to prevent).
- A `#[ignore]`d regeneration test that rewrites the artifact from the
  implementation, documented with the exact command to run.

Follow the repo's existing pattern: if it already pins contract data with a
test, match its style rather than inventing a parallel mechanism. If the
implementation's own key normalisation is subtle, derive keys through the
implementation's own function — see
`references/mcp-surface-derivation.md` for why string reversal fails.

## Pitfalls

1. **Reversing an identifier transformation by string manipulation.** Tool and
   command names are often built by concatenating parts with a separator,
   which destroys the boundary between them (`group + subcommand` collapsed into
   one underscore-joined string). You cannot invert that reliably. Derive the
   canonical key from the implementation's own normalisation function, or
   better, from the object that already carries the canonical key.
2. **Counting from source or help text.** Both describe intent, not the
   assembled surface. Assemble and measure.
3. **Declaring a gap "hidden" without reading the project's own skills and
   docs.** Projects document their own limitations. Re-deriving a known one
   discredits the audit; the real finding is usually the narrower delta (what
   is documented vs. what the code actually does).
4. **Fixing the docs but not the mechanism.** Correcting a number in a Markdown
   file decays on the next release. The durable fix is the pin test plus the
   honest error path.
5. **Trusting a doc's "default".** See step 5 — there are often two.
6. **Leaving the artifact unverified by the build.** An artifact no test reads
   is documentation with extra steps.
7. **Tripping a pre-existing guard test with the claim you just added.** Repos
   pin their docs with tests, and a guard's heuristic is often coarser than a
   legitimate claim: a test asserting that every `<N> commands` in the docs
   equals the catalog total will read a group-scoped count as a wrong total.
   Before writing a number into a doc, grep the test tree for the pattern that
   guard matches. When the guard rejects a claim, read the set of values it
   *accepts* first (catalog total, dangerous total, each group's size) before
   touching the doc: if the doc's number is one of those, the doc is right and
   the guard's accepted set is stale; if it is none of them, the doc is wrong
   and the guard is telling the truth. When the heuristic is provably coarser
   than honest claims, fix the heuristic — accept any number verifiable
   against the contract — rather than weakening the doc or moving the
   goalposts. Surface the options (fix the doc, fix the heuristic, revert the
   change) with a recommendation: weakening a guard is the user's call, not a
   side effect of your edit.
8. **Inventing a path convention instead of copying the file's own.** Read the
   manifest-directory convention from a sibling test in the same file before
   writing a new one. A bin-first crate's `CARGO_MANIFEST_DIR` is the repo root,
   so `"/../agents/x.json"` resolves one level too high and the test dies with a
   bare `NotFound` — the error names a path, never the mistake.
9. **Calling a deliberate exclusion benign without checking what it exposes.**
   A surface can be excluded or gated for a reason that still hides a hazard.
   When a request/response protocol exposes something that reads or writes local
   state, check whether that state is per-client or global: one state file behind
   a multi-client protocol means every client shares a single account, which is a
   different and usually worse isolation story than the exclusion table records.
10. **Removing the reason an exclusion existed without removing the guard that
    enforces it.** The exclusion table records *why*; the refusal can live
    elsewhere — a guard module, a policy function, a dedicated error variant, a
    test. Once you make the surface actually safe, the stale guard blocks
    precisely the thing you just made safe, and it reads like a deliberate
    design decision rather than leftover. Grep for the error text and the error
    variant, not just the exclusion `const`, and remove the enforcement in the
    same change as the reason.
11. **Flipping a contract flag as if it were a one-line edit.** A safety
    annotation (`dangerous`, `auth_required`, a required flag) is usually pinned
    twice: once as a set in a test, and once as a count restated in prose across
    several docs. Adding one entry fails the pin test *and* every doc that
    restates the total. Grep for the count and for the pinned set before you
    touch a flag; expect to touch the test plus N docs.
12. **Reporting a finding from a probe you never verified isolated.** A probe
    that sets env vars to redirect state (`HOME`, `APPDATA`, `XDG_*`) only works
    if the tool actually honours them — a Windows binary that resolves its
    config dir through a shell known-folder API ignores all three. Prove the
    isolation took effect (the target directory was written, the real one
    untouched) *before* drawing any conclusion, or you will report the tool's
    real-config behaviour as a bug in the isolated path.

## Verification

- [ ] The actual surface was measured by running the thing, not read from source
- [ ] Every gap has a reason; none is unexplained
- [ ] Deliberate exclusions were found in the code's own exclusion table before
      being called accidental
- [ ] All copies of a wrong claim were grepped and fixed, not just the first
- [ ] The binary's own default was read from source, and each "default" claim
      was attributed to the binary or to a shipped artifact
- [ ] The artifact is pinned by a test that fails on drift, with a regeneration path
- [ ] Any number written into a doc was checked against the repo's guard-test
      patterns before the edit landed
- [ ] Path conventions in new tests were copied from a sibling test in the same
      file, not invented
- [ ] Any guard, policy, or error variant enforcing an exclusion was found and
      removed together with the exclusion's reason
- [ ] A changed contract flag was checked against the pinned set test and every
      prose restatement of the count
- [ ] Any probe used to report a finding was verified to actually isolate state

## Support Files

- `scripts/mcp_tools_probe.py` — measure an MCP server's real tool surface over
  stdio.
- `references/mcp-surface-derivation.md` — canonical-key normalisation, why
  tool-name reversal fails, and the exclusion-table pattern.
