# Delegation

The doctrine the generated lead and worker adapters must carry. Read this when
generating adapters, and when deciding what belongs in each one.

The premise: a repository worked on by one long-context agent and a repository
worked on by a lead plus several cheap subagents need different discipline. A
single self-contained adapter that carries planning, the Before/After gate, and
governance writes turns every subagent that loads it into a project manager.
Splitting by role, not by activity, is what fixes that.

## 1. Roles

**Lead** — the only agent in direct contact with a human. It owns:

- Understanding vague requests and aligning on intent.
- The Before / After gate.
- Architecture and product decisions, and the Decision Gate.
- Task decomposition and worker dispatch.
- Every whole-project build, test suite, and process restart.
- Acceptance of worker output.
- Every write to a governance file: atlas docs, plan files, completed folders,
  daily summaries, architecture decisions.

**Worker** — a delegated subagent. It owns:

- Executing one bounded task contract.
- Searching for the precise code (grep, symbol search, call hierarchy).
- Reading only the atlas files the contract names.
- Making the edit and running only contract-permitted checks.
- Returning one structured report.

A worker never runs the Before / After gate, never writes a plan or summary,
never updates the atlas, never creates dated folders, never widens its own scope,
and never re-opens a design question the lead already settled.

## 2. Role Resolution

Neither Claude Code nor Codex exposes a reliable, stable signal for "am I a
subagent." Do not build correctness on environment sniffing. Resolve the role
from the instructions themselves:

1. **Explicit header wins.** A prompt whose header declares `ROLE: worker` is a
   worker. `ROLE: lead` is a lead.
2. **No header → lead.** Direct conversation with a human is the default, so the
   Before / After gate — the whole point of the human-alignment step — is never
   silently skipped.
3. **Governance write gate (the safety net).** Before writing *any* governance
   file — an atlas doc, `docs/changes/planning/**`, `docs/changes/completed/**`,
   or an Architecture Decisions row — the agent must first answer one question:
   *did my instructions come from a human turn, or from another agent's task
   description?* If from another agent, do not write. Report the needed change
   in the structured report and let the lead write it.

Rule 3 is what makes rule 2 safe. A worker that was dispatched without a header
still behaves like a lead for reasoning, but is blocked at the only place where
a misjudged role does lasting damage — the shared documents.

**Single writer.** For any governance file, exactly one agent writes it. That is
the lead. Two agents appending to the same daily summary is how the summary
becomes wrong.

## 3. Task Contract v1

The lead does not forward chat history or a full spec to a worker. It forwards
a contract. Everything the worker needs, and nothing else.

```markdown
---
ROLE: worker
CONTRACT: atlas/v1
TASK_TYPE: implement        # implement | investigate | review
---

## Goal
<one sentence: what must be true when this is done>

## Context
<3-5 lines the worker cannot derive on its own: the already-diagnosed root
cause, the approach the user chose, the constraint that drove it. Not chat
history, not the index, not a spec dump.>

## Read First
- docs/<project>/<module>.md
<only the module doc(s) that matter. Never the whole index. Never every module
doc. If the worker needs a fact from another module, it asks — it does not
go read the map.>

## Allowed Paths
- src/<area>/**
- tests/<area>/**
<editing anything outside this list is out of scope: stop and report>

## Must Preserve
- <architecture boundary, public API, or contract that must not change>

## Forbidden
- <task-specific bans, on top of the baseline catalogue in §5>

## Acceptance
- <check 1: an exact command, or an observable behaviour>
- <check 2>
- Old behaviour that must not change: <...>

## Verification You May Run
- <scoped commands only, e.g. `pytest tests/auth -q`>
<whole-project build, full suite, dev server, anything binding a port: do not
run — report `verification: deferred-to-lead`>

## Stop And Report If
- The root cause turns out to be outside Allowed Paths.
- The fix requires changing something under Must Preserve.
- Two or more viable approaches differ materially in trade-offs.
```

`Must Preserve` and `Forbidden` are usually free to write: copy them from the
owning module doc's **Do Not Do** and **Known Risks** sections. That is what
those sections are for.

## 4. Concurrency And Shared Resources

**Single-builder rule.** These belong to the lead alone:

- Whole-project build (`dist/`, `build/`, `out/`, `target/`, `.next/`, …).
- The full test suite.
- Dev servers, watchers, and anything that binds a port.
- Databases, migrations, seeded fixtures.
- Dependency installs and lockfile changes; global or cached state.

The lead runs these only when no worker is in flight.

A worker may run only checks confined to its `Allowed Paths` that touch no
shared resource — one scoped test file, a lint or typecheck over changed files.
If a worker judges that only a shared-resource check could verify its change, it
runs nothing and reports `verification: deferred-to-lead`, naming what the lead
must run.

