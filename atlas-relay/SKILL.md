---
name: atlas-relay
description: "Execution manager for a formal Atlas dispatch plan. Load only when instructions arrive as a dispatch plan or with ROLE: relay-lead. Execute detailed atlas/v4 task packages strictly in order, route each package to the current suitable executor, independently accept the returned work, record completion, and deliver according to the plan. Do not use for direct human planning, ordinary development, or a single ROLE: worker package."
---

# Atlas Relay

Turn one confirmed dispatch plan into finished, independently accepted work.

The planner already discussed the problem with the human and encoded the confirmed solution in detailed packages. Relay owns sequencing, executor routing, acceptance, records, and delivery. Source implementation belongs to Worker.

Read `../atlas-planner/references/delegation.md` for the shared `atlas/v4` contract.

## Role check

- `ROLE: relay-lead`, or a dispatch plan -> continue here.
- `ROLE: worker` -> use `atlas-worker`.
- Human is still discussing what to build -> use `atlas-planner` only if they explicitly asked for the planner; otherwise handle it directly.
- Ordinary direct development -> handle it directly without an atlas skill.

## Entry

1. Read the dispatch plan in full.
2. Read every named task package before dispatching anything.
3. Confirm package order, dependency reasons, batch objective, and `DELIVERY_POLICY`.
4. Execute packages strictly one at a time.

Do not reinterpret the human-confirmed Goal or Recommended Solution just because another implementation would be easier.

## Dispatch

Read each package's `EXECUTION_ROUTE`.

- `gpt-subagent` -> use the currently configured capable GPT coding subagent.
- `claude-p` -> use the currently configured Claude command/worker for that route.

Route names are stable capability labels; model versions are not part of the package contract. If a route is unavailable, choose an equivalent executor only when the package Goal, confirmed solution intent, Acceptance, and important Constraints remain unchanged. Record the adjustment.

Hand the worker the package, not chat history or a second specification.

## Wait

Only one package executor is active at a time.

Use the route's completion mechanism rather than arbitrary polling sleeps. A timeout from a wait primitive means the worker may still be running; wait again unless the tool explicitly reports failure.

While a worker is active:

- do not edit the same working tree;
- do not start another worker on the same batch;
- do not run acceptance checks against a tree that is still changing.

## Accept

Worker output is evidence to inspect, not automatic acceptance.

For each package:

1. Read the returned diff/change surface.
2. Compare it against Goal, Problem / Root Cause, Recommended Solution, Acceptance, and Constraints.
3. Re-run the decisive checks when the environment supports them.
4. Verify the change solves the diagnosed cause rather than merely making a check green.
5. Check for silent solution drift: weakened tests, swallowed exceptions, hidden special cases, duplicated ownership, downstream patches that leave the cause intact, or contract changes not allowed by the package.

If the worker discovered that a package-local implementation detail is invalid, decide whether the proposed adjustment preserves the confirmed solution intent. If yes, approve and record it. If no, stop and return the conflict to the human.

When a fixable gap exists, return only the concrete gaps to the same package/worker. Do not reopen already accepted parts.

## Human additions during a batch

- Same Goal and solution intent -> queue the addition into the current or not-yet-run package, make Acceptance consistent, and rerun as needed.
- Different Goal or materially different solution -> keep it separate; do not stretch the confirmed package into new work.
- Addition arrives while Worker is active -> queue it until the worker returns; do not edit underneath the active worker.

## Record and deliver

After acceptance:

1. Write the `Completion record`: actual changes, implementation adjustments, verification evidence, unavailable resources, and residual risk.
2. If the accepted work established a lasting rule that future work in this repository must follow, add it to the repository `AGENTS.md` as a plain rule. Residual risk stays in the completion record.
3. Delete the package file from `docs/changes/planning/`; there is no completed archive.
4. Apply `DELIVERY_POLICY`:
   - `no commit` -> leave accepted changes in the working tree and put the completion record in the report;
   - `commit only` -> commit the accepted changes with the completion record as the commit message body;
   - `commit and push` -> the same, then push without force.
5. Only then start the next package.

After the final package, run the dispatch plan's Shared Verification. Only after it succeeds, delete the dispatch plan and remove `docs/changes/planning/` (and `docs/changes/`, `docs/`) when empty.

## Report

Report package results (with each completion record when nothing was committed), Shared Verification, delivery, and any unresolved conflict. Never claim a package or batch is accepted when mandatory evidence is missing.
