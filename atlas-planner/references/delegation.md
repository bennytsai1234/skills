# Delegation

Single source of truth for the `atlas-planner` → human → `atlas-relay` →
`atlas-worker` workflow.

The planning-to-execution handoff is deliberately human-mediated. The planner
writes the packages and dispatch plan, then stops. The human hands the dispatch
plan to Relay. From that point, the handed-off batch is executed and accepted
between Relay and Worker; it does not normally return to Planner.

A human request for immediate results with no planning/acceptance step uses
`atlas-fast` instead.

## 1. The Loop

```text
Human      → states the need
Planner    1. understand and investigate
           2. align Before / After and any real decisions
           3. write task packages
           4. write dispatch plan and hand it to the human
Human      → gives the dispatch plan to Relay
Relay      5. read the plan and every package
           6. execute package 1
Worker     7. implement and verify package 1
Relay      8. independently accept package 1; return gaps if needed
           9. record/archive/deliver package 1
          10. execute package 2, then repeat
          11. after the last accepted package, run Shared Verification
          12. archive the dispatch plan, refresh affected atlas facts, report
```

**Execution is strictly sequential.** Only one package/worker may be active at a
time. Relay does not dispatch the next package until the current one has been
accepted and recorded.

The human may ask Relay for status or add requirements during the batch. An
addition stays in the existing package only while that package keeps the same
Goal. A different Goal is a new task, not an expansion of the old package.

## 2. Roles

### Planner (`atlas-planner`)

Owns the human-alignment and specification side:

- understand vague requests;
- read the atlas and relevant code;
- reproduce/diagnose bugs before specifying a fix;
- settle product decisions that cannot be inferred from the repository;
- run the Before / After gate;
- cut work into task packages;
- write the dispatch plan;
- write atlas/Architecture Decision material on the planning side.

Planner normally writes specification, not source code. After handoff, the batch
belongs to Relay and Worker. Planner reviews the finished result only when the
human explicitly asks for a second pass.

### Relay (`atlas-relay`)

Owns execution management after the human handoff:

- read the dispatch plan and all named packages;
- execute packages in the plan's order, one at a time;
- choose the package's declared execution route, or an equivalent route when the
  Goal is unchanged;
- wait without interfering with the active worker;
- independently re-run decisive Acceptance checks;
- return precise gaps to the same worker/package;
- record accepted work, archive it, commit/push it according to policy;
- run final Shared Verification;
- refresh affected atlas facts from accepted completion records;
- report the batch to the human.

Relay may repair non-semantic execution details when intent is unchanged. It does
not invent a new Goal. If a package cannot be completed without changing its
Goal, Relay reports that concrete conflict to the human.

### Worker (`atlas-worker`)

Owns one package's implementation:

- explore beyond Starting Points as needed;
- choose the implementation from Goal, Background, Acceptance, code, and
  Constraints;
- edit all required source/test files;
- add/extend tests when useful evidence;
- run checks needed to establish Acceptance;
- fix returned `## Gaps` lists;
- report changed files, root cause, real verification output, risks, and anything
  Relay must handle.

Worker does not write change-management records, archive packages, commit, push,
or manage batch order.

## 3. Role Resolution

Resolve from the received instructions:

| Header / input | Role |
|---|---|
| `ROLE: worker` | Worker — use `atlas-worker` |
| `ROLE: relay-lead`, or a dispatch plan | Relay — use `atlas-relay` |
| no role header, human discussing what to build | Planner — use `atlas-planner` |

Governance ownership:

| File | Writer |
|---|---|
| Atlas docs / Architecture Decisions (planning side) | Planner |
| `docs/changes/planning/**` initial packages + dispatch plan | Planner |
| `Completion record` | Relay |
| `docs/changes/completed/**` | Relay |
| Source and tests | Worker |
| Implementation commits/pushes | Relay |

## 4. Dispatch Plan

The human hands Relay exactly one entry file: the dispatch plan. It names all
packages. Write one even for a single package so the receiving agent resolves to
Relay rather than Worker.

