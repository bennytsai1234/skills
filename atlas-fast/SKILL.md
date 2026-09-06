---
name: atlas-fast
description: "Default execution path for ordinary development work. Use when the human asks to investigate, fix, change, build, implement, or adjust something and does not explicitly request formal planning, task packages, dispatch, or independent acceptance. If a Codebase Atlas exists, use it for navigation before live search. Route explicit planning/discussion work to atlas-planner, dispatch plans to atlas-relay, and ROLE: worker packages to atlas-worker."
---

# Atlas Fast

Handle ordinary development with the least process needed to reach a correct result.
Do not create task packages, dispatch plans, completion records, or a formal acceptance loop.

## Route first

- `ROLE: worker` -> use `atlas-worker`.
- `ROLE: relay-lead`, or a dispatch plan -> use `atlas-relay`.
- Human explicitly asks to discuss first, plan, decompose, write packages, dispatch, or run formal acceptance -> use `atlas-planner`.
- Otherwise continue here, including read-only investigation and normal implementation work.

## Navigate

1. Read the applicable `AGENTS.md` rules.
2. If a Codebase Atlas exists under `docs/`, read its index once.
3. Read only the module docs relevant to the request.
4. Use live search (`rg`, symbol search, call hierarchy, tests) for exact locations.
5. If no atlas exists, do not stop or build one automatically; inspect the repository normally unless the human explicitly asks for an atlas.

The atlas is a routing layer, not a substitute for reading code.

## Investigate

For explanation, review, or diagnosis requests:

- inspect only enough code and evidence to answer the question;
- separate confirmed facts, inference, and unknowns;
- for bugs, establish the direct cause when the available environment makes that practical;
- do not modify source code unless the human also asked for a change.

## Change

For implementation requests:

1. Identify the real problem and the correct change surface.
2. Check whether an existing abstraction already owns the behavior.
3. Choose the smallest sufficient fix that preserves existing architecture unless that architecture is the cause.
4. Implement across every file genuinely required by the goal.
5. Run the smallest decisive verification first. Expand only for new failures, meaningful uncertainty, or higher-impact changes.
6. Follow the current user instruction and project `AGENTS.md` for commit/push behavior. This skill does not impose its own delivery policy.

Do not keep exploring once the change surface and implementation are clear. Do not add preventive refactors, unrelated documentation, speculative features, or a formal workflow merely because the task is large.

## Report

Report the result, decisive evidence, and any real remaining limitation. Keep implementation narration short.
