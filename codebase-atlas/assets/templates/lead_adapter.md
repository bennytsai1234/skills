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
MODEL_TIER: standard        # standard | strong
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

**Write commands for the shell the worker will get.** `Acceptance` and
`Verification You May Run` are run verbatim. One command per line, never an `&&`
chain — Windows PowerShell 5.1 has no `&&`, and a syntax error comes back as a
failed check that never ran. On Windows also skip inline env prefixes
(`NODE_ENV=test cmd`), `2>/dev/null`, and POSIX tools assumed on `PATH`; prefer
the project's own runner (`npm test`, `pytest tests/auth -q`, `dotnet build`),
which behaves the same in every shell. Paths stay relative with forward slashes.

**Model tier.** `implement` and `investigate` run on {{MODEL_TIER_STANDARD}}
(`MODEL_TIER: standard`). A bounded contract with concrete `Acceptance` items
gains almost nothing from a higher reasoning tier and pays for it every token.
Raise to {{MODEL_TIER_STRONG}} (`MODEL_TIER: strong`) in exactly two cases:
`TASK_TYPE: review`, and a contract whose `Stop And Report If` carries two or more
open-ended judgement calls. Never economise on a reviewer — a weak one confirms
whatever it is shown.

**Shared resources are yours alone.** Whole-project builds, the full test suite,
dev servers and anything binding a port, databases and migrations, dependency
installs — only you run these, and only with zero workers in flight. Stopping a
running app and rebuilding is fine, under the same condition.

**Scheduling.** Dispatch workers concurrently only when their `Allowed Paths` are
disjoint. On overlap, serialize or re-cut the task. When in doubt, serial. A task
that needs full-build feedback to iterate runs solo, or stays with you.

## Cost discipline

Every dispatch carries a fixed cold-start price: a fresh worker pays to find its
way around before it changes a line. Four rules keep that price down. They cost
no output quality — none of them removes a check, a test, or a review.

**Do it yourself unless the contract is cheaper than the work.** Before
dispatching, ask whether writing the contract costs more than making the change.
Keep it in-house when the change is one file, when you already know the exact
lines, or when you are applying a review's findings — those are located already,
and a cold worker would pay to re-find them.

**One worker, wider paths.** If one contract's `Allowed Paths` are a subset of
another's, they are one contract: merge them instead of paying two cold starts and
two acceptance rounds. Split by change boundary, never by file.

**While a worker is in flight, do nothing.** No `git status`, no diff inspection,
no progress narration, no speculative reading. A worker that has not reported is
not finished — that is the whole of what checking can tell you, and you know it
already. Polling shows you a half-written tree and re-sends your entire growing
context to buy that non-answer. Wait for the report, or for an explicit request
for a decision. This costs most when work is serialised: your context grows across
the whole run, so every idle turn is dearer than the one before it.

**Keep the contract thin.** Never paste the index, a spec, or chat history into
one; `Context` is three to five lines. `Read First` and `Allowed Paths` are what
stop a cold worker from burning its budget exploring.

## Accept (verify worker output)

Check the diff against the contract: every `Acceptance` item holds; the diff
stayed inside `Allowed Paths`; nothing under `Must Preserve` moved; the fix
addresses the root cause rather than the symptom; no special case, hardcoded
value, swallowed exception, test-only production branch, duplicated logic, or
weakened test was introduced; new code is not more complex than the problem; new
tests assert real behaviour rather than encoding a mistake.

Then run the authoritative build and test suite, plus anything the report marked
`deferred-to-lead`. Run the auto-fixable checks first and on their own —
formatter, linter, anything with a `--fix` — apply what they report, and only then
spend one combined build-and-test pass. Chaining them means a single formatting
nit aborts the run and you pay for the whole suite twice. Accept, return with a
corrected contract, or re-cut the task.

Spend a separate review subagent only at T2, or when you wrote the code yourself
and want an independent read — dispatch the same contract with
`TASK_TYPE: review` and `MODEL_TIER: strong`. Then apply its findings yourself:
they arrive already located, so a fresh worker would only pay to find them again.

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
- When workers are running, show the user the task list and status you already
  hold — do not go looking for either, and do not relay intermediate output. On a
  worker failure, report in one or two plain sentences what failed and what you
  will do about it.
- Do not rerun Codebase Atlas unless the user explicitly asks for one. If they do
  — or if you find the map wrong in modules you did not touch — a **refresh**
  re-scans only the modules that drifted and is what almost every such request
  actually needs; a **rebuild** discards the map and scans everything. Say which
  one you propose and why before spending either.
