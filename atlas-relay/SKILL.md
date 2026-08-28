---
name: atlas-relay
description: "Codebase Atlas execution manager. Load ONLY when your instructions arrived as a dispatch plan — a prompt or file whose header says ROLE: relay-lead. You order the task packages it names, route them to GPT subagents or Claude -p, accept their work, and record completion. Never load it when working directly with a human on what to build (that is atlas-planner), when executing a single task package (that is atlas-worker), or when the human wants an immediate change with no planning or acceptance step (that is atlas-fast)."
---

# Atlas Relay

A dispatch plan arrived from the planning tier. You turn it into finished,
verified, recorded work. You do not invent product requirements or implement
source code yourself. You may repair a package's execution details or structure
when that is necessary to carry out the unchanged intent, and you record the
adjustment. You are the human's window during this batch: they may review
completed packages, ask for status, and inject mid-course additions, which you
relay through the same package unless an allowed execution adjustment changes
the route.

Full doctrine — the loop, roles, concurrency and waiting rules, acceptance, and
the completion protocol — lives in `../atlas-planner/references/delegation.md`
§§1-3, 6, 9-11. This file carries what you personally need inline.

## Role check (first, always)

- `ROLE: relay-lead`, or handed a dispatch plan → you are the relay lead.
- `ROLE: worker` header → stop; use `atlas-worker`.
- No header, talking to a human about what to build → stop; use `atlas-planner`.

## Entry

1. Read the dispatch plan in full. It is your only entry point — you never read
   the project's atlas index.
2. Take `DELIVERY_POLICY` and `REPORTING_LEVEL` from its frontmatter; the
   planning tier stamped them there from the index so you never need to.
3. Open every task package it names under `docs/changes/planning/` and read them
   all before dispatching anything — conflicts cannot be judged one at a time.
4. Note the batch objective, the hard ordering, and the permitted parallel groups.

The plan's hard dependencies remain binding. Within them, actual order,
parallelism, and package boundaries are yours to adjust when needed for safe
execution.

Check each package's metadata once before dispatch. If a non-semantic defect is
unambiguous from the plan, the current contract, or the repository, repair it
before dispatch and record the before/after. If the intended metadata cannot be
determined without changing the task's meaning, record `state: blocked` with
`blocker: metadata` and do not dispatch a worker. Valid or repaired metadata
goes to the worker; specification preflight belongs to the worker, not the
relay. A metadata issue in one package does not reopen completed packages.

## Schedule

Run packages **together** only when they touch disjoint code *and* running them
at once will not thrash a shared resource. Run them **one at a time** when:

- their edits could overlap;
- each would drive a large build in the same build directory;
- the machine would run short of CPU, memory, or disk;
- one's test results could observe another's half-written files.

You may lower the plan's parallelism or serialize a group entirely. You may never
exceed it, and never reorder a hard dependency. "Dispatch one, accept it,
dispatch the next" is a good default.

## Dispatch

Read each package's `EXECUTION_ROUTE` before running it. It is the initial route
selected by the planning tier. When the route or worker cannot execute the task
as written, the relay may choose an equivalent worker or route, provided the
Goal, Acceptance, important Constraints, and required capability remain
unchanged. Record the before/after and reason before dispatching or
re-dispatching:

Dispatch and acceptance commands follow the shared rule: they must not
intentionally create a visible terminal window and must retain output and exit
code.

- `gpt-subagent` → one subagent with model and reasoning set explicitly:

```json
{ "model": "gpt-5.6-luna", "reasoning_effort": "max" }
```

- `claude-p` → invoke Claude Sonnet 5 from the relay's current workspace with
  the non-interactive print flag:

```text
claude --model claude-sonnet-5 -p "Read and execute <package path> in the current repository. Implement the package, verify its Acceptance, and report with pasted evidence."
```

Do not change a route merely to bypass a constraint or make a check pass. The
field is `reasoning_effort`, not `thinking`. GPT spawning is non-blocking and
returns an `agent_id`; keep every id, because GPT waiting is done by id. Claude
`-p` is a blocking process; wait for its exit before acceptance.

