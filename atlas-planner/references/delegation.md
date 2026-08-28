# Delegation

The doctrine `atlas-planner`, `atlas-relay`, and `atlas-worker` carry between
them. This is the single source of truth for the three-tier loop; the other two
skills point here rather than duplicating it.

The handoff from planning to execution is human-mediated: the lead writes files
and stops, and the human carries one file across. Everything after that — order,
dispatch, acceptance, records — belongs to the relay lead, who is also the
human's window during the batch: mid-course additions are relayed through the
same package unless an allowed execution adjustment changes the route.

A request the human flags as wanting immediate results, with no plan or
acceptance step, does not enter this loop at all — see `atlas-fast`.

## 1. The Loop

```text
Human      → states the need
Lead       1. understand the project and the need
           2. clarify the goal and acceptance evidence
           3. write the task packages
           4. write the dispatch plan, commit and push, hand it to the human
Human      → gives the dispatch plan to the relay lead
Relay      5. read the plan and every package it names
           6. order the work; decide real parallelism
           7. route each package to a GPT subagent or Claude `-p`
Worker     8. explore, implement across files as needed
           9. run the checks that prove acceptance
          10. report with evidence and risks
Relay     11. accept by re-running the decisive checks — or return precise gaps
          12. fill the completion record, archive, summarize, commit and push
          13. run the batch verification, report
          14. run the atlas refresh from the completion records
Human     (optional, any time) → reviews a package or asks the relay for status;
          injects mid-course additions → the relay updates the same package and route as needed
```

Step 4→5 crosses a human, once. Steps 7→8 and 10→11 do not — the relay lead
dispatches and accepts on its own. The relay is the human's window during the
batch: the human may review completed packages, ask for status, and inject
mid-course additions, which the relay relays through the same package and adjusts
the route only under the execution-adjustment rules. If the human injects
nothing, the batch runs to completion on its own — the workflow must be complete
without mid-course input.

## 2. Roles

**Lead (`atlas-planner`)** — the only agent in contact with the human. Runs on
the strongest available model. It owns:

- Understanding vague requests and aligning on intent.
- Reading the atlas and deciding what the change touches.
- Product decisions that cannot be inferred from the repository, and the Decision
  Gate.
- The Before / After gate.
- Diagnosis: reproducing the problem, finding the root cause, proving it.
- Decomposition: cutting the work into packages.
- Writing every task package and the dispatch plan, then committing and pushing
  them.
- Atlas docs and Architecture Decisions rows for work it planned itself.
- Reissuing a specification when the relay escalates a spec defect.

For the current workflow, the lead's default output is specification. Source or
test edits and subagent dispatch belong to the execution tier; this is a current
responsibility boundary, not a permanent statement about what the role can never
do. No size exemption: small fixes like a typo go straight to an execution model
rather than through this workflow — or to `atlas-fast` when the human explicitly
wants to skip ceremony.

The lead may read code, run read-only checks, and re-run a verification whose
result decides acceptance. When one of those fails, it is a gap to return, not
something to fix.

**Relay lead (`atlas-relay`)** — the execution manager, started by the human with
the dispatch plan. Runs on **GPT-5.6-Luna, reasoning Max**. Its current workflow
responsibilities are:

- Reading the dispatch plan and every package it names.
- Execution order within the plan's dependencies, and the real parallelism
  decision.
- GPT dispatch, passed explicitly as
  `{"model": "gpt-5.6-luna", "reasoning_effort": "max"}` — never inherited. The
  field is `reasoning_effort`, not `thinking`; `max` is the top of this model's
  scale (`low` / `medium` / `high` / `xhigh` / `max`).
- Claude frontend execution through `claude --model claude-sonnet-5 -p` from the
  relay's current workspace. A Claude package is run directly by the relay, not
  as a GPT subagent.
- Waiting without interfering (§6).
- Acceptance, by re-running the decisive checks (§9).
- Repairing non-semantic task details and, when the intended outcome is
  unchanged, adjusting execution order, package boundaries, workers, or routes;
  every adjustment is recorded for acceptance.
- Completion records, the completed folder, the daily summary, and the commit and
  push (§10).
- Being the human's window during the batch: status questions and mid-course
  additions are relayed through the same package, with route adjustments governed
  by §6.
- The atlas refresh at batch end, from the completion records (§10).

