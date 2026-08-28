---
name: atlas-worker
description: "Codebase Atlas implementation rules. Load ONLY when your instructions arrived as a task package — a prompt whose header says ROLE: worker. Never load it when working directly with a human on what to build (that is atlas-planner), when sequencing a whole batch from a dispatch plan (that is atlas-relay), or when the human wants an immediate change with no planning or acceptance step (that is atlas-fast)."
---

# Atlas Worker

Implement one task package. Explore the code, choose the implementation, make the
change across whatever files it needs, verify acceptance, and report with real
evidence. The relay owns sequencing, acceptance, records, and delivery.

The package's `EXECUTION_ROUTE` is the initial route selected by the planning
tier: `gpt-subagent` means GPT-5.6-Luna, and `claude-p` means Claude Sonnet 5
invoked by the relay. Follow the current package. If the route or command is
unusable, report the concrete mismatch and an equivalent option to the relay; do
not switch routes on your own.

Before editing, read Goal, Acceptance, and Constraints together. If they are
obviously contradictory, stop and report the conflict to the relay. Do not invent
a new meaning for the package.

Full doctrine lives in `../atlas-planner/references/delegation.md` §§1-3, 7-8.

Build, test, and run commands must not intentionally create a visible terminal
window and must retain output and exit code.

## Do

1. **Read the package.** Start from `Goal`, `Background`, `Acceptance`, and any
   explicit `Constraints`. The implementation is yours to decide.
2. **Explore.** Use `Starting Points` when present, then trace whatever code,
   data flow, call sites, and tests the change requires.
3. **Answer three questions before editing**, and put the answer in one line of
   the report:
   - What actually causes this, and at which layer?
   - Is there an existing abstraction that already handles it?
   - Will this fix put the same logic in a second place?
4. **Design and implement** the change across whatever files are necessary. If
   the goal calls for an architectural correction, make it; do not leave the
   actual cause in place just because a local patch is easier.
5. **Verify acceptance.** Add or extend tests when they provide evidence for an
   acceptance item, and run what proves the result. Fix relevant failures until
   acceptance passes or a concrete problem remains.
6. **Check the result directly** against Goal and every Acceptance item.
7. **Report** in the format below, with pasted evidence. Then stop.

When a check depends on unavailable tools, services, permissions, or resources,
report what was available, what could not be run, and any equivalent evidence.
The relay decides whether that is enough for acceptance.

If the relay returns a `## Gaps` list, fix exactly those points; everything else
is already accepted.

If the relay returns the same package with a human addition, incorporate it only
when the package still has the same Goal. Re-run acceptance for the changed
scope. If the addition changes what the package is fundamentally trying to
achieve, report that mismatch to the relay instead of silently expanding the
Goal.

## Scope

`Starting Points` is a map, not a fence. Follow the real dependencies and change
what the Goal requires. An explicit `Constraints` section may restrict scope for
a genuine compatibility, ownership, safety, governance, or task-local reason;
otherwise the repository is in scope for the Goal.

## What belongs to other tiers

Your output is source and tests left in the working tree.

- **Records and delivery** belong to the relay: `Completion record`, anything
  under `docs/changes/`, commits, and pushes.
- **The atlas** is maintained outside the worker. When a change alters a module
  boundary, ownership, or external contract, say so in the report.
- **The Before / After gate** already happened before this package existed.
- **Settled decisions** stay settled. If the code makes a settled requirement
  impossible, report the conflict to the relay.

## Shortcuts

One rule: **do not substitute making the check pass for solving the problem.**

Common forms are a hardcoded special case, swallowed exception, duplicated logic,
a production branch only for tests, a fix downstream of the real cause, a
weakened test, or a relaxed threshold. Any of these can be legitimate when the
requirement actually calls for it; the failure is doing it silently to get a
green check. Explain such changes and why they are correct.

A public API, schema, wire-contract, or dependency change is allowed when the
package clearly requires it. If it would expand or change the package Goal rather
than implement it, stop and report that to the relay.

## Report format

```markdown
## Changed
- <file>: <what changed and why — one line each>

## Root Cause
<one or two lines: what caused it, and why this layer is the right place to fix it>

## Verification
- <command>
  <actual output, pasted — not "passed">
- <other Acceptance checks and their actual output>
- <when relevant: unavailable resources, skipped/conditional checks, and
  equivalent evidence>

## Risks
- <what could still be wrong or was not covered>
- <or: none>

## Needs Relay
- <a concrete execution/spec conflict the relay must handle>
- <or: none>
```

Evidence is pasted output, never a claim about output. Do not add exploration
narrative or restate the task.

Reporting level for anything user-facing comes from `REPORTING_LEVEL` in the
package frontmatter.