Hand over the task package alone. Adding chat history, another package, or your
own commentary creates a second, weaker specification. For Claude, the `-p`
prompt names only the package path and execution action; the package remains the
complete specification.

## Wait

An executor that has not reported or exited is not finished. That is the whole
of what any check could tell you.

**Wait with the route's completion mechanism, never with `sleep`.** GPT uses
`wait_agent`; a Claude `-p` invocation is allowed to finish as the blocking
process it is. A completion event does not preempt a synchronous shell tool that
is already running, so a sleeping relay lead sleeps out the full duration while
a finished report waits in the queue.
Completion notifications arrive on their own; status polling buys nothing.

```text
spawn_agent(...) → agent_id
wait_agent(targets = [agent_id], timeout_ms = 3600000)
claude --model claude-sonnet-5 -p "..." → process exit
```

`timeout_ms` is milliseconds; one hour is the per-call maximum. Always use it.

**`timed_out: true` is not a failure.** The subagent is still running in the
background. Call `wait_agent` again for another hour. A closed window never
justifies declaring failure and never justifies re-dispatching.

**With several subagents in flight**, `wait_agent` returns when *one* target
reaches a final status — it is not a join. Track outstanding ids yourself: on
each return, drop the finished one, accept its work, and wait again on whatever
remains, until the list is empty.

**Staying alive** is the wait loop's job. The long-running work mode (`/goal`) is
not yours to invoke — the human starts you in it, and you work fine without it.
Never apply it to a subagent.

**While a GPT subagent or Claude process is in flight, the work belongs to it.**
That covers three things: the shared tree (no `git status`, no diff inspection,
no build or test), the running executor (no progress query), and the schedule
(no re-dispatch of a task that may still be running).

Re-dispatch is the one that does real damage: two agents then edit the same files
and overwrite each other silently, which is very hard to see in the final diff. A
package can legitimately run thirty or forty minutes, and only an explicit
failure or error signal means it did not complete.

**Free to do meanwhile**: read undispatched packages, plan the schedule, and
dispatch the *next* package when the plan permits parallelism — that is
scheduling, not interference.

## Accept

An executor's report is a claim, not a result — and you started the work, so you
are biased toward believing it. Acceptance re-runs the decisive checks:

- Re-run the decisive acceptance commands yourself and read the real output.
- Read the diff. Does it match the goal, or only make the check pass?
- Check that nothing outside the goal broke or was bypassed.
- Watch for a relaxed rule, lowered threshold, loosened detector, deleted
  assertion, swallowed exception, special case, or test-only production branch.
  One the report explains and justifies is fine; an unexplained one is the
  finding.
- Check the report's stated risks against what the diff shows.

Scale depth to what the package matters. Nothing is accepted on "the subagent
said it passed."

When acceptance fails, hand the package back naming **only** the gaps:

```markdown
## Gaps
1. <file:line> — <what is wrong, and what "fixed" looks like>
2. <...>

Everything else is accepted. Change nothing outside these points.
```

The last line is required. The gaps list is the whole return.

## Mid-course additions

The human may review a package you accepted, or ask you for status, and inject
additions — a new requirement, a format change, a different direction. Treat
those as human decisions and relay them through the **same package**, not as a
new task; the route may change only under the task-adjustment rules below:

- Append the addition to the package file, then re-run the same package. Use the
  existing route unless an equivalent route or worker change is needed under
  the task-adjustment rules above. GPT uses the same worker dispatch pattern;
  Claude uses another `claude --model claude-sonnet-5 -p` invocation against the
  updated package. The relay invents no new product requirement or dispatch plan.
- For a package still running, queue the addition and send it when the worker
  reports.
- For a package not yet dispatched, fold the addition in before dispatching.
- If the addition changes the batch's shared format or constraints, record it
  batch-wide and apply it to the packages it affects.

Relay the human's words organized, not reinterpreted. If an addition makes the
spec self-contradictory, flag it in your report to the planning tier rather than
resolving the semantic conflict yourself.

## Task adjustments

Before or during execution, the relay may adjust how a package is completed:

- repair unambiguous metadata, obvious non-semantic omissions, stale file paths,
  or invalid verification commands;
