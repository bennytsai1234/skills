# Design: Codebase Atlas Two-Workflow Redesign

**Date:** 2026-05-31
**Status:** approved

## Overview

Restructure the atlas that Codebase Atlas generates from **four workflows**
(`understand`, `change`, `validate`, `main`) into **two workflows** split on the
only boundary that carries real risk — read vs write — plus a set of distilled,
self-contained **technique docs** that the workflows pull in on demand.

- **Investigate** (read): merges `understand` + `validate`. Answers "how does it
  work / where / is it correct / why did CI fail / where's the cost / what's the
  risk." Never edits files.
- **Change** (write): every code edit. Opens with a cheap discipline-tier
  judgement, then pulls in the relevant technique docs, gates on Before/After,
  edits, and verifies in proportion to the tier.

The thin router (read the index, confirm the project in one sentence, decide
read vs write) folds into the adapter — there is no standalone `main` workflow.

## Why

Two problems with the current four-workflow design:

1. **`understand` and `validate` are split on a weak axis.** Both are read-only,
   gather context the same way, and report the same way; they differ only in the
   *flavour* of the answer (explanation vs verdict). Splitting them buys no
   mechanical difference — only an extra file and an extra routing decision. The
   boundary that actually carries weight (irreversibility, the Before/After
   human gate, verification, rollback) is **read vs write**.

2. **`change` re-invents disciplines that mature skills already do better.** It
   carries its own inline "Structured Bug Investigation Workflow" and per-type
   verification — duplicating `systematic-debugging` / `diagnose` / `tdd` /
   `verification-before-completion`. And it applies the same heavy preamble to
   every task regardless of size, which is slow and token-expensive for trivial
   work.

## Key Decisions

- **Harvest, don't delegate.** The useful disciplines are distilled (merged)
  from `superpowers` and `mattpocock-skills` into Codebase Atlas's own assets,
  not invoked at runtime. After initialization the target repo is fully
  self-contained: daily work needs neither `superpowers`, `mattpocock-skills`,
  nor `codebase-atlas` installed — only its own `docs/`.
- **Two levels of self-containment.** (1) The Codebase Atlas skill ships the
  distilled technique docs as templates. (2) Initialization copies them into the
  target repo's `docs/` so the generated atlas stands alone.
- **Progressive disclosure.** Workflow docs stay thin; they point to
  `docs/<project>_techniques/*.md` and the agent reads a technique only when the
  task calls for it. No technique content is inlined into the workflow docs.
- **Demote task types to internal parameters.** The old "10 change types / 6
  validate types" become internal hints the agent picks, not separate workflows.
- **Proportionality via discipline tiers.** Change opens by judging a tier:
  - **T0 trivial** (no behaviour-logic change, reversible, single file): no
    debugging/TDD ceremony; one-line Before/After; skip the committed plan; run
    the single most relevant check.
  - **T1 normal** (contained, reversible, clear diagnosis): light path — fix an
    obvious confirmed root cause; add one focused test when a cheap seam exists;
    one-line plan; type-appropriate test subset.
  - **T2 hard/risky** (intermittent/async/stateful bug, multi-module, external
    API, irreversible, perf regression, or self-assessed uncertain diagnosis):
    full discipline; usually triggers the Decision Gate; full verification.
  - **Hard floor:** irreversible / cross-module / external-API / migration work
    is at least T2 regardless — same conditions as the existing Decision Gate.
  - **Control model:** the AI judges the tier automatically; the user can
    override any time with a plain phrase ("be quick" / "be thorough").
- **Before/After exposes the diagnosis.** Before states the current situation
  **and the diagnosed root cause/nature of the problem** in plain language;
  After states what becomes true **and how it will be verified**. This is what
  lets the user catch a shallow or wrong diagnosis. The internal disciplines
  exist precisely to make that diagnosis trustworthy.

## Harvest Set

Four distilled, dependency-free, tool-neutral technique docs. Each merges the
best of its sources and drops cross-file references, marketing, and
environment-specific examples; voice matches Codebase Atlas ("the user",
English default rendered in the working language).

| Technique doc | Distilled from | Serves |
|---|---|---|
| `debugging.md` | superpowers:systematic-debugging (root-cause iron law) + mattpocock:diagnose (feedback-loop-first, ranked falsifiable hypotheses) | Change(bug), Investigate(why-broken / CI failure) |
| `tdd.md` | superpowers:test-driven-development + mattpocock:tdd (vertical tracer-bullet slices; honest "no correct seam" finding) | Change(feature/bugfix) |
| `verification.md` | superpowers:verification-before-completion (evidence before claims) | Change post-edit |
| `code-review.md` | superpowers:requesting-code-review + receiving-code-review | Investigate(review) |

Folded in, not standalone (YAGNI; promote later if they earn it):

- **Refactoring/architecture** — a short distilled note (from
  mattpocock:improve-codebase-architecture: deepening opportunities, deletion
  test, seams) inside the Change workflow's refactor handling.
- **Zoom-out** — a technique inside the Investigate workflow ("unfamiliar with
  an area → go up a layer, map modules/callers first").

## Output Shape (generated atlas, target repo)

```
docs/
  <project>_index.md                  (map — unchanged structure)
  <project>/<module>.md               (module docs — unchanged structure)
  <project>_investigate_workflow.md   (read — new, merges understand+validate)
  <project>_change_workflow.md        (write — slimmed, points to techniques)
  <project>_techniques/
    debugging.md
    tdd.md
    verification.md
    code-review.md
  <project>_adapter.md                (entry — embeds the thin router)
```

The reference-assisted naming (`<project>_<reference>_...`) follows the same
substitution as today.

## Per-File Migration (the Codebase Atlas skill itself)

In-place evolution, not a rewrite.

| File | Action |
|---|---|
| `references/modes.md` | keep |
| `assets/templates/module.md` | keep |
| `assets/templates/change_plan.md` | delete — its fields are inlined into the change workflow's plan step so the generated atlas stays self-contained (no dependency on the skill's assets at daily-use time) |
| `assets/templates/index.md` | modify: workflow links 4→2, add techniques pointer |
| `assets/templates/understand_workflow.md` | rename → `investigate_workflow.md`; merge validate's 6 question types + zoom-out hint |
| `assets/templates/validate_workflow.md` | delete (absorbed) |
| `assets/templates/main_workflow.md` | delete (router → adapter) |
| `assets/templates/change_workflow.md` | modify: remove inline bug-investigation → point to `techniques/debugging.md`; add tier step; unify plan-commit by tier; Before/After-as-diagnosis |
| `assets/templates/adapter.md` | modify: embed thin router |
| `assets/templates/claude_code_adapter.md` | modify: embed thin router |
| `SKILL.md` | modify: Main Workflow steps (four→two + techniques), adapter step, Core Rules wording, When-Not-To-Use |
| `README.md` | modify: What It Creates / Daily Use workflow lists |
| `references/atlas-contract.md` | modify: Output Shape, Workflow Requirements (4→2), new Techniques + tier/proportionality section, Before/After-as-diagnosis |
| `references/quality-checklist.md` | modify: workflow checks 4→2; add technique-doc + tier checks |
| `assets/techniques/{debugging,tdd,verification,code-review}.md` | **new** (distilled) |

## Out Of Scope

- The map itself (index/module templates), `modes.md`, language detection,
  delivery/reporting decisions, Decision Gate philosophy, and the Before/After
  gate as the sole human interface — all preserved.
- Runtime dependency on `superpowers` / `mattpocock-skills` — explicitly
  rejected in favour of harvesting.
- Standalone refactoring / zoom-out technique docs — folded in for now.
