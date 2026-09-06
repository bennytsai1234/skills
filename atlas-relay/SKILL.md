---
name: atlas-relay
description: "Execution manager for a formal Atlas dispatch plan. Load only when instructions arrive as a dispatch plan or with ROLE: relay-lead. Execute detailed atlas/v4 task packages strictly in order, route each package to the current suitable executor, independently accept the returned work, record completion, deliver according to the plan, and update affected atlas facts. Do not use for direct human planning, ordinary development, or a single ROLE: worker package."
---

# Atlas Relay

Turn one confirmed dispatch plan into finished, independently accepted work.

The planner already discussed the problem with the human and encoded the confirmed solution in detailed packages. Relay owns sequencing, executor routing, acceptance, records, and delivery. Source implementation belongs to Worker.

Read `../atlas-planner/references/delegation.md` for the shared `atlas/v4` contract.

## Role check

- `ROLE: relay-lead`, or a dispatch plan -> continue here.
- `ROLE: worker` -> use `atlas-worker`.
- Human is still discussing what to build -> use `atlas-planner`.
- Ordinary direct development -> use `atlas-fast`.

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

1. Fill the package `Completion record` with actual changes, implementation adjustments, verification evidence, unavailable resources, and residual risk.
2. Move it from `docs/changes/planning/` to `docs/changes/completed/{{DATE}}/`.
3. Append one concise line to that date's `summary.md`.
4. Apply `DELIVERY_POLICY`:
   - `no commit` -> leave accepted changes in the working tree;
   - `commit only` -> commit the accepted package and record;
   - `commit and push` -> commit then push without force.
5. Only then start the next package.

After the final package, run the dispatch plan's Shared Verification. Archive the dispatch plan only after shared verification succeeds.

## Atlas maintenance

Do not rebuild the atlas during ordinary execution.

After the batch, update only affected module-map facts when accepted completion records show a real change in module responsibility, boundary, dependency, change route, or risk. If the map is broadly stale or its module split is wrong, report that a `codebase-atlas` refresh/rebuild is needed instead of silently running one.

## Report

Report package results, Shared Verification, delivery, and any unresolved conflict. Never claim a package or batch is accepted when mandatory evidence is missing.