**Worker (`atlas-worker`)** — an implementation route selected by one task
package. Non-frontend packages run on **GPT-5.6-Luna, reasoning Max** as GPT
subagents. Frontend/UI packages run on **Claude Sonnet 5** through the relay's
`claude -p` invocation. The selected worker route owns:

- Exploring the codebase to find what the change requires. The package names
  starting points; it does not cap what may be read.
- Deciding the implementation from the goal, background, acceptance criteria,
  code, and explicit constraints.
- Editing across as many files as the change needs.
- Adding or extending tests when they are needed to establish acceptance.
- Running the checks needed to establish acceptance — including a whole-project
  build and the full test suite — and fixing relevant failures.
- Reporting with evidence: what was changed, what was run, what came back.

In the current workflow, records and delivery belong to the relay lead, the atlas
and Architecture Decisions to the lead, and the Before / After gate to the
conversation that produced the package. A decision the package settled stays
settled — a worker that thinks one is wrong says so in `Needs A Decision`.

**What this workflow is for.** Work that needs analysis, a plan, several
implementation steps, and acceptance. A typo, a constant, a one-line config
change never enters it — those go straight to an execution model, or to
`atlas-fast` when the human explicitly asks to skip the ceremony. Do not build a
trivial tier to accommodate them.

## 3. Role Resolution

Resolve the role from the instructions, not from the environment:

| Header | Role |
|---|---|
| `ROLE: worker` | Worker — use `atlas-worker` |
| `ROLE: relay-lead`, or handed a dispatch plan | Relay lead — use `atlas-relay` |
| no header, talking to a human | Lead — use `atlas-planner`, so the human-alignment gate is never silently skipped |

**Governance writes** are split by tier. Before writing one, confirm the file
belongs to your tier:

| File | Written by | Committed and pushed by |
|---|---|---|
| Atlas docs (`docs/*_index.md`, `docs/<project>/*.md`) | Lead at init; Relay at batch end | Lead; Relay at batch end |
| Architecture Decisions rows | Lead at init; Relay at batch end | Lead; Relay at batch end |
| `docs/changes/planning/**` — packages, dispatch plans | Lead | Lead, before handover |
| `Completion record` inside a package | Relay lead | Relay lead |
| `docs/changes/completed/**` — archived packages, dispatch plans, `summary.md` | Relay lead | Relay lead |
| Source and tests | Worker (working tree only) | Relay lead |

A worker writes no governance file. A boundary, ownership, or contract change
travels up: worker reports it → relay lead records it → lead writes the atlas.

Both tiers push. The execution tier reads the packages out of the repository, so
unpushed planning files may not be there when it looks.

## 4. The Dispatch Plan — the single entry point

The human hands the relay lead **one file**: the dispatch plan. It names the
packages; the relay lead opens them itself.

A stack of packages handed over by hand loses its ordering the moment one is
forgotten, and every package header says `ROLE: worker` — so a relay lead handed
only packages resolves itself as a worker, and the sequencing tier disappears.
Write a dispatch plan even for a single package.

```markdown
---
ROLE: relay-lead
CONTRACT: atlas/v3
MODEL: GPT-5.6-Luna
REASONING: Max
DELIVERY_POLICY: <no commit | commit only | commit and push>
REPORTING_LEVEL: <plain | technical>
---

# <what this batch achieves>

## Objective
<2-4 lines: what is true when the whole batch is done>

## Task Packages
| # | Package | Route | Goal (one line) |
|---|---|---|---|
| 1 | `docs/changes/planning/{{DATE}}-{{SLUG}}.md` | `gpt-subagent` or `claude-p` | <...> |

## Execution Order
<the dependency graph. Mark which orderings are hard requirements and why.>

## Parallel Groups
<which packages may run at once, and what makes that safe. Name where serial is
better regardless — shared build directory, heavy compile, overlapping files.>

## Shared Verification
<the authoritative check to run after the whole batch, with expected result>

## Completion Protocol
<per §10; anything batch-specific here>
```

Hard ordering is the lead's and may not be reordered. Actual parallelism is the
relay lead's: it may lower it or serialize a group, never raise it.

## 5. Task Package (`atlas/v3`)

The lead writes this to `docs/changes/planning/{{DATE}}-{{SLUG}}.md`. It is both
the plan file and part of what the human hands over — one artifact, not two.

Complete means: a competent agent that has never seen this conversation can read
this file, understand the desired result, find the code, choose an implementation,
and prove the result with evidence.

