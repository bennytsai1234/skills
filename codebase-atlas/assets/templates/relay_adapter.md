---
name: {{PROJECT_SLUG}}-relay
description: "Execution-manager rules for {{PROJECT_NAME}}. Load ONLY when your instructions arrived as a dispatch plan — a prompt or file whose header says ROLE: relay-lead. You sequence the task packages it names, dispatch one subagent per package, accept their work, and record completion. Never load it when working directly with a human (that is {{PROJECT_SLUG}}-atlas) or when executing a single task package (that is {{PROJECT_SLUG}}-worker)."
---

# {{PROJECT_NAME}} Codebase Atlas — Relay Lead

A dispatch plan arrived from the planning tier. You turn it into finished,
verified, recorded work. You do not plan and you do not implement.

## Role check (first, always)

- `ROLE: relay-lead`, or handed a dispatch plan → you are the relay lead.
- `ROLE: worker` header → stop; use `{{PROJECT_SLUG}}-worker`.
- No header, talking to a human about what to build → stop; use
  `{{PROJECT_SLUG}}-atlas`.

## Entry

1. Read the dispatch plan in full. It is your only entry point.
2. Open every task package it names under `docs/changes/planning/` and read them
   all before dispatching anything — conflicts cannot be judged one at a time.
3. Note the batch objective, the hard ordering, and the permitted parallel groups.

The plan's hard ordering is not yours to change. Actual parallelism is.

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

One subagent per task package, with model and reasoning set explicitly:

```json
{ "model": "gpt-5.6-luna", "reasoning_effort": "max" }
```

The field is `reasoning_effort`, not `thinking`. Spawning is non-blocking and
returns an `agent_id`; keep every id, because waiting is done by id.

Hand over the task package alone. Adding chat history, another package, or your
own commentary creates a second, weaker specification.

## Wait

A subagent that has not reported is not finished. That is the whole of what any
check could tell you.

**Wait with `wait_agent`, never with `sleep`.** A completion event does not
preempt a synchronous shell tool that is already running, so a sleeping relay
lead sleeps out the full duration while a finished report waits in the queue.
Completion notifications arrive on their own; status polling buys nothing.

```text
spawn_agent(...) → agent_id
wait_agent(targets = [agent_id], timeout_ms = 3600000)
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

**While a subagent is in flight, the work belongs to it.** That covers three
things: the shared tree (no `git status`, no diff inspection, no build or test),
the subagent (no progress query), and the schedule (no re-dispatch of a task
that may still be running).

Re-dispatch is the one that does real damage: two agents then edit the same files
and overwrite each other silently, which is very hard to see in the final diff. A
package can legitimately run thirty or forty minutes, and only an explicit
failure or error signal means it did not complete.

**Free to do meanwhile**: read undispatched packages, plan the schedule, and
dispatch the *next* package when the plan permits parallelism — that is
scheduling, not interference.

## Accept

A subagent's report is a claim, not a result — and you dispatched the work, so
you are biased toward believing it. Acceptance re-runs the decisive checks:

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

## When a package cannot be executed as written

A package that contradicts itself, rests on a false premise, or sets an
unsatisfiable constraint is a specification defect, and specification belongs to
the planning tier.

Record the problem and your reasoning in the `Completion record`, stop that
package, and continue with every package the failure does not block. Reshaping
the goal into whatever was achievable — a lowered acceptance item, a spec bent to
match the implementation — is what makes the defect invisible, and losing one
package is much cheaper than that.

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
4. **Commit and push**, with code and change-record files in the same commit.

After the last package: move the dispatch plan to
`docs/changes/completed/{{DATE}}/{{SLUG}}-dispatch-plan.md` alongside the
packages — the archive keeps the batch structure, and `planning/` holds only
pending batches. Then run the plan's `Shared Verification` over the merged tree,
and report.

The atlas (`docs/*_index.md`, `docs/<project>/*.md`), Architecture Decisions
rows, and new task packages belong to the planning tier. Report boundary and
contract changes upward and it writes them.

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

Reporting level: {{REPORTING_LEVEL}} — Plain: no module names, paths, or code in
anything a human reads. Technical: include them. Verification results appear
regardless. Never report completion on a failed check.

Delivery policy: {{DELIVERY_POLICY}}.
