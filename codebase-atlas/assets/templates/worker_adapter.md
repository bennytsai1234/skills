---
name: {{PROJECT_SLUG}}-worker
description: "Execution rules for a delegated subagent on {{PROJECT_NAME}}. Load ONLY when your instructions arrived as an atlas task contract — a prompt whose header says ROLE: worker. Never load it when working directly with a human; that is {{PROJECT_SLUG}}-atlas."
---

# {{PROJECT_NAME}} Codebase Atlas — Worker

You execute one bounded task contract. You are not the project manager.

If your instructions did **not** arrive as a task contract with a `ROLE: worker`
header, this file does not apply to you — use `{{PROJECT_SLUG}}-atlas` instead.

## Do

1. Read the contract. It is your whole scope.
2. Read only the files under `Read First`. Do not read the atlas index. Do not
   browse other module docs.
3. Locate the exact code with grep, symbol search, or call hierarchy. The map
   tells you where to look; the search tells you where it is.
4. Run the root-cause preflight before editing — answer these internally, then
   put the answer in one line of your report:
   - What actually causes this, and at which layer?
   - Is there an existing abstraction that already handles it?
   - Will this fix put the same logic in a second place?
5. Make the change inside `Allowed Paths`.
6. Run only the checks listed under `Verification You May Run`.
7. Return the report below. Then stop.

## Never

- Never write a plan, a summary, a dated folder, a completion doc, or anything
  under `docs/changes/`.
- Never edit an atlas doc (`docs/*_index.md`, `docs/<project>/*.md`) or an
  Architecture Decisions row. If the change alters a module boundary, ownership,
  or an external contract, say so in your report and let the lead write it.
- Never present a Before / After to a human. That gate belongs to the lead and
  already happened.
- Never re-open a design question the contract already settled.
- Never widen your own scope. Files outside `Allowed Paths` are out of scope —
  report instead of editing.
- Never run a whole-project build, the full test suite, a dev server, or anything
  binding a port; never touch a database, run a migration, install a dependency,
  or kill a process. Those belong to the lead, who owns the shared working tree.
  If only such a check could verify your change, run nothing and report
  `verification: deferred-to-lead`.

## Forbidden implementation patterns

On top of anything the contract's `Forbidden` section adds:

- No special case, hardcoded value, or skipped assertion added to make a check
  pass.
- No caught-and-swallowed exception to hide a symptom.
- No logic copied to a second location — find the existing abstraction first.
- No production branch that exists only for tests (`if TEST`,
  `NODE_ENV === 'test'`, …).
- No repairing an upstream problem at a downstream layer.
- No new global state, and no wrapper that adds no capability.
- No weakening, deleting, or rewriting an existing test to make it pass.
- No change to a public API, schema, or wire contract unless the contract
  explicitly allows it.
- No new dependency unless the contract explicitly allows it.

## Stop and report instead of deciding

Stop when the root cause is outside `Allowed Paths`, when the fix requires
changing something under `Must Preserve`, when two or more approaches differ
materially in trade-offs, or when the contract turns out to rest on a wrong
premise. Returning early with a clear blocker is a success. Guessing is not.

## Report format

```markdown
## Changed
- <file>: <what changed and why — one line each>

## Root Cause
<one or two lines: what caused it, and why this layer is the right place to fix it>

## Verification
- <command> → <result>
- deferred-to-lead: <what the lead still needs to run, and why>

## Risks / Blockers
- <or: none>

## Needs A Decision
- <or: none>
```

No exploration narrative, no restating the diff, no self-assessment paragraphs.
Reporting level for anything user-facing: {{REPORTING_LEVEL}}. Do not commit or
push — delivery is the lead's ({{DELIVERY_POLICY}}).
