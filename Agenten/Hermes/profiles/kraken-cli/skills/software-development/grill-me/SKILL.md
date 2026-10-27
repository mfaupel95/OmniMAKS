---
name: grill-me
description: "Adversarial plan interview before implementation."
version: 2.0.0
author: "Rafael Zendron (rafaumeu) + Matt Pocock (mattpocock/skills, grilling) + Hermes Agent"
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [planning, adversarial, interview, decision-tree, pre-implementation, review, alignment]
    related_skills: [requesting-code-review, subagent-driven-development, test-driven-development]
---

# Grill Me

Stress-tests a plan through structured adversarial questioning before any
code is written. Models the plan as a **design tree** — every decision
branches into the decisions that hang off it — and interviews the user in
rounds until every branch is resolved and nothing is silently assumed.

Combines the phase discipline of the original with the frontier-rounds
mechanic from mattpocock/skills' `grilling`.

## When to Use

- User says "grill me", "interview my plan", "stress test this idea"
- Before complex work: auth flows, schema changes, migrations, payments
- A plan has unresolved decisions or seems vague
- Before `subagent-driven-development` decomposition

Do NOT use for existing code (use `requesting-code-review`) or simple one-off
tasks.

## Prerequisites

A plan, a raw idea, or an explicit decision to find one. If the user invokes
this skill with no plan attached, do not stall on a single "what is the
plan?" round — the frontier is empty because the root node is missing.
Recon the environment first (see Opening), then return ONE round whose root
question is the topic, carrying 2-3 concrete candidate topics you found in the
repo with a one-line reason each, plus one meta-question about what success
looks like for this interview. The candidate list is what makes the round
answerable; a bare "what do you want?" is not.

## Opening: Recon Before the First Round

Before Round 1, establish the facts the root question depends on so the first
message carries substance instead of a formality. For a code task: clean/dirty
git state, current HEAD/branch, whether the repo's own docs match what the
code actually does (compare the documented contract — command counts, flags,
safety annotations — against the source), and any open markers. Report those
facts in the reply, then ask. A round that opens with "the docs claim X and
the code does Y" gets answered; one that opens with "so, what's the plan?"
gets a shrug.

## Core Mechanic: Frontier Rounds

Map the plan as a design tree. The **frontier** is every decision whose
prerequisites are already settled — the questions you can ask NOW without
guessing at answers you haven't heard yet.

Work in **rounds**: ask the whole current frontier in one message, numbered,
each question carrying your recommended answer. Then wait. A question whose
answer depends on another question still open in this round belongs to a
LATER round, not this one.

Format each round like so:

```
❓ Q1 — <question title>: <question body, options if relevant>
➡️ Recommendation: <your recommended answer + one-line why>

❓ Q2 — <question title>: <question body>
➡️ Recommendation: <...>
```

Each answer reshapes the tree: settled decisions push the frontier outward
and unblock dependent questions. Recompute the frontier and ask the next
round.

**Facts are your job; decisions are the user's.** When a frontier question
needs a fact from the environment (codebase, filesystem, config, docs), find
it yourself with `search_files` / `read_file` / `terminal` — or dispatch a
subagent via `delegate_task` for a heavy exploration. Never ask the user for
anything you could look up. Don't block on an exploration: only the questions
downstream of it wait; ask the rest of the frontier now.

## Stance

Adversarial applies to the user's *framing* too, not only to the plan. If the
user states a goal, treat it as a claim to be tested: name the assumption
underneath it, say what it costs if it is wrong, and offer the alternative you
would pick instead. End a round with a concrete next step, not a courtesy
close — "waiting for your answer" reads as passivity and invites a non-answer.

## Question Coverage (work these branches into the tree)

**Understanding** — the real goal and boundaries:
- What is the ACTUAL objective? What is explicitly IN and OUT of scope?
- What are the constraints (time, tech, team, budget)? Who are the users?

**Technical decisions** — for each architectural choice:
- "Why this approach and not X?" / "What happens if Y fails?"
- "What's the worst case?" / "How would you roll back?"
- Cross-reference the existing codebase; if the project already has a
  pattern for this, call it out.

