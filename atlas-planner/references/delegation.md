# Atlas Delegation Contract

Single source of truth for the formal `atlas-planner` -> human -> `atlas-relay` -> `atlas-worker` workflow.

Ordinary development does not use this contract; it is handled directly without an atlas skill. Formal planning uses this contract because the human explicitly wants discussion, decomposition, handoff, and independent acceptance.

## 1. Loop

```text
Human   -> states the need and discusses it with Planner
Planner -> investigates, diagnoses, proposes solution, revises with human
Human   -> explicitly confirms problem + target + solution
Planner -> writes detailed task packages + one dispatch plan
Human   -> hands dispatch plan to Relay
Relay   -> executes package 1
Worker  -> implements and verifies package 1
Relay   -> independently accepts; returns gaps if needed
Relay   -> records/delivers package 1
Relay   -> repeats for the next package, strictly in sequence;
           at a stop point, hands back to the human before continuing
Relay   -> runs final shared verification and reports the batch
```

The Planner confirmation gate happens before any package is written. The later human handoff to Relay authorizes execution of the confirmed plan.

## 2. Roles

### Planner

Owns:

- discussion with the human;
- repository investigation;
- root-cause diagnosis;
- target-state and solution design;
- resolving real product/compatibility decisions;
- decomposition;
- detailed task packages;
- dispatch plan.

Planner writes specifications, not production source code.

### Relay

Owns:

- reading the dispatch plan and all packages;
- sequential execution;
- resolving the concrete executor for each route;
- waiting without interfering with active workers;
- independent acceptance;
- returning precise gaps;
- completion records (commit messages or the Relay report) and removing accepted packages from the queue;
- delivery according to the plan/project policy;
- final shared verification.

### Worker

Owns one package's implementation:

- read the detailed package;
- inspect enough live code to implement it correctly;
- follow the confirmed solution unless real code proves an implementation detail invalid;
- edit source/tests;
- run acceptance evidence;
- report actual output, risks, and any conflict Relay must resolve.

Worker does not plan the batch, archive packages, commit/push, or rewrite the agreed Goal.

## 3. Role resolution

| Input | Role |
|---|---|
| `ROLE: worker` | Worker / `atlas-worker` |
| `ROLE: relay-lead` or dispatch plan | Relay / `atlas-relay` |
| human explicitly asks for planner / `atlas-planner` | Planner / `atlas-planner` |
| ordinary direct development | direct handling (no atlas skill) |

## 4. Dispatch plan (`atlas/v4`)

```markdown
---
ROLE: relay-lead
CONTRACT: atlas/v4
DELIVERY_POLICY: no commit | commit only | commit and push
---

# <batch title>

## Objective
<what is true when the whole batch is complete>

## Task Packages
| # | Package | Route | Goal | Stop |
|---|---|---|---|---|
| 1 | `docs/changes/planning/...md` | `gpt-subagent` or `claude-p` | ... | `yes` / `no` |

## Execution Order
<exact order and real dependency reason>

## Shared Verification
<final check over the integrated tree and expected result>
```

The plan names route classes, not model versions. Relay maps a route to the current supported executor.

`Stop: yes` marks a package after which Relay delivers and hands back to the human: a spike's go/no-go, or Human Verification that later packages depend on.

## 5. Task package (`atlas/v4`)

```markdown
---
ROLE: worker
CONTRACT: atlas/v4
TASK_TYPE: implement | investigate | review
EXECUTION_ROUTE: gpt-subagent | claude-p
---

## Goal
<one independently understandable engineering result>

## Problem / Root Cause
<confirmed problem and, for bugs, the diagnosed direct cause>

## Background
<context the worker cannot cheaply infer from the repository>

## Recommended Solution
<the solution direction confirmed with the human; include concrete technical detail or pseudocode when useful>

## Implementation Steps
1. <meaningful ordered step>
2. <...>

## Expected Change Surface
- <likely module / area / contract; not a hard fence>

## Acceptance
### Agent Verification
- <command or observable behavior an agent can run here, plus expected result>
- <important regression/negative case when relevant>
- <what must not change>

### Human Verification
- <check that needs a remote/GPU host, desktop app, browser, mic/camera, production-like infrastructure, or human judgment; omit when none>

## Constraints
- <only real non-inferable requirements; omit when none>

## Starting Points
- <symbols, routes, tests, or files that accelerate orientation>

## Completion record
<left empty by Planner; Relay fills it only after acceptance>
```

### Package quality

A package is portable when a competent worker with no chat history can understand the problem, follow the confirmed solution, find the code, implement it, and prove the result.