```markdown
---
ROLE: worker
CONTRACT: atlas/v3
TASK_TYPE: implement        # implement | investigate | review
MODEL: GPT-5.6-Luna         # use Claude Sonnet 5 for frontend/UI packages
EXECUTION_ROUTE: gpt-subagent  # use claude-p for frontend/UI packages
REASONING: Max              # GPT packages only; omit for Claude packages
REPORTING_LEVEL: plain      # plain | technical — from the index, for anything
                             # in the report that surfaces to the human directly
---

## Goal
<one sentence: what must be true when this is done>

## Background
<everything the worker cannot derive on its own — no length limit>

## Acceptance
- <exact command with its expected result, or an observable behaviour>
- <another objectively checkable result>
- <what must not change>

## Constraints (only when needed)
- <a requirement that cannot be inferred from the code or ordinary engineering
  judgement, such as API compatibility, schema ownership, dependency policy,
  component ownership, or deterministic verdict authority>
<omit this section when no explicit constraint exists>

## Starting Points (optional)
- docs/<project>/<module>.md
- <the symbol, route, or entrypoint that may help orient exploration>
<omit this section when no useful pointer is available>

## Evidence
- The actual output for each Acceptance check, pasted rather than summarized.
- The tests and other checks run, plus any remaining risks.

## Completion record
<left empty by the lead; filled in by the relay lead on acceptance — see §10>
```

For a frontend/UI package, use this route metadata instead:

```yaml
MODEL: Claude Sonnet 5
EXECUTION_ROUTE: claude-p
```

Do not add `REASONING` to a Claude package. The relay uses the route metadata to
choose between a GPT subagent and `claude --model claude-sonnet-5 -p`. The route
is the planning tier's initial choice; the relay may revise it or the worker
assignment when an equivalent execution path is needed and the task's intent is
unchanged. It records the before/after and reason.

### Preflight ownership

Preflight is layered, not repeated. The planner avoids obvious contradictions
when writing the package. The relay checks package metadata once; it repairs an
unambiguous non-semantic defect and records the before/after, or reports
`state: blocked` with `blocker: metadata` when the intended value cannot be
determined without changing the task's meaning. After valid or repaired
metadata, the worker performs one lightweight specification preflight before
editing; an obvious contradiction is `state: blocked` with `blocker: spec`.
This is a reasonableness check, not a general-purpose specification parser.

**Background** is what makes the package portable to a model with zero
conversation history, on another platform. No length limit. Include, when they
apply:

- The problem, in enough depth that the goal is obviously the right goal.
- How the current implementation works, with the wrong code quoted.
- Real input against real wrong output — a table beats a paragraph.
- Any inventory the lead already did, marking entries that are "currently correct
  but only by luck", since a worker skips exactly those otherwise.
- Known limits of single-file or single-pass analysis.

Add a constraint only when it records a real requirement that the worker cannot
infer from the repository or ordinary engineering judgement — "preserve existing
functionality", "use a reasonable architecture", or "maintain code quality" are
not requirements.

**Acceptance rules.** Every acceptance item must be checkable by someone who was
not in the conversation — an exact command with an expected result, or an
observable behaviour described precisely enough to disagree with. "Works
correctly" is not an acceptance criterion. Prefer exact expected values over
existence claims. Cover the negative case and say what a negative fixture must
contain. Name what must not change. Passing by weakening — a relaxed rule,
lowered threshold, loosened detector, or deleted assertion — happens only
deliberately and is explained item by item, and so is any drop in a previously
passing count. When an item depends on something that may not exist on the
execution machine, state whether it is skippable or conditional and what
evidence remains required.

**Command rules.** Write commands for the shell the worker will get. One command
per line, never an `&&` chain — Windows PowerShell 5.1 has no `&&`. On a Windows
host also avoid inline environment prefixes (`NODE_ENV=test cmd`), `2>/dev/null`,
and POSIX utilities assumed on `PATH`. Prefer the project's own runner
(`npm test`, `pytest tests/auth -q`, `dotnet build`). Paths stay relative with
forward slashes, on every host.

**`Starting Points` is a map, not a fence.** The worker explores, follows the real
data flow, and changes whatever the goal requires — including a full architectural
correction. Fencing a capable model into two or three files is how a proper fix
degrades into a local patch. `Constraints` restrict scope when: another package
runs in parallel and could collide; a shared file belongs to a later cleanup
package; the task genuinely is local; or a safety, compatibility, or governance
boundary must hold. When two packages would conflict, run them serially rather
than fencing both.