Why: with several workers editing one tree, any worker's full build observes
other workers' half-finished files. The result is a report like "tests failed,
but possibly because another agent was editing" — noise that is worse than no
result, because it cannot be acted on. One authoritative build over the merged
state, after every worker returns, is both more reliable and cheaper than N
unreliable ones.

**Scheduling rule.** The lead dispatches workers concurrently only when their
`Allowed Paths` are disjoint. On overlap: serialize, or cut the task along a
different seam. When in doubt, serial.

A task that needs full-build feedback to make progress ("fix these type errors",
"get the suite green") runs solo — no other worker in flight — and is usually
better kept in the lead.

**Process rule.** Stopping a running dev server or app and rebuilding is
allowed, for the lead, with zero workers in flight. Workers never kill
processes, never restart servers, never install dependencies.

**Escape hatch: worktree.** When paths genuinely must overlap and the work is
large enough to pay for it, the lead may give a worker its own `git worktree`;
the worker then owns its tree's build and tests, and the lead owns the merge.
Do not make this the default — it costs a per-tree dependency install and a
merge step.

## 5. Forbidden Implementation Patterns

Every worker carries this baseline. "Do not patch" is too abstract to enforce;
these are checkable.

- Do not add a special case, hardcoded value, or skipped assertion to make a
  check pass.
- Do not catch and swallow an exception to make a symptom disappear.
- Do not copy existing logic to a second location — find the existing
  abstraction first.
- Do not add a production branch that exists only for tests
  (`if TEST`, `NODE_ENV === 'test'`, …).
- Do not repair an upstream problem at a downstream layer.
- Do not introduce new global state, or a wrapper that adds no capability.
- Do not weaken, delete, or rewrite an existing test to make it pass.
- Do not change a public API, schema, or wire contract unless the contract
  explicitly allows it.
- Do not add a dependency unless the contract explicitly allows it.
- Do not touch files outside `Allowed Paths`.

**Root-cause preflight.** Before editing, the worker answers three questions
internally and puts the answer in one line of its report:

1. What actually causes this, and at which layer?
2. Is there an existing abstraction that already handles it?
3. Will this fix put the same logic in a second place?

If the honest answer to (1) points outside `Allowed Paths`, stop and report —
that is the case the contract's *Stop And Report If* exists for.

## 6. Worker Report Format

Short and structured. The lead reads this instead of re-deriving the work.

```markdown
## Changed
- <file>: <what changed and why — one line each>

## Root Cause
<one or two lines: what caused it, and why this layer is the right place to fix it>

## Verification
- <command> → <result>
- deferred-to-lead: <what the lead still needs to run, and why>

## Risks / Blockers
- <or: none>

## Needs A Decision
- <or: none>
```

No narrative of the exploration. No restating the diff. No self-assessment
paragraphs.

## 7. Acceptance

The lead accepts, returns, or re-cuts the task. Default path costs nothing
extra: the lead already holds the contract and can read the diff itself.

Check, against the contract:

- Does every `Acceptance` item hold?
- Did the diff stay inside `Allowed Paths`?
- Is anything under `Must Preserve` altered?
- Does the diff contain any pattern from §5?
- Does the change address the root cause, or the symptom?
- Is the new code more complex than the problem it solves?
- Do new tests assert real behaviour, or do they encode the implementation's
  mistake?
- Are there side effects the report did not mention?

Then run the authoritative build and test suite, and anything the report marked
`deferred-to-lead`.

**Spend a separate review subagent only when** the change is T2 (irreversible,
cross-module, external API, migration), or the lead wrote the code itself and
wants an independent read. Dispatch it with the same contract plus
`TASK_TYPE: review` — a reviewer is a worker with a read-only goal, so it obeys
the same scope, the same forbidden list, and the same report format. Give it the
stronger model; a weak reviewer confirms whatever it is shown.

## 8. Cost Control

Where the money actually goes, in order:

1. **Cold-start exploration.** A fresh subagent that has to find its way around
   burns more than the edit does. The contract's `Read First` and `Allowed
   Paths` exist to make exploration unnecessary.
2. **Spawn count.** One worker with slightly wider `Allowed Paths` beats three
   workers inside the same module. Split by change boundary, not by file.
3. **Wasted spawns.** A vague contract produces work that has to be redone.
   `Acceptance` is the cheapest insurance in this workflow.
4. **Redundant builds.** §4 replaces N unreliable builds with one reliable one.
5. **Review.** Inline lead review is free; a review subagent is not. Tier it.

Never paste the index, a spec, or chat history into a contract. `Context` is
three to five lines.

Model tiering: cheap model with raised reasoning for workers on bounded tasks;
the strong model for the lead, and for T2 review.
