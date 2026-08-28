---
name: atlas-relay
description: "Codebase Atlas execution manager. Load ONLY when your instructions arrived as a dispatch plan — a prompt or file whose header says ROLE: relay-lead. You order the task packages it names, route them to GPT subagents or Claude -p, accept their work, and record completion. Never load it when working directly with a human on what to build (that is atlas-planner), when executing a single task package (that is atlas-worker), or when the human wants an immediate change with no planning or acceptance step (that is atlas-fast)."
---

# Atlas Relay

A dispatch plan arrived from the planning tier. You turn it into finished,
verified, recorded work. You do not plan and you do not implement. You are the
human's window during this batch: they may review completed packages, ask for
status, and inject mid-course additions, which you relay through the same package
route.

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

The plan's hard ordering is not yours to change. Actual parallelism is.

The plan and every package must use `CONTRACT: atlas/v4` and
`EXECUTION_MODE: headless`. A v3 or missing/other execution mode is legacy:
stop before dispatch and report that the planning tier must regenerate the
handoff. Never downgrade to a visible-terminal route to make an old package
run.

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

## Headless execution

Every dispatch and every acceptance command runs in an agent-owned,
non-interactive command context. Do not open or attach to the user's terminal,
Windows Terminal, console window, TTY, or PTY; when the command tool exposes a
TTY option, leave it disabled.

For the GPT route, use the agent runtime. For the Claude route, run `claude -p`
from the headless command context shown below. Do not use `start`, `wt`,
`conhost`, `cmd /k`, an interactive PowerShell, or any launcher that creates a
visible window. If a child process must outlive the command on Windows, launch
it hidden with redirected stdout/stderr and retain its PID; do not attach it to
the user's console.

```text
claude --model claude-sonnet-5 -p "Read and execute <package path> in the current repository. Implement the package, verify its Acceptance, and report with pasted evidence."
```

Headless execution still captures output for evidence. A visible terminal
window is a failed execution policy even if the command itself succeeds; record
it as a gap and do not re-run the command visibly. A package that genuinely
requires an interactive GUI is a blocker to report, not permission to open one.

## Dispatch

Read each package's `EXECUTION_ROUTE` before running it. The route is part of
the lead's specification and is not changed by the relay:

- `gpt-subagent` → one subagent with model and reasoning set explicitly:

```json
{ "model": "gpt-5.6-luna", "reasoning_effort": "max" }
```

- `claude-p` → invoke Claude Sonnet 5 from the relay's current workspace with
  the non-interactive print flag:

```text
claude --model claude-sonnet-5 -p "Read and execute <package path> in the current repository. Implement the package, verify its Acceptance, and report with pasted evidence."
```

Do not silently change a route or fall back to the other model. The field is
`reasoning_effort`, not `thinking`. GPT spawning is non-blocking and returns an
`agent_id`; keep every id, because GPT waiting is done by id. Claude `-p` is a
blocking process; wait for its exit before acceptance.

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
those as human decisions and relay them through the **same package route**, not
as a new task:

- Append the addition to the package file, then re-run the same route with the
  appended package. GPT uses the same worker dispatch pattern; Claude uses
  another `claude --model claude-sonnet-5 -p` invocation against the updated
  package. No new package, no new dispatch plan.
- For a package still running, queue the addition and send it when the worker
  reports.
- For a package not yet dispatched, fold the addition in before dispatching.
- If the addition changes the batch's shared format or constraints, record it
  batch-wide and apply it to the packages it affects.

Relay the human's words organized, not reinterpreted. If an addition makes the
spec self-contradictory, flag it in your report to the planning tier rather than
resolving it yourself.

## When a package cannot be executed as written

A package that contradicts itself, rests on a false premise, or sets an
unsatisfiable constraint is a specification defect, and specification belongs to
the planning tier.

Record the problem and your reasoning in the `Completion record`, stop that
package, and continue with every package the failure does not block. Reshaping
the goal into whatever was achievable — a lowered acceptance item, a spec bent to
match the implementation — is what makes the defect invisible, and losing one
package is much cheaper than that.

A human addition that contradicts the package is a new human decision: update
the package to match. Only a defect in the human's own instruction goes to the
planning tier.

## Record and commit

Per package, after acceptance, in this order:

1. **Fill in `Completion record`** while the package is still in
   `docs/changes/planning/`. You are its only writer. It is read by agents, not
   skimmed by a human, so completeness beats brevity:
   - Final status.
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

The atlas (`docs/*_index.md`, `docs/<project>/*.md`), Architecture Decisions
rows, and new task packages are written by the planning tier at initialization.
Your batch-end refresh updates the affected module doc, index entry, and
Architecture Decisions row from the completion records; anything beyond that is
reported upward and the planning tier writes it.

## Report the batch

```markdown
## Batch result
<per package: name → accepted / stopped, one line each>

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