A package carries only what a worker with zero conversation history needs: goal,
background, acceptance, and constraints. Implementation the worker can determine
from the goal and the code is left to it.

Mid-course additions from the human are appended to the package and re-sent as
the same task; GPT uses the same worker dispatch pattern and Claude uses another
`claude -p` invocation. The relay may adjust the route or worker under the
execution-adjustment rules when needed. They are extensions of one task, not new
product requirements or a new dispatch plan.

## 6. Concurrency And Waiting

Relay／worker 執行命令不得主動建立可見終端視窗，並須保留輸出與 exit
code；實際開窗時先找出 launcher，再修真正的來源。

### Deciding what runs in parallel

Parallelism is a means, not a goal. It exists to shorten the batch, not to keep
subagents busy.

Parallel when packages touch disjoint code *and* will not thrash a shared
resource. Serial when: edits could overlap; each would drive a large build in the
same build directory; the machine would run short of CPU, memory, or disk; or one
package's test results could observe another's half-written files.

"Dispatch one, accept it, dispatch the next" is a good default — often faster in
wall-clock terms than four subagents fighting over one build directory.

A package scheduled to run alongside others gets isolated-corpus acceptance
rather than a global count other packages are concurrently changing, and the
package says why, so the worker does not switch back to the global check.

After the batch, the relay lead runs the plan's `Shared Verification` once over
the merged tree.

### Waiting for an executor

Use the route's completion mechanism, never `sleep`. GPT uses `wait_agent`; a
Claude `-p` invocation is allowed to finish as the blocking process it is. A
completion event does **not** preempt a synchronous shell tool already running,
so a sleeping relay lead sleeps out the full duration while a finished report
waits in the queue. Completion notifications arrive on their own; status
polling buys nothing. GPT spawning is non-blocking and returns an `agent_id`;
waiting is done by id.

```text
spawn_agent(...) → agent_id
wait_agent(targets = [agent_id], timeout_ms = 3600000)
```

`timeout_ms` is milliseconds; one hour is the per-call maximum. Always use it.

`timed_out: true` means the window closed — the subagent is still running in the
background. Call the wait again. It never justifies declaring failure and never
justifies re-dispatching.

With several subagents in flight, `wait_agent` returns when *one* target reaches
a final status; it is not a join. Track outstanding ids, drop each finished one,
accept its work, and wait again on the remainder until the list is empty.

Staying alive is the wait loop's job. The long-running work mode (`/goal` on
Codex) belongs to the **human**, who starts the relay lead in it; the relay lead
never invokes it for itself and never applies it to a subagent. A relay lead
started without it still works.

**While a GPT subagent or Claude process is in flight, the work belongs to it** —
the shared tree (no `git status`, no diff inspection, no build or test), the
running executor (no progress query), and the schedule (no re-dispatch of a
task that may still be running).

Re-dispatch does the real damage: two agents then edit the same files and
overwrite each other silently, which is very hard to see in the final diff. A
package can legitimately run thirty or forty minutes, and only an explicit
failure or error signal means it did not complete.

Free to do meanwhile: read undispatched packages, plan the schedule, and dispatch
the next package under the plan's permitted parallelism — scheduling, not
interference.

### Human additions mid-batch

The relay is the human's window during the batch. The human may review a
completed package, ask for status, or inject additions — a new requirement, a
format change, a different direction for a package that is done or still
running.

- An addition for a **finished** package: append it to that package and re-run
  the same package — normally on the same route, but an equivalent route or
  worker may be selected under the execution-adjustment rules — GPT uses the
  same worker dispatch pattern; Claude uses another `claude --model
  claude-sonnet-5 -p` invocation — an extension of the same task, not a new
  package or dispatch plan.
- An addition for a **running** package: queue it; the worker gets it when it
  reports, as the same appended package. The tree and the running worker stay
  untouched.
- An addition for a **not-yet-dispatched** package: fold it in before dispatch.
- An addition that changes the batch's shared format, constraints, or shared
  verification: record it batch-wide and apply it to the packages it affects.

Human additions are human decisions, not relay inventions: relay them organized,
not reinterpreted, and update the package so the worker has one source of truth.
If an addition makes the spec self-contradictory, flag it upward rather than
resolving it yourself.

