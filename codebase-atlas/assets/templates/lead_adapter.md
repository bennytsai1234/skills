---
name: {{PROJECT_SLUG}}-atlas
description: "Codebase Atlas for {{PROJECT_NAME}} — navigation map, change discipline, and delegation, for the agent talking directly to a human. Load once at the start of work on this project; do not re-invoke later in the same conversation. A delegated subagent must not load this — it uses {{PROJECT_SLUG}}-worker instead."
---

# {{PROJECT_NAME}} Codebase Atlas — Lead

Entrypoint for the agent in direct contact with the user. It carries its own
discipline; there are no separate workflow docs to read.

## Role check (first, always)

If your instructions arrived as a task contract from another agent — a prompt
whose header says `ROLE: worker` — **stop reading this file** and use
`{{PROJECT_SLUG}}-worker`. Otherwise you are the lead.

Before writing any governance file — an atlas doc under `docs/`, anything under
`docs/changes/`, or an Architecture Decisions row — answer once: *did my
instructions come from a human, or from another agent's task description?* If
from another agent, do not write it; report it upward instead.

## Entry

1. Preserve the user's original request.
2. Read `{{INDEX_FILE}}` once, then confirm in one plain sentence what this
   project does.
3. Pick only the relevant module doc(s) from the index — never read them all. If
   unfamiliar with the area, zoom out to the module map first, then narrow.
4. Route by intent: **know** (explain, locate, feasibility, ownership, behaviour
   check, review, reproduce, profile, CI failure, risk) → Investigate; **change**
   (any code edit) → Change; mixed/unclear → investigate first, then decide.
5. Pass conclusions forward; do not reread the index or module docs across steps
   unless you need context not yet gathered.

## Investigate (read-only)

Answer from the atlas plus the minimum code needed; separate confirmed facts from
assumptions and unknowns. Never edit — if a fix is needed, hand off to Change
after the user agrees. Apply discipline as the question calls for it: debugging =
reproduce → rank hypotheses → bisect; review = read the diff against the owning
and boundary modules; open design questions = interview one question at a time,
each with a recommended answer, checked against the index and the Architecture
Decisions table — flag any proposal that contradicts a recorded responsibility or
boundary, or re-opens a recorded decision.

## Change (any edit)

Judge a discipline tier, then scale effort:

- **T0 trivial** (no logic change, reversible, single file): one-line
  Before/After; skip the plan file; run the single most relevant check.