- Do not make Worker rediscover Planner's root cause or product decision.
- `Recommended Solution` may be prescriptive about architecture, data/state ownership, APIs, ordering, and failure behavior when those were part of the confirmed solution.
- `Implementation Steps` are a concrete route, not a transcript or line-by-line patch.
- `Expected Change Surface` and `Starting Points` are maps, not fences.
- `Acceptance` is objective. "Works correctly" is not acceptance.
- Agent Verification proves the core result; Human Verification lists only what an agent cannot run.
- When the direction rests on an unproven assumption, the first package is an `investigate` spike with go/no-go criteria and `Stop: yes`.
- Split packages by independently verifiable engineering result and dependency boundary, not by file count.

## 6. Sequential execution

Relay runs exactly one package at a time:

```text
package 1 -> worker -> accept -> record/deliver
package 2 -> worker -> accept -> record/deliver
...
```

Do not start the next worker while the current package is active or awaiting acceptance. This keeps each diff and verification attributable to one package.

After a `Stop: yes` package is accepted and delivered, Relay reports the result (spike go/no-go evidence, or the Human Verification checklist) and waits for the human before starting the next package.

### Environment blockers

An environment blocker is something outside the repository that the work needs but the agent cannot fix by command within the package: Docker or another daemon not running, a host or service unreachable, missing credentials or permissions, a step that needs a GUI, browser, microphone, or a person.

- Use the repository's scripted, headless way to start local services when one exists.
- If a direct attempt fails, or fixing it would mean changing things outside the repository (system services, desktop apps, hosts, credentials), stop. Worker reports it under `Needs Relay`; Relay tells the human what is blocked and the smallest action that unblocks it, then waits.
- Do not cycle through workarounds, swap in a different environment, or weaken Acceptance to get past the blocker.

Use the executor's completion primitive. A wait timeout means "still running" unless the tool explicitly reports failure; do not redispatch merely because a wait call timed out.

While a worker is active, Relay does not edit underneath it or launch a second worker on the same tree.

## 7. Implementation adjustments

The confirmed Goal and solution direction are authoritative. Real code may still invalidate a package-local implementation detail.

Worker reports the concrete mismatch. Relay may approve an equivalent adjustment when it preserves:

- the same Goal;
- the same user-confirmed solution intent;
- Acceptance meaning;
- important Constraints and external contracts.

Record the adjustment in the Completion record. If the only viable correction changes the Goal or solution intent, stop and return the conflict to the human instead of silently redesigning the task.

## 8. Worker evidence

Worker reports:

```markdown
## Changed
- <file>: <what changed and why>

## Root Cause / Implementation
<why the change solves the package problem and whether any recommended detail had to be adjusted>

## Verification
- <command/check>
  <actual output>

## Risks
- <real remaining uncertainty>

## Needs Relay
- <conflict/adjustment request>
```

Omit `Risks` and `Needs Relay` when there is nothing to report. Evidence is actual output or observable result, not a claim that something passed.

## 9. Acceptance

Relay acceptance is independent of Worker confidence.

- Re-run decisive checks when the environment provides what they need.
- Inspect the diff against Goal, Recommended Solution, Acceptance, and Constraints.
- Reject test-only shortcuts, weakened assertions, swallowed failures, duplicated logic, or downstream patches that leave the diagnosed cause in place unless the confirmed solution intentionally requires them.
- Missing infrastructure is not automatic rejection when the package explicitly allows conditional evidence, but a mandatory core result may never be called accepted without reasonable proof.
- Relay accepts on Agent Verification. Human Verification items are not attempted beyond what the tools can actually drive; they go to the human as a checklist in the report.

When a fixable gap exists, return only the gaps to the same package/worker.

## 10. Completion protocol

`docs/changes/planning/` is a work queue, not an archive: it holds only packages that are not yet accepted and the running dispatch plan. Completed work is recorded in git commit messages, not in files.

After accepting a package, Relay:

1. writes the `Completion record` (actual changes, adjustments, verification, unavailable resources, residual risk);
2. if the accepted work established a lasting rule that future work in this repository must follow, adds it to the repository `AGENTS.md` as a plain rule; residual risk stays in the completion record;
3. deletes the package file;
4. applies `DELIVERY_POLICY`, putting the completion record in the commit message body when it commits; under `no commit` the record goes into the Relay report;
5. then starts the next package.

After the last package, run Shared Verification. If it succeeds, delete the dispatch plan, remove `docs/changes/planning/` (and `docs/changes/`, `docs/`) when empty.

## 11. Cost and context discipline

- Discuss and discover once in Planner; carry those conclusions into packages.
- Do not paste chat history into Worker prompts.
- One package at a time.
- Split only when the split improves ownership, dependency clarity, failure isolation, or acceptance.
- Do not repeat full-repository exploration in every tier.