### Relay task adjustments

The relay may modify how a task is executed without waiting for a new planning
round. It may repair unambiguous metadata, obvious non-semantic omissions, stale
paths, or verification commands;
change an equivalent command, worker, or execution route; reorder independent
work; or split a package when the original Goal, Acceptance, and important
Constraints remain unchanged. A split carries the original acceptance across
its pieces and makes dependencies explicit.

For every adjustment, record a short `Task adjustments` note in the package or
completion record: original value, replacement, reason, and evidence that the
intent is unchanged. If no equivalent adjustment exists, or the change would
alter the meaning of a requirement, escalate it as a specification decision.
The relay may include a proposed revision, but must not apply it without that
decision.

## 7. Shortcut Patterns

One rule: **do not substitute making the check pass for solving the problem.**

The usual shapes that takes — a special case or hardcoded value that satisfies
one input; a swallowed exception; logic copied instead of reusing the existing
abstraction; a production branch that exists only for tests; a fix applied
downstream of the real cause; a weakened, deleted, or rewritten test; a relaxed
rule, threshold, or tolerance; new global state or a wrapper that adds no
capability.

Any of these can be the right call. A test that encodes the old wrong behaviour
*should* be rewritten; a threshold that was genuinely wrong *should* move. The
failure is doing one silently to get a green check. **Do it deliberately, then
say so and why in the report.** That is what makes it auditable at acceptance
(§9) rather than a rule to deadlock against.

Two changes reach outside the package and are worth flagging prominently in
`Needs A Decision` when the goal requires them and the package did not anticipate
them: a change to a public API, schema, or wire contract, and a new dependency.

**Root-cause preflight.** Before editing, the worker answers internally and puts
the answer in one line of its report: what actually causes this, and at which
layer? Is there an existing abstraction that already handles it? Will this fix
put the same logic in a second place?

## 8. Worker Report Format

Every package report records the outcome separately from facts about work that
already happened:

```text
state: pending | running | blocked | done | failed
blocker: metadata | spec | execution | acceptance | null
implementation_completed: true | false
pushed: true | false
```

`blocked` means the next stage cannot be attempted or continued because a
prerequisite or defect prevents it. `failed` means the stage was attempted but
execution or verification failed. A specification defect discovered after
implementation can therefore be `blocked / spec` while
`implementation_completed` and `pushed` are both true. `done` means the relay
judges the core result sufficiently established in the available environment.
A missing resource is not automatically a failure or a blocker; the relay judges
whether the unavailable check is material to the core result using the Goal,
Acceptance, actual change, available evidence, and the limitation. A non-material
or explicitly skippable/conditional check, or one covered by equivalent evidence,
may coexist with `done` when the limitation and residual risk are recorded. If a
core result cannot be reasonably judged because a resource is missing, use
`blocked / execution`; if the check ran and failed because of the environment,
use `failed / execution`.

```markdown
## Status
state: <pending | running | blocked | done | failed>
blocker: <metadata | spec | execution | acceptance | null>
implementation_completed: <true | false>
pushed: <true | false>

## Changed
- <file>: <what changed and why — one line each>

## Root Cause
<one or two lines: what caused it, and why this layer is the right place to fix it>

## Verification
- <command>
  <the actual output, pasted — not "passed">
- <tests/checks run for Acceptance and their actual output>
- <when relevant: available or missing resources, skipped/conditional checks,
  and equivalent evidence considered>

## Risks
- <what could still be wrong, what was not covered, what is worth watching>
- <or: none>

## Needs A Decision
- <or: none>
```

Evidence is pasted output, never a claim about output. No exploration narrative
or restatement of the task is needed.

### When a package cannot be executed as written

If it contradicts itself, rests on a false premise, or sets an unsatisfiable
constraint, the worker stops and reports the conflict rather than quietly
reinterpreting the goal.

The relay lead first checks whether an unambiguous equivalent task adjustment
can make the package executable. If so, it records the adjustment and continues
with the revised package. If not, it records the problem and its reason in the
`Completion record`, stops that package, and continues with every package the
failure does not block — so the least possible work is lost before the human
returns. A correction that changes the meaning of a requirement belongs to the
planning tier.

## 9. Acceptance

**Relay acceptance is the primary gate**, and the only one guaranteed to happen.
An executor's report is a claim, not a result — and the relay lead started the
work, so it is biased toward believing it. Scale depth to what the package
matters; acceptance re-runs the decisive checks against the actual environment
and available resources.