```markdown
---
ROLE: relay-lead
CONTRACT: atlas/v3
MODEL: GPT-5.6-Luna
REASONING: Max
DELIVERY_POLICY: <no commit | commit only | commit and push>
REPORTING_LEVEL: <plain | technical>
---

# <batch title>

## Objective
<what is true when the whole batch is done>

## Task Packages
| # | Package | Route | Goal |
|---|---|---|---|
| 1 | `docs/changes/planning/{{DATE}}-{{SLUG}}.md` | `gpt-subagent` or `claude-p` | <one line> |

## Execution Order
<the exact package order and any dependency reason>

## Shared Verification
<authoritative final check over the whole tree, with expected result>

## Completion Protocol
<any batch-specific delivery requirement; otherwise use §10>
```

## 5. Task Package (`atlas/v3`)

```markdown
---
ROLE: worker
CONTRACT: atlas/v3
TASK_TYPE: implement        # implement | investigate | review
MODEL: GPT-5.6-Luna         # Claude Sonnet 5 for frontend/UI
EXECUTION_ROUTE: gpt-subagent  # claude-p for frontend/UI
REASONING: Max              # GPT only; omit for Claude
REPORTING_LEVEL: plain      # plain | technical
---

## Goal
<one sentence: what must be true when done>

## Background
<what a worker with zero conversation history cannot infer>

## Acceptance
- <checkable command/behavior plus expected result>
- <negative case when relevant>
- <what must not change>

## Constraints (only when needed)
- <real requirement the repository/ordinary engineering judgment cannot infer>

## Starting Points (optional)
- <module/symbol/route that helps orientation>

## Evidence
- Actual output for Acceptance checks.
- Tests/checks run and remaining risks.

## Completion record
<left empty by Planner; filled by Relay only after acceptance>
```

For frontend/UI packages:

```yaml
MODEL: Claude Sonnet 5
EXECUTION_ROUTE: claude-p
```

Do not add `REASONING` to Claude packages.

### Package quality

A package is portable: a competent worker with no chat history can understand the
Goal, find the code, choose an implementation, and prove the result.

- `Background` contains only context the worker cannot derive cheaply: current
  behavior, wrong examples, real inputs/outputs, prior inventory, analysis limits.
- `Constraints` contains only genuine non-inferable requirements.
- `Acceptance` is objectively checkable. "Works correctly" is not enough.
- Prefer exact expected values and observable behavior.
- Cover important negative behavior and say what must not change.
- If a check may depend on an unavailable resource, say whether it is conditional
  or skippable and what evidence still remains required.
- Write one shell command per line and use paths relative to the repository with
  forward slashes.
- `Starting Points` is a map, not a fence. The worker follows real dependencies.

## 6. Sequential Execution, Waiting, and Human Additions

### Sequential execution

Relay runs exactly one package at a time:

```text
package 1 → worker → accept → record/archive
package 2 → worker → accept → record/archive
package 3 → ...
```

Do not dispatch package 2 while package 1's worker is active or while package 1
is still awaiting acceptance.

This makes each package's diff, build, test, and commit attributable to one worker
at a time.

### Waiting

Use the route's completion mechanism, never `sleep`.

GPT:

```text
spawn_agent(...) → agent_id
wait_agent(targets = [agent_id], timeout_ms = 3600000)
```

Claude:

```text
claude --model claude-sonnet-5 -p "..." → process exit
```

A GPT wait timeout means the worker is still running. Wait again; do not
re-dispatch merely because the wait call timed out.

While a worker is in flight, the tree belongs to it: Relay does not run
`git status`, inspect diffs, build, test, or start another worker.

### Human additions

The human may add something during the batch.

- **Same Goal** → append/merge the addition into that package, make its
  Acceptance/Constraints consistent, and re-run as needed.
- **Different Goal** → keep it separate from the existing package. It is new
  work, not a reason to stretch the old package.
- **Addition arrives while Worker is active** → queue it until the worker returns;
  do not edit underneath an active worker.

Relay organizes the human's words but does not reinterpret them into a new
product requirement.

### Relay task adjustments

Relay may repair execution details without reopening planning when intent stays
unchanged:

- unambiguous metadata;
- stale paths;
- an invalid verification command replaced by an equivalent one;
- an equivalent worker or execution route;
- package-local execution detail needed to carry out the same Goal.

