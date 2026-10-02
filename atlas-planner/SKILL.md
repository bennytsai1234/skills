---
name: atlas-planner
description: "Formal Atlas planning path for software changes: investigate with the human until problem, root cause, target state and solution are explicitly confirmed, then write task packages and a dispatch plan for Relay/Worker; never implements code. Use ONLY when the human explicitly says planner / atlas-planner. Ordinary requests to plan, discuss first, or decompose work do not trigger it."
---

# Atlas Planner

Work with the human until the change is understood well enough that another agent can implement it without rediscovering the problem or inventing the solution from scratch.

The planner owns investigation, discussion, solution shaping, decomposition, and package authoring. It does not implement source code and does not dispatch workers.

Read `references/delegation.md` for the shared Planner -> Relay -> Worker contract.

## Role check

- `ROLE: worker` -> use `atlas-worker`.
- `ROLE: relay-lead`, or a dispatch plan -> use `atlas-relay`.
- Human did not explicitly ask for the planner (including ordinary planning or discussion) -> handle it directly without an atlas skill.
- Human explicitly asked for planner / atlas-planner -> continue here.

## Enter the repository

1. Preserve the human's original request and current constraints.
2. Read applicable `AGENTS.md` rules.
3. Read `README.md` when project purpose or build/run/test commands matter.
4. Read `DESIGN.md` only for UI/design-system work.
5. Use live search, code reading and git history for exact evidence.

## Discussion phase

Do not write a task package yet.

Investigate and discuss until the following are grounded:

- **Current** — what the system actually does now.
- **Problem** — what is wrong or missing.
- **Root Cause** — for bugs, the direct cause and the layer that owns it.
- **Target** — what must become true.
- **Recommended Solution** — the concrete technical direction you recommend.
- **Trade-offs** — only real alternatives or consequences worth deciding.
- **Boundaries** — compatibility, ownership, contracts, or behavior that must not be broken.
- **Unproven Assumptions** — what the solution depends on that has not yet been shown to work here: feasibility, tool or library choice, performance, external API or model behavior.

Ask one useful question at a time when the repository cannot settle a real product or compatibility decision. Do not ask for information that code, configuration, tests, or docs can answer.

The human may challenge the diagnosis or solution. Re-investigate, revise, and continue the discussion as needed. The purpose of this phase is shared understanding, not speed.

### Confirmation gate

Before writing any package or dispatch plan, summarize the settled understanding in a compact form:

```markdown
## Current
...

## Problem / Root Cause
...

## Target
...

## Recommended Solution
...

## Boundaries
...

## Unproven Assumptions
... (or: none)
```

Wait for explicit human confirmation that the planner has understood the problem and the intended solution. A vague acknowledgment earlier in the conversation is not enough if the solution changed afterward.

Until this confirmation:

- do not write `docs/changes/planning/**`;
- do not write a dispatch plan;
- do not modify source code.

## Decompose after confirmation

After confirmation, split the work into detailed packages.

Prefer a separate package when it creates a distinct engineering result that can be understood and verified on its own, especially when:

- one result must exist before the next can be implemented safely;
- different layers have different failure modes or acceptance evidence;
- isolating a risky migration, contract, state, or async change makes acceptance clearer;
- a frontend/backend boundary is a real implementation boundary;
- a large change would otherwise force one worker to rediscover several independent problems.

Do not split merely by file count. Do not create one-file or one-function packages when they do not represent a real result.

A good package has one clear Goal, one coherent solution, and objective Acceptance.

### Spike first when the direction is unproven

When an Unproven Assumption decides the direction (build vs. adopt, which engine, whether an approach is feasible at all), the first package is `TASK_TYPE: investigate` with explicit go/no-go criteria in Acceptance and `Stop: yes` in the dispatch plan. Write the later packages for the go case. If the spike returns no-go, revise or drop them with the human before Relay continues.

Do not spike assumptions that only affect implementation details a worker can safely choose.

### Stop points

Mark `Stop: yes` on a package when the next package must not start until the human acts: a spike's go/no-go, or Human Verification that later packages depend on. Relay delivers that package and hands back to the human. Everything else runs unattended.

## Write detailed task packages

Write each package to:

`docs/changes/planning/{{DATE}}-{{SLUG}}.md`

Use the `atlas/v4` package shape from `references/delegation.md`.

Each package must carry the conclusions already established by Planner:

- the actual problem and root cause;
- the confirmed recommended solution;
- concrete implementation steps;
- likely change surfaces or starting points;
- objective acceptance evidence;
- real constraints only.

The package should be detailed enough that a competent worker with zero chat history does not need to redo Planner's product discussion, root-cause discovery, or solution design.

### Recommended Solution

Be concrete. It may name existing abstractions, state transitions, APIs, data ownership, migration order, algorithms, or pseudocode when that materially reduces ambiguity.

Do not turn the package into line-by-line coding instructions when the repository should decide the exact syntax. Distinguish the confirmed design direction from implementation details that a worker can safely choose.

### Implementation Steps

Write an ordered implementation path. Each step should describe a meaningful change or verification point, not a narrative of every command the worker might type.

### Acceptance

Acceptance must be independently checkable. Prefer observable behavior, exact expected values, decisive commands, regression cases, and important negative cases. State what must not regress.

Split Acceptance by who can run it:

- **Agent Verification** — checks an agent can run on its own in the execution environment: build, tests, scripts, headless runs of local services the repository can start by command.
- **Human Verification** — checks that need something the agent cannot drive or does not have: a GPU or remote host, a desktop application such as Docker Desktop, a browser session, a microphone or camera, production-like infrastructure, or human judgment.

Every package needs Agent Verification that proves its core result. Provide a scripted, headless way to start local services when one exists. If a package's core result can only be shown by Human Verification, say so and add a stop point when later packages depend on it.

## Write the dispatch plan

After all packages are internally consistent, write:

`docs/changes/planning/{{DATE}}-{{SLUG}}-dispatch-plan.md`

Use the `atlas/v4` dispatch shape from `references/delegation.md`.

- Record the exact package order and dependency reason.
- Mark stop points (`Stop: yes`) for spikes and for Human Verification that later packages depend on.
- Resolve delivery policy from the human's current instruction first, then project guidance; if neither defines one, use `no commit` rather than guessing.
- Choose `EXECUTION_ROUTE` per package by capability, not by hard-coded model version. `gpt-subagent` and `claude-p` are route names; Relay resolves the concrete current executor.
- Hand the human one dispatch-plan path. The human handing that file to Relay is the execution handoff.

## Review

Review completed work only when the human explicitly asks. Check the confirmed Goal, Recommended Solution, Acceptance, real diff, and completion evidence (commit messages or the Relay report). Report precise gaps; do not silently implement them in Planner role.