- Re-run the decisive acceptance commands and read the real output when the
  environment provides what they require. If a check depends on unavailable
  resources, determine whether the package makes it skippable or conditional, or
  whether equivalent evidence proves the same acceptance item.
- Read the diff. Does it match the goal, or only make the check pass?
- Check that nothing outside the goal broke or was bypassed.
- Check for §7 shortcut patterns — especially a relaxed rule or weakened
  assertion that makes a number look right. A shortcut the report explains and
  justifies is fine; an unexplained one is the finding.
- Check the report's stated risks against what the diff shows.

The relay makes the final completion judgment against the actual environment. It
may mark a package `done` when the core result is reasonably established and a
missing check is non-material in context, explicitly skippable/conditional, or
covered by equivalent evidence. It must not mark a core result complete merely
because a resource is missing. If the missing resource prevents a reasonable
completion judgment, use `blocked / execution`; if a check was attempted and
failed because of the environment, use `failed / execution`. Record the available
and missing resources, what was skipped or substituted, the basis for the
judgment, and the remaining risk.

**Returning.** A return names gaps and nothing else; re-explaining the task, the
goal, or the package adds nothing.

```markdown
## Gaps
1. <file:line> — <what is wrong, and what "fixed" looks like>
2. <...>

Everything else is accepted. Change nothing outside these points.
```

The final line is required. Return at most twice; on a third round the
specification is the suspect, and that is the lead's to fix — stop the package
and record why.

**Lead review is a second pass**, reached when the relay escalates a spec defect
or the human asks for one. It reads the same way, against the `Completion
record` and the diff, and re-runs whatever decides acceptance. A wrong
specification is the lead's to withdraw, fix, and reissue.

## 10. Completion Protocol

Order matters: a summary written before the files reach their final state
describes a state that no longer exists. Per package, after it reaches a
terminal state (`done`, `blocked`, or `failed`):

1. **Fill in `Completion record`** while the package is still in `planning/`.
   Written by the relay lead, read by agents rather than skimmed by a human, so
   completeness beats brevity: final status; any `Task adjustments` with original
   and revised values, reasons, and evidence; what was actually changed and
   where it diverged from the package; acceptance and verification results with
   real values; whether a module boundary, ownership, or external contract
   changed; environment/resource limits, known limits, remaining debt, residual
   risk.
2. **Move** to `docs/changes/completed/{{DATE}}/{{SLUG}}.md`, by completion date.
   Every completed package is archived; none is deleted, and none is left in
   `planning/`.
3. **Append** one line to `docs/changes/completed/{{DATE}}/summary.md`, newest
   last — now, not before.
4. **Commit and push**, code and change-record files together.

After the last package: move the dispatch plan to
`completed/{{DATE}}/{{SLUG}}-dispatch-plan.md` alongside the packages, so the
completed folder holds the whole batch and `planning/` keeps only pending
batches. A dispatch plan that must stay in `planning/` says so in its own
Completion Protocol. Then run the plan's `Shared Verification` over the merged
tree, run the atlas refresh from the `Completion record` entries that flagged a
boundary, ownership, or contract change (update the affected module doc, index
entry, and Architecture Decisions row), and report the batch. The relay owns
this refresh; the lead is involved only when a spec defect needs reissuing.

## 11. Cost And Context Discipline

- **While work is out, leave it to the execution tier.** Waiting is scheduling:
  read undispatched packages, plan the order, and answer the human's status
  questions. No `git status`, no diff inspection, no speculative reading, no
  progress narration — for the lead across the whole batch, and for the relay
  lead while a subagent is in flight.
- **Specify once, completely.** Spend the effort on `Background` and on making
  `Acceptance` checkable, before the handoff. A thin package makes the worker pay
  to rediscover what the lead already knew.
- **Carry conclusions forward.** Move conclusions across steps instead of
  re-reading the index at review time.
- **Batch the review.** Review once against the whole returned change, and issue
  one list of gaps.
- **Split by change boundary, not by file.** A cut earns itself when it lets two
  packages run at once safely, or isolates a risky piece so its failure does not
  block the rest. It earns nothing when the halves must be re-verified together
  anyway.
- **Serialize shared builds.** Several subagents each building the same tree is
  the most expensive way to get the least reliable answer; serialize instead.