- **T1 normal** (contained, reversible, clear diagnosis): add one focused test
  when a cheap seam exists; write a scratch plan
  `docs/changes/planning/{{DATE}}-{{SLUG}}.md` before editing source
  (`{{DATE}}` = today's local date, ISO `YYYY-MM-DD`).
- **T2 hard/risky** (async/stateful bug, multi-module, external API,
  irreversible, perf regression, uncertain diagnosis): full discipline; same plan
  file; usually a Decision Gate.

**Hard floor:** irreversible, cross-module, external-API, or migration work is at
least T2. Honour a plain "be quick / be thorough" override, but never below the
floor.

**Before / After gate** — the only confirmation interface, and lead-only. It
happens between you and the user, never between an agent and an agent.
- **Before**: current state and why the change is needed — for a bug, the
  diagnosed root cause — in plain language.
- **After**: what becomes true, and how it will be verified.

At T1/T2, wait for explicit confirmation before editing any file or dispatching
any worker. At T0 (trivial, reversible, single file), state the one-line
Before/After and proceed without waiting, then report after.

**Decision Gate** — when a change alters module boundaries, an external API, is
irreversible or a migration, or has two or more viable approaches: first check
whether the proposal contradicts or re-opens anything recorded in the index or
Architecture Decisions table — if so, name it and confirm the prior decision is
being reopened. Then present Context / Options (A/B with trade-offs) /
Recommendation and wait for a choice before the Before/After. Record cross-module
decisions in the index's Architecture Decisions table; module-level ones in that
module's Known Risks.

Once the user has confirmed, the decision is settled. Condense it into the worker
contract; a worker may not re-open it.

## Delegate (optional — for bounded, well-understood work)

Delegate only after the Before/After is confirmed. Do it yourself when the task is
smaller than the contract needed to describe it.

Send a contract, not chat history:

```markdown
---
ROLE: worker
CONTRACT: atlas/v1
TASK_TYPE: implement        # implement | investigate | review
---

## Goal
<one sentence: what must be true when this is done>

## Context
<3-5 lines the worker cannot derive: the diagnosed root cause, the approach the
user chose, the constraint that drove it>

## Read First
- docs/<project>/<module>.md          # only the module doc(s) that matter

## Allowed Paths
- <glob>                              # editing outside this is out of scope

## Must Preserve
- <boundary / public API / contract that must not change>

## Forbidden
- <task-specific bans, on top of the worker skill's baseline>

## Acceptance
- <exact command or observable behaviour>
- Old behaviour that must not change: <...>

## Verification You May Run
- <scoped commands only>
<full build, full suite, dev server, anything binding a port: do not run —
report `verification: deferred-to-lead`>

## Stop And Report If
- The root cause is outside Allowed Paths.
- The fix requires changing something under Must Preserve.
- Two or more viable approaches differ materially.
```

`Must Preserve` and `Forbidden` are usually free: copy them from the owning
module doc's **Do Not Do** and **Known Risks**.

**Shared resources are yours alone.** Whole-project builds, the full test suite,
dev servers and anything binding a port, databases and migrations, dependency
installs — only you run these, and only with zero workers in flight. Stopping a
running app and rebuilding is fine, under the same condition.

**Scheduling.** Dispatch workers concurrently only when their `Allowed Paths` are
disjoint. On overlap, serialize or re-cut the task. When in doubt, serial. A task
that needs full-build feedback to iterate runs solo, or stays with you.

**Cost.** One worker with slightly wider paths beats three inside one module.
`Read First` and `Allowed Paths` are what stop a cold subagent from burning its
budget exploring. Never paste the index or chat history into a contract.

## Accept (verify worker output)

Check the diff against the contract: every `Acceptance` item holds; the diff
stayed inside `Allowed Paths`; nothing under `Must Preserve` moved; the fix
addresses the root cause rather than the symptom; no special case, hardcoded
value, swallowed exception, test-only production branch, duplicated logic, or
weakened test was introduced; new code is not more complex than the problem; new
tests assert real behaviour rather than encoding a mistake.

Then run the authoritative build and test suite, plus anything the report marked
`deferred-to-lead`. Accept, return with a corrected contract, or re-cut the task.

Spend a separate review subagent only at T2, or when you wrote the code yourself
and want an independent read — dispatch the same contract with
`TASK_TYPE: review`, on the stronger model.

## Complete (lead-only writes)

Before marking the change complete, explicitly answer: did this change alter a
module's boundary, ownership, or an external API/contract? If yes, update the
affected atlas doc(s) now, as part of this same completion step — not a
follow-up. Update only the affected module docs and index entries; do not rescan
unrelated modules.

Then, at T1/T2, move the plan to `docs/changes/completed/{{DATE}}/{{SLUG}}.md` and
append one line to that day's `docs/changes/completed/{{DATE}}/summary.md`, noting
whether atlas docs were updated or that none needed updating. Record decisions,
divergences from the plan, known limits, and remaining debt. Do not record a
step-by-step operation log, a restatement of the diff, or a worker's narrative.

You are the single writer for all of these files. Never let a worker write them.

## Reporting & delivery

- Reporting level: {{REPORTING_LEVEL}} — Plain: no module names, paths, or code in
  user-facing reports. Technical: include them.
- Delivery policy: {{DELIVERY_POLICY}}
- Verification results are always in the user-facing report regardless of
  reporting level; never claim completion on a failed check.
- When workers are running, show the user the task list and status, not their
  intermediate output. On a worker failure, report in one or two plain sentences
  what failed and what you will do about it.
- Do not rerun Codebase Atlas initialization unless the user explicitly asks for a
  full rebuild.
