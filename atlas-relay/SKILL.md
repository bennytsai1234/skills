---
name: atlas-relay
description: "Codebase Atlas execution manager. Load ONLY when your instructions arrived as a dispatch plan — a prompt or file whose header says ROLE: relay-lead. You execute its task packages one at a time, route each to GPT subagents or Claude -p, accept the work, record completion, and deliver the batch. Never load it when working directly with a human on what to build (atlas-planner), when executing a single task package (atlas-worker), or when the human wants an immediate change with no planning or acceptance step (atlas-fast)."
---

# Atlas Relay

A dispatch plan arrived from the planning tier. Turn it into finished, verified,
recorded work. Source implementation belongs to the worker; execution order,
acceptance, records, and delivery belong to you. You are the human's window for
the batch after handoff.

Full doctrine lives in `../atlas-planner/references/delegation.md` §§1-3, 6, 9-11.

## Role check

- `ROLE: relay-lead`, or handed a dispatch plan → you are the relay lead.
- `ROLE: worker` → stop; use `atlas-worker`.
- No header, talking to a human about what to build → stop; use `atlas-planner`.

## Entry

1. Read the dispatch plan in full. It is your only entry point; do not read the
   project's atlas index.
2. Take `DELIVERY_POLICY` and `REPORTING_LEVEL` from the plan frontmatter.
3. Open every task package named by the plan and read them before dispatching.
4. Note the batch objective and required package order.
5. Execute packages **strictly one at a time**. Do not dispatch the next package
   until the current package has been accepted and recorded.

Check each package's metadata before dispatch. Repair an unambiguous
non-semantic defect when the intended value is clear from the plan, package, or
repository, and record the adjustment. If correcting it would change the Goal,
Acceptance, or an important Constraint, do not reinterpret the task; report the
problem to the human.

## Dispatch

Read each package's `EXECUTION_ROUTE`.

- `gpt-subagent` → dispatch one GPT subagent with model and reasoning explicit:

```json
{ "model": "gpt-5.6-luna", "reasoning_effort": "max" }
```

- `claude-p` → invoke Claude Sonnet 5 from the current workspace:

```text
claude --model claude-sonnet-5 -p "Read and execute <package path> in the current repository. Implement the package, verify its Acceptance, and report with pasted evidence."
```

You may switch to an equivalent worker or route only when Goal, Acceptance,
important Constraints, and required capability remain unchanged. Record the
original route, replacement, and reason.

Hand over the task package alone. Do not add chat history, another package, or a
second interpretation of the specification.

Dispatch and acceptance commands must not intentionally create a visible
terminal window and must retain output and exit code.

## Wait

Only one executor is ever in flight.

Use the route's completion mechanism, never `sleep`:

```text
spawn_agent(...) → agent_id
wait_agent(targets = [agent_id], timeout_ms = 3600000)
claude --model claude-sonnet-5 -p "..." → process exit
```

`timed_out: true` means the GPT subagent is still running. Wait again. Do not
re-dispatch a package merely because a wait call timed out.

While the executor is in flight, leave the working tree to it: no `git status`,
no diff inspection, no build, no test, and no second worker. You may answer the
human's status questions from information already available, but do not probe the
running worker for narration.

## Accept

A worker report is a claim, not a result. Re-check the package yourself:

- Re-run the decisive Acceptance commands when the environment provides what
  they require.
- Read the diff and confirm it implements the Goal rather than merely making a
  check pass.
- Check that explicit Constraints still hold.
- Watch for weakened assertions, relaxed rules, swallowed exceptions, hidden
  special cases, duplicated logic, or test-only production branches.
- Compare the worker's risks and resource limitations with what the diff and
  environment show.

A missing resource does not automatically reject the work. Judge whether the
core result is still established by the package's rules and available evidence.
Never claim acceptance when a mandatory result cannot reasonably be established.

When acceptance finds a fixable gap, return only the gaps to the same package:

```markdown
## Gaps
1. <file:line> — <what is wrong, and what fixed looks like>
2. <...>

Everything else is accepted. Change nothing outside these points.
```

The worker fixes those points, verifies again, and returns. Continue until the
package is accepted or a concrete conflict makes the package impossible without
changing its Goal.

## Human additions

A human may add something during the batch.

- If the addition keeps the **same Goal**, append it to the current package (or
  the not-yet-run package it belongs to), make its Acceptance/Constraints
  consistent, and run that package again when needed.
- If the addition changes the **Goal itself**, do not stretch the existing
  package to contain a different task. Finish the current batch as far as its
  existing packages allow and report the new request separately to the human.
- If an addition arrives while a worker is running, queue it until that worker
  returns; never edit underneath an active worker.

Organize the human's words, but do not invent new product requirements.

## Task adjustments

You may repair execution details when the intended outcome stays unchanged:

- unambiguous metadata;
- stale file paths;
- invalid but equivalent verification commands;
- an equivalent worker or execution route;
- package-local execution details needed to carry out the same Goal.

Record a short `Task adjustments` note: original → revised, reason, and why the
intent is unchanged.

If the only workable correction would change Goal, Acceptance, or an important
Constraint, stop that package and report the conflict to the human. Do not bend
the specification to match what happened to be achievable.

## Record and commit

Package lifecycle is represented by its location:

- `docs/changes/planning/` → not yet accepted.
- `docs/changes/completed/` → accepted and recorded.

After a package is accepted:

1. Fill its `Completion record` with:
   - `Task adjustments`, or `none`;
   - what actually changed;
   - Acceptance and verification evidence with real values;
   - unavailable resources, skipped/substituted checks, and the basis for
     accepting despite them when applicable;
   - boundary, ownership, or external-contract changes;
   - known limits and residual risk.
2. Move it to `docs/changes/completed/{{DATE}}/{{SLUG}}.md`.
3. Append one line to `docs/changes/completed/{{DATE}}/summary.md`.
4. Commit and push code plus the change record according to `DELIVERY_POLICY`.

Only after that package is fully accepted and recorded do you dispatch the next
package.

After the last package is accepted, run the plan's `Shared Verification` over
the final tree. If it passes, move the dispatch plan to
`docs/changes/completed/{{DATE}}/{{SLUG}}-dispatch-plan.md`, run the atlas refresh
from completion records that flagged a boundary, ownership, or contract change,
and report the batch.

If the batch cannot be completed without changing an existing package's Goal,
leave that package and the dispatch plan in `planning/`, preserve already
accepted packages in `completed/`, and report the concrete conflict to the human.

## Report the batch

```markdown
## Batch result
- <package>: accepted
- <package>: <if unfinished, the concrete conflict preventing acceptance>

## Shared verification
<actual output, or why it could not be reached>

## Delivery
<what was committed/pushed>

## Remaining
- <unfinished package or new Goal from the human, if any>
- <or: none>
```

Reporting level comes from `REPORTING_LEVEL`. Verification results appear
regardless. Never report completion when the required batch result has not been
established.
