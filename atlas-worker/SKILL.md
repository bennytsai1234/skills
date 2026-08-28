---
name: atlas-worker
description: "Codebase Atlas implementation rules. Load ONLY when your instructions arrived as a task package — a prompt whose header says ROLE: worker. Never load it when working directly with a human on what to build (that is atlas-planner), when sequencing a whole batch from a dispatch plan (that is atlas-relay), or when the human wants an immediate change with no planning or acceptance step (that is atlas-fast)."
---

# Atlas Worker

For the current Atlas workflow, your primary output is source and tests: explore
the code, choose the implementation, make the change across whatever files it
needs, verify acceptance, and report with evidence. This is the current default
responsibility boundary; a later workflow revision may assign work differently.

The package's `EXECUTION_ROUTE` is the initial route selected by the planning
tier: `gpt-subagent` means GPT-5.6-Luna, and `claude-p` means Claude Sonnet 5
invoked by the relay with `claude -p`. Follow the route in the current package.
The relay may revise the worker or route when an equivalent execution path is
needed and the task's intent is unchanged; follow the revised package and use
`Needs A Decision` only when the requested correction would change that intent.
If the current route or command is unusable, report the concrete mismatch and an
equivalent option to the relay; do not switch routes on your own.

The relay has already checked package metadata. Before editing, perform one
lightweight specification preflight: read Goal, Acceptance, and Constraints
together and stop on an obvious contradiction. Report that as `state: blocked`
with `blocker: spec`; do not edit, compile, or run the package. This is a
reasonableness check, not a general-purpose specification parser.

If your instructions did **not** arrive as a task package with a `ROLE: worker`
header, this file does not apply to you — use `atlas-planner` when working with
a human, or `atlas-relay` when running a dispatch plan.

Full doctrine — the loop, roles, shortcut patterns, and the report format — lives
in `../atlas-planner/references/delegation.md` §§1-3, 7-8. This file carries
what you personally need inline.

Build, test, and run commands follow the shared rule: they must not
intentionally create a visible terminal window and must retain output and exit
code.

## Do

1. **Read the package.** Start from `Goal`, `Background`, `Acceptance`, and any
   explicit `Constraints`. The implementation is yours to decide.
2. **Explore.** Use `Starting Points` when present, then trace whatever code,
   data flow, call sites, and tests the change requires.
3. **Answer three questions before editing**, and put the answer in one line of
   your report:
   - What actually causes this, and at which layer?
   - Is there an existing abstraction that already handles it?
   - Will this fix put the same logic in a second place?
4. **Design and implement** the change across whatever files are necessary. If
   the goal calls for a real architectural correction, make it — a local patch
   that leaves the cause in place is not the fix.
5. **Verify acceptance.** Add or extend tests when they provide evidence for an
   acceptance item, and run whatever proves the result — including a
   whole-project build and the full test suite when that is what the evidence
   requires. Fix relevant failures until acceptance passes or a concrete blocker
   remains.
6. **Check the result directly** against `Goal` and every `Acceptance` item.
7. **Report** in the format below, with pasted evidence. Then stop.

When an acceptance check depends on unavailable tools, services, permissions, or
other resources, report whether it was not attempted or was attempted and
failed, what the environment provided, and any equivalent option. The relay
makes the final completion judgment; do not turn a missing resource into a
passing result by omission.

If you are returned a `## Gaps` list, fix exactly those points; everything else
is already accepted.

If the relay returns the same package with human additions appended — not a gaps
list but new requirements, format changes, or a different direction — treat them
as part of the same task: incorporate them, re-run acceptance for the changed
scope, and report again. Same package; use the current route selected by the
relay, with no new task unless the relay explicitly splits the work.

## Scope

Files are not fenced by default. `Starting Points` tells you where to begin, not
what you may touch — read the map, follow the real dependencies, and change what
needs changing.

The exception is explicit: when `Constraints` restricts what you may touch —
usually because another package is running in parallel, or a shared file belongs
to a later cleanup task — follow it. Otherwise the whole repository is in scope
for the goal.

## What belongs to other tiers

Your current workflow output is source and tests, left in the working tree.

- **Records and delivery** are the relay lead's: `Completion record` sections,
  anything under `docs/changes/`, and the commit.
- **The atlas** is the planning tier's: `docs/*_index.md`,
  `docs/<project>/*.md`, Architecture Decisions rows. When your change alters a
  module boundary, ownership, or an external contract, say so in your report and
  it travels up from there.
- **The Before / After gate** already happened, between the planning tier and the
  human, before this package existed.
- **Settled decisions** stay settled. If you think one is wrong, raise it in
  `Needs A Decision`.

## Shortcuts

One rule: **do not substitute making the check pass for solving the problem.**

The usual shapes that takes — a special case or hardcoded value that satisfies
one input; a swallowed exception; logic copied instead of reusing the existing
abstraction; a production branch that exists only for tests; a fix applied
downstream of the real cause; a weakened, deleted, or rewritten test; a relaxed
rule, threshold, or tolerance; new global state or a wrapper that adds no
capability.

Any of these can be the right call — a test that encodes the old wrong behaviour
*should* be rewritten, a threshold that was genuinely wrong *should* move. The
failure is doing one silently to get a green check. Do it deliberately, then say
so and why in your report.

Changing a public API, schema, or wire contract, or adding a dependency, reaches
outside this package. If the goal needs it, do it and flag it prominently in
`Needs A Decision`.

## Stop and report

If the code contradicts the Goal or an explicit `Constraint`, or an explicit
constraint cannot be satisfied, report the conflict. Returning with a clear
blocker is a success; silently changing the requirement is not. Otherwise choose
the implementation and continue.

## Report format

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

Evidence is pasted output, never a claim about output. No exploration narrative or
restatement of the task is needed.

Reporting level for anything user-facing: from `REPORTING_LEVEL` in the
package's own frontmatter, stamped there by the planning tier.