Record each adjustment as original → revised, reason, and why intent is unchanged.
If the correction would change Goal, Acceptance meaning, or an important
Constraint, stop that package and report the conflict to the human.

## 7. Shortcut Patterns

Do not substitute making a check pass for solving the problem.

Watch for:

- hardcoded special cases;
- swallowed exceptions;
- duplicated logic instead of an existing abstraction;
- production branches that exist only for tests;
- fixes applied downstream of the real cause;
- weakened/deleted assertions;
- relaxed thresholds/rules solely to obtain green output.

Any of these may be legitimate when the requirement actually calls for it. The
problem is using one silently to satisfy Acceptance. Explain deliberate changes
of this kind in the Worker report so Relay can judge them.

Before editing, Worker identifies the root cause, checks for an existing
abstraction, and asks whether the fix would duplicate logic.

## 8. Worker Report

```markdown
## Changed
- <file>: <what changed and why>

## Root Cause
<cause and why this is the correct layer to fix>

## Verification
- <command>
  <actual output, pasted>
- <other Acceptance evidence>
- <when relevant: unavailable resources and equivalent evidence>

## Risks
- <remaining uncertainty>
- <or: none>

## Needs Relay
- <execution/spec conflict Relay must handle>
- <or: none>
```

Evidence is actual output, not "passed". Do not include exploration narrative or
restate the package.

### When a package cannot be executed as written

Worker reports the concrete contradiction, false premise, unavailable capability,
or unsatisfied Constraint to Relay.

Relay first checks whether an equivalent execution adjustment preserves the same
Goal. If yes, record it and continue. If not, leave the package in `planning/`
and report the conflict to the human. Do not quietly reinterpret the Goal.

## 9. Acceptance

Relay acceptance is the gate.

- Re-run decisive Acceptance checks against the actual environment.
- Read the diff against the Goal and explicit Constraints.
- Check §7 shortcut patterns.
- Compare Worker-reported risks/resource limits with reality.
- A missing resource is not automatically rejection if the package explicitly
  allows a conditional/skippable check or equivalent evidence establishes the
  same result.
- Never accept a package when a mandatory core result cannot reasonably be
  established.

When something fixable is wrong, return only the gaps:

```markdown
## Gaps
1. <file:line> — <what is wrong, and what fixed looks like>
2. <...>

Everything else is accepted. Change nothing outside these points.
```

The same package/worker loop continues until Relay accepts it or discovers a
conflict that cannot be solved without changing the Goal.

## 10. Completion Protocol

Package lifecycle is represented by its location:

```text
docs/changes/planning/   = not yet accepted
docs/changes/completed/  = accepted and recorded
```

After Relay accepts one package:

1. Fill `Completion record` while the package is still in `planning/`:
   - Task adjustments, or `none`;
   - what actually changed;
   - real Acceptance/verification values;
   - unavailable resources and substituted/skipped checks when relevant;
   - the basis for acceptance when evidence was conditional;
   - boundary, ownership, or external-contract changes;
   - known limits and residual risk.
2. Move it to `docs/changes/completed/{{DATE}}/{{SLUG}}.md`.
3. Append one line to `docs/changes/completed/{{DATE}}/summary.md`.
4. Commit/push code plus the change record according to `DELIVERY_POLICY`.
5. Only then start the next package.

After the last package is accepted:

1. Run `Shared Verification` on the final tree.
2. If it succeeds, move the dispatch plan to
   `docs/changes/completed/{{DATE}}/{{SLUG}}-dispatch-plan.md`.
3. Refresh affected atlas facts from Completion records that flagged boundary,
   ownership, or contract changes.
4. Report the batch to the human.

If an existing package cannot be accepted without changing its Goal, it and the
dispatch plan remain in `planning/`. Already accepted packages remain archived
in `completed/`. Relay reports the concrete conflict to the human.

## 11. Cost and Context Discipline

- Specify once, completely. A thin package makes Worker rediscover what Planner
  already knew.
- Run one package at a time and finish its acceptance/recording before the next.
- While Worker is active, Relay leaves the tree alone.
- Worker receives the package, not chat history or Relay commentary.
- Carry conclusions forward instead of repeatedly rereading the atlas.
- Split by real change boundary or risk isolation, not by file count.
- Review/accept against the whole returned change once per worker round.