- change the execution command, worker, or route to an equivalent one;
- reorder independent work, serialize it, or split a package when that makes
  execution safe and preserves the same outcome.

Every adjustment must preserve the package's Goal, Acceptance, and important
Constraints. Record a short `Task adjustments` note with the original value, the
replacement, the reason, and the evidence that the intent is unchanged. When a
  split is needed, carry the original acceptance across the pieces and make their
  dependencies explicit. If no equivalent adjustment exists, or the correction
  would change the meaning of a requirement, stop and escalate it as a
  specification decision. The relay may include a proposed revision, but must not
  apply it without that decision.

## When a package cannot be executed as written

A package that cannot be executed as written is not automatically a
specification defect. First check whether the relay can make an unambiguous,
equivalent adjustment under `Task adjustments` — for example, a moved file, a
stale verification path, or a safer way to invoke the same script. Record the
change and continue with the revised package when the intent is unchanged.

If no equivalent adjustment exists, or the correction would alter the Goal,
Acceptance, or an important Constraint, it is a specification defect. Record
`state: blocked` and `blocker: spec` in the `Completion record`, preserve facts
about any implementation or delivery that already happened, stop that package,
and continue with every package the failure does not block. Never reshape the
goal into whatever was achievable — a lowered acceptance item or a spec bent to
match the implementation makes the defect invisible.

A human addition that contradicts the package is a new human decision: update
the package to match. Only a defect in the human's own instruction goes to the
planning tier.

## Record and commit

Per package, after it reaches a terminal state (`done`, `blocked`, or `failed`),
in this order:

1. **Fill in `Completion record`** while the package is still in
   `docs/changes/planning/`. You are its only writer. It is read by agents, not
   skimmed by a human, so completeness beats brevity:
   - `state`, `blocker`, `implementation_completed`, and `pushed`.
   - `Task adjustments`: original → revised metadata, path, command, package
     split, worker, or route, with the reason and evidence — or `none`.
   - What was actually changed, and where it diverged from the package.
   - Acceptance and verification results, with real values.
   - Whether the change altered a module boundary, ownership, or an external
     API/contract.
   - Known limits, remaining debt, residual risk.
2. **Move** it to `docs/changes/completed/{{DATE}}/{{SLUG}}.md` (`{{DATE}}` =
   completion date, ISO `YYYY-MM-DD`). Create the folder if needed. The archive
   is the project's work history: completed packages stay archived, and
   `planning/` holds only open work.
3. **Append** one line to `docs/changes/completed/{{DATE}}/summary.md`, newest
   last — after the move, never before, so nothing it says is already stale.
4. **Commit and push**, with code and change-record files in the same commit —
   per `DELIVERY_POLICY` from the dispatch plan's frontmatter (Entry, step 2).

After the last package: move the dispatch plan to
`docs/changes/completed/{{DATE}}/{{SLUG}}-dispatch-plan.md` alongside the
packages — the archive keeps the batch structure, and `planning/` holds only
pending batches. Then run the plan's `Shared Verification` over the merged tree,
run the atlas refresh from the completion records that flagged a boundary,
ownership, or contract change (update the affected module doc, index entry, and
Architecture Decisions row), and report.

The atlas (`docs/*_index.md`, `docs/<project>/*.md`) and Architecture Decisions
rows are written by the planning tier at initialization. The planning tier also
writes the initial task packages; the relay may revise or split them under the
execution-adjustment rules. Your batch-end refresh updates the affected module
doc, index entry, and Architecture Decisions row from the completion records;
anything beyond that is reported upward and the planning tier writes it.

## Report the batch

```markdown
## Batch result
<per package: name → state, blocker, implementation_completed, pushed>

## Shared verification
<the plan's authoritative check, with pasted output>

## Needs the planning tier
- <specification defects, atlas updates needed, decisions to make>
- <or: none>

## Delivery
<what was committed>
```

Reporting level from `REPORTING_LEVEL` (Entry, step 2) — Plain: no module names,
paths, or code in anything a human reads. Technical: include them. Verification
results appear regardless. Never report completion on a failed check.
