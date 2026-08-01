# Delegation

The doctrine the generated lead, relay, and worker adapters must carry. Read this
when generating adapters, and when deciding what belongs in each one.

The handoff from planning to execution is human-mediated: the lead writes files
and stops, and the human carries one file across. Everything after that — order,
dispatch, acceptance, records — belongs to the relay lead, because the human is
not expected to come back.

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
           7. dispatch one subagent per package
Worker     8. explore, implement across files as needed
           9. run the checks that prove acceptance
          10. report with evidence and risks
Relay     11. accept by re-running the decisive checks — or return precise gaps
          12. fill the completion record, archive, summarize, commit and push
          13. run the batch verification, report
Lead      14. (if the human returns) second-pass review, and atlas updates
```

Step 4→5 crosses a human, once. Steps 7→8 and 10→11 do not — the relay lead
dispatches and accepts on its own. Step 14 may never happen, and the workflow
must be complete without it.

## 2. Roles

**Lead** — the only agent in contact with the human. Runs on the strongest
available model. It owns:

- Understanding vague requests and aligning on intent.
- Reading the atlas and deciding what the change touches.
- Product decisions that cannot be inferred from the repository, and the Decision
  Gate.
- The Before / After gate.
- Diagnosis: reproducing the problem, finding the root cause, proving it.
- Decomposition: cutting the work into packages.
- Writing every task package and the dispatch plan, then committing and pushing
  them.
- Atlas docs and Architecture Decisions rows.
- Second-pass review of whatever the human brings back.

**The lead never edits source code or tests.** No size exemption: a typo leaves
as a task package like everything else. It never dispatches a subagent. Its
output is specification.

The lead may read code, run read-only checks, and re-run a verification whose
result decides acceptance. When one of those fails, it is a gap to return, not
something to fix.

**Relay lead** — the execution manager, started by the human with the dispatch
plan. Runs on **GPT-5.6-Luna, reasoning Max**. It owns:

- Reading the dispatch plan and every package it names.
- Execution order within the plan's dependencies, and the real parallelism
  decision.
- Dispatch, passed explicitly as
  `{"model": "gpt-5.6-luna", "reasoning_effort": "max"}` — never inherited. The
  field is `reasoning_effort`, not `thinking`; `max` is the top of this model's
  scale (`low` / `medium` / `high` / `xhigh` / `max`).
- Waiting without interfering (§6).
- Acceptance, by re-running the decisive checks (§9).
- Completion records, the completed folder, the daily summary, and the commit and
  push (§10).

**Worker** — a strong implementation agent, dispatched against one task package.
Runs on **GPT-5.6-Luna, reasoning Max**. It owns:

- Exploring the codebase to find what the change requires. The package names
  starting points; it does not cap what may be read.
- Deciding the implementation from the goal, background, acceptance criteria,
  code, and explicit constraints.
- Editing across as many files as the change needs.
- Adding or extending tests when they are needed to establish acceptance.
- Running the checks needed to establish acceptance — including a whole-project
  build and the full test suite — and fixing relevant failures.
- Reporting with evidence: what was changed, what was run, what came back.

Everything else belongs to another tier: records and delivery to the relay lead,
the atlas and Architecture Decisions to the lead, the Before / After gate to the
conversation that produced the package. A decision the package settled stays
settled — a worker that thinks one is wrong says so in `Needs A Decision`.

**What this workflow is for.** Work that needs analysis, a plan, several
implementation steps, and acceptance. A typo, a constant, a one-line config
change never enters it — those go straight to an execution model. Do not build a
trivial tier to accommodate them.

## 3. Role Resolution

Resolve the role from the instructions, not from the environment:

| Header | Role |
|---|---|
| `ROLE: worker` | Worker |
| `ROLE: relay-lead` | Relay lead |
| no header | Lead — so the human-alignment gate is never silently skipped |

**Governance writes** are split by tier. Before writing one, confirm the file
belongs to your tier:

| File | Written by | Committed and pushed by |
|---|---|---|
| Atlas docs (`docs/*_index.md`, `docs/<project>/*.md`) | Lead | Lead |
| Architecture Decisions rows | Lead | Lead |
| `docs/changes/planning/**` — packages, dispatch plans | Lead | Lead, before handover |
| `Completion record` inside a package | Relay lead | Relay lead |
| `docs/changes/completed/**` — archived packages, `summary.md` | Relay lead | Relay lead |
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
---

# <what this batch achieves>

## Objective
<2-4 lines: what is true when the whole batch is done>

## Task Packages
| # | Package | Goal (one line) |
|---|---|---|
| 1 | `docs/changes/planning/{{DATE}}-{{SLUG}}.md` | <...> |

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
MODEL: GPT-5.6-Luna
REASONING: Max
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

**Background** is what makes the package portable to a model with zero
conversation history, on another platform. No length limit. Include, when they
apply:

- The problem, in enough depth that the goal is obviously the right goal.
- How the current implementation works, with the wrong code quoted.
- Real input against real wrong output — a table beats a paragraph.
- Any inventory the lead already did, marking entries that are "currently correct
  but only by luck", since a worker skips exactly those otherwise.
- Known limits of single-file or single-pass analysis.

Do not add generic rules such as "preserve existing functionality", "use a
reasonable architecture", or "maintain code quality". Add a constraint only when
it records a real requirement that the worker cannot infer from the repository or
ordinary engineering judgement.

**Acceptance rules.** Every acceptance item must be checkable by someone who was
not in the conversation — an exact command with an expected result, or an
observable behaviour described precisely enough to disagree with. "Works
correctly" is not an acceptance criterion. Prefer exact expected values over
existence claims. Cover the negative case and say what a negative fixture must
contain. Name what must not change. Ban passing by weakening — no relaxed rule,
lowered threshold, loosened detector, or deleted assertion — and require any drop
in a previously passing count to be explained item by item. Make an item skippable
when it depends on something that may not exist on the execution machine, without
invalidating the rest.

**Command rules.** Write commands for the shell the worker will get. One command
per line, never an `&&` chain — Windows PowerShell 5.1 has no `&&`. On a Windows
host also avoid inline environment prefixes (`NODE_ENV=test cmd`), `2>/dev/null`,
and POSIX utilities assumed on `PATH`. Prefer the project's own runner
(`npm test`, `pytest tests/auth -q`, `dotnet build`). Paths stay relative with
forward slashes, on every host.

**`Starting Points` is a map, not a fence.** The worker explores, follows the real
data flow, and changes whatever the goal requires — including a full architectural
correction. Fencing a capable model into two or three files is how a proper fix
degrades into a local patch. Restrict scope in `Constraints` only when: another
package runs in parallel and could collide; a shared file belongs to a later
cleanup package; the task genuinely is local; or a safety, compatibility, or
governance boundary must hold. When two packages would conflict, run them
serially rather than fencing both.

**Never** paste chat history, the index, or a full spec into a package. Do not
prescribe the implementation when the worker can determine it from the goal and
the code.

## 6. Concurrency And Waiting

### Deciding what runs in parallel

Parallelism is a means, not a goal. Never widen it to keep subagents busy.

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

### Waiting for a subagent

Use `wait_agent`, never `sleep`. A completion event does **not** preempt a
synchronous shell tool already running, so a sleeping relay lead sleeps out the
full duration while a finished report waits in the queue. Completion
notifications arrive on their own; status polling buys nothing. Spawning is
non-blocking and returns an `agent_id`; waiting is done by id.

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

**While a subagent is in flight, the relay lead leaves the work alone** — the
shared tree (no `git status`, no diff inspection, no build or test), the subagent
(no progress query), and the schedule (no re-dispatch of a task that may still be
running).

Re-dispatch does the real damage: two agents then edit the same files and
overwrite each other silently, which is very hard to see in the final diff. A
package can legitimately run thirty or forty minutes, and only an explicit
failure or error signal means it did not complete.

Free to do meanwhile: read undispatched packages, plan the schedule, and dispatch
the next package under the plan's permitted parallelism — scheduling, not
interference.

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

```markdown
## Changed
- <file>: <what changed and why — one line each>

## Root Cause
<one or two lines: what caused it, and why this layer is the right place to fix it>

## Verification
- <command>
  <the actual output, pasted — not "passed">
- <tests/checks run for Acceptance and their actual output>

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

The relay lead does the same, upward. It does not rewrite the goal, lower or drop
an acceptance item, or adjust the spec to match what the implementation happens
to do. It records the problem and its reason in the `Completion record`, stops
that package, and continues with every package the failure does not block — so
the least possible work is lost before the human returns. A specification defect
belongs to the planning tier.

## 9. Acceptance

**Relay acceptance is the primary gate**, and the only one guaranteed to happen.
A subagent's report is a claim, not a result — and the relay lead dispatched the
work, so it is biased toward believing it. Scale depth to what the package
matters; never accept on text alone.

- Re-run the decisive acceptance commands and read the real output.
- Read the diff. Does it match the goal, or only make the check pass?
- Check that nothing outside the goal broke or was bypassed.
- Check for §7 shortcut patterns — especially a relaxed rule or weakened
  assertion that makes a number look right. A shortcut the report explains and
  justifies is fine; an unexplained one is the finding.
- Check the report's stated risks against what the diff shows.

**Returning.** A return names gaps and nothing else. Do not re-explain the task,
do not restate the goal, do not re-send the package.

```markdown
## Gaps
1. <file:line> — <what is wrong, and what "fixed" looks like>
2. <...>

Everything else is accepted. Change nothing outside these points.
```

The final line is required. Return at most twice; on a third round the
specification is the suspect, and that is the lead's to fix — stop the package
and record why.

**Lead review is a second pass**, when and if the human brings results back. It
reads the same way, against the `Completion record` and the diff, and re-runs
whatever decides acceptance. A wrong specification is the lead's to withdraw,
fix, and reissue.

## 10. Completion Protocol

Order matters: a summary written before the files reach their final state
describes a state that no longer exists. Per package, after acceptance:

1. **Fill in `Completion record`** while the package is still in `planning/`.
   Written by the relay lead, read by agents rather than skimmed by a human, so
   completeness beats brevity: final status; what was actually changed and where
   it diverged from the package; acceptance and verification results with real
   values; whether a module boundary, ownership, or external contract changed;
   known limits, remaining debt, residual risk.
2. **Move** to `docs/changes/completed/{{DATE}}/{{SLUG}}.md`, by completion date.
   Every completed package is archived; none is deleted, and none is left in
   `planning/`.
3. **Append** one line to `docs/changes/completed/{{DATE}}/summary.md`, newest
   last — now, not before.
4. **Commit and push**, code and change-record files together.

After the last package: run the plan's `Shared Verification` over the merged
tree, then report the batch. The lead updates atlas docs afterward, from the
`Completion record` entries that flagged a boundary, ownership, or contract
change.

## 11. Cost And Context Discipline

- **While work is out, do nothing.** No `git status`, no diff inspection, no
  speculative reading, no progress narration — for the lead across the whole
  batch, and for the relay lead while a subagent is in flight.
- **Specify once, completely.** Spend the effort on `Background` and on making
  `Acceptance` checkable, before the handoff. A thin package makes the worker pay
  to rediscover what the lead already knew.
- **Do not re-read what you already concluded.** Carry conclusions forward across
  steps rather than re-reading the index at review time.
- **Batch the review.** Review once against the whole returned change, and issue
  one list of gaps.
- **Split by change boundary, never by file.** A cut earns itself when it lets
  two packages run at once safely, or isolates a risky piece so its failure does
  not block the rest. It does not when the halves must be re-verified together
  anyway.
- **Do not multiply builds.** Several subagents each building the same tree is
  the most expensive way to get the least reliable answer; serialize instead.