**Edge cases:**
- "What happens if the user does Z?" / "What if dependency X goes down?"
- "What if volume is 100x expected?" / "What are the security implications?"

## Synthesis (when the frontier is empty)

1. Summarize ALL decisions in bullet points
2. List anything left open, and what is explicitly OUT of scope
3. Ask: "Aligned? Should I start implementing, or adjust anything?"

Do not act on the plan until the user confirms shared understanding.

The green light covers the whole synthesis, not its first item. When the user
delegates the sequencing ("do what you think is best", "just do it"), state
which workstreams you are starting and in what order — that is the moment a
scope mismatch is cheap to fix. Implement disjoint workstreams in parallel
rather than serially: delegate each to a subagent to keep your own context
compact, keep their file scopes non-overlapping, and verify each independently
before integrating.

## Pitfalls

1. **Asking questions out of dependency order.** A question that depends on
   an unanswered question is a guess wearing a question mark. Keep it for a
   later round.
2. **Skipping the codebase.** Find facts in code with Hermes tools instead of
   asking the user.
3. **Accepting "I don't know" as final.** Suggest options, explain
   trade-offs, make a recommendation. When the user is unsure about a
   *component* of the plan rather than a decision, establish first whether
   that component is **deterministic** — fully specified by the data — or
   discretionary. Determinism, not the user's confidence, decides whether it
   can be tested at all: a discretionary component cannot be backtested
   regardless of which variant they pick, so "which one do you prefer" is the
   wrong question. Reframe it as "do we drop it, reduce it to a mechanical
   proxy, or run it as a variant beside the deterministic version" — that
   gives them a decision they can actually make.
4. **Writing code during the interrogation.** Alignment only — code after the
   explicit green light.
5. **Being too agreeable.** Your job is to find problems. If everything looks
   fine, look harder.
6. **Not adapting to the user's language.** Interview in whatever language
   the user speaks.
7. **Declaring a limitation "hidden" without checking the project's own
   docs first.** A project usually documents its own gaps — in a README, a
   skill, an AGENTS.md, a "known limitations" section. Search for the
   limitation before you present it as a discovery; a re-derived, already
   documented gap costs the user's time and discredits the finding. State the
   precise delta instead: what is documented, what is not, and where they
   disagree. A skill that implies one thing while the code does another is a
   real finding; a limitation the skill already states is not.
8. **Burying a correction of your own earlier claim.** When a later
   measurement contradicts something you said in an earlier round, retract it
   in the next round explicitly — what you claimed, what is actually true,
   and what that changes about the plan. Quietly dropping the wrong claim
   leaves the user reasoning from a premise you no longer hold.
9. **Accepting a partial round.** Users routinely answer some questions and
   skip others. A skipped question is still on the frontier and blocks the
   synthesis — name the skipped ones explicitly and ask them again, rather
   than silently narrowing the plan to whatever was answered.
10. **Reading a green light as narrower than the synthesis.** The synthesis
    lists every workstream the plan produced. "Do what you think is best" or a
    thumbs-up authorises all of them, not the first — the user expects the
    remaining ones done and will have to ask again. When the user delegates
    the sequencing, pick it yourself and say which workstreams are in it;
    leaving some out silently is how a plan ends up half-built. The same
    applies mid-implementation: if the user lists workstreams to run, they
    mean all of them, in parallel where the scopes allow.

## Verification

- [ ] Every question in a round had all its prerequisites already settled
- [ ] Provided a recommendation with each question
- [ ] Explored the codebase for facts instead of asking the user
- [ ] Frontier empty (no branch silently assumed) before synthesizing
- [ ] Produced a clear summary of all decisions and open items
- [ ] Confirmed user alignment before stopping
- [ ] If invoked with no plan, opened with recon facts and a candidate topic list rather than a bare topic question
- [ ] Every "hidden"/"undocumented" claim checked against the project's own docs and skills first
- [ ] No question skipped between rounds — skipped frontier questions were re-asked, not silently dropped
