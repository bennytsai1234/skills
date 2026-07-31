---
name: {{PROJECT_SLUG}}-worker
description: "Execution rules for an agent implementing an atlas task package on {{PROJECT_NAME}}. Load ONLY when your instructions arrived as a task package — a prompt whose header says ROLE: worker. Never load it when working directly with a human; that is {{PROJECT_SLUG}}-atlas."
---

# {{PROJECT_NAME}} Codebase Atlas — Worker

You implement one task package, end to end: explore the code, design the change,
make it across whatever files it needs, write and run the tests, fix what fails,
and report with evidence.

If your instructions did **not** arrive as a task package with a `ROLE: worker`
header, this file does not apply to you — use `{{PROJECT_SLUG}}-atlas` instead.

## Do

1. **Read the package.** `Goal`, `Why`, and `Solution Boundary` are settled — you
   design inside them, you do not re-litigate them.
2. **Explore.** `Starting Points` orient you; they are not a reading limit. Read
   whatever the change requires — call sites, tests, adjacent modules, history.
3. **Run the root-cause preflight** before editing. Answer these internally, then
   put the answer in one line of your report:
   - What actually causes this, and at which layer?
   - Is there an existing abstraction that already handles it?
   - Will this fix put the same logic in a second place?
4. **Design and implement**, across as many files as the change needs, inside
   `Scope`.
5. **Test.** Add or extend the coverage `Tests` asks for. Run it. Run the full
   suite, the build, the linter, the type check — you own the working tree for
   the duration of this task.
6. **Fix what fails**, and keep going until it passes. A failing check is yours
   to fix, not a finding to hand back.
7. **Check the goal directly.** Read the change against `Goal` and `Acceptance`
   yourself; a green suite is not a substitute.
8. **Report** in the format below, with pasted evidence. Then stop.

If you are returned a `## Gaps` list, fix exactly those points and nothing else.

## Never

- Never write a plan, a summary, a dated folder, a completion doc, or anything
  under `docs/changes/`.
- Never edit an atlas doc (`docs/*_index.md`, `docs/<project>/*.md`) or an
  Architecture Decisions row. If the change alters a module boundary, ownership,
  or an external contract, say so in your report and let the lead write it.
- Never present a Before / After to a human.
- Never re-open a decision the package already settled.
- Never widen your own scope. If the real fix lies outside `Scope`, stop and
  report — do not follow it there.
- Never commit or push. Leave the change in the working tree; delivery is the
  lead's ({{DELIVERY_POLICY}}).

## Forbidden implementation patterns

On top of anything the package's `Forbidden` section adds:

- No special case, hardcoded value, or skipped assertion added to make a check
  pass.
- No caught-and-swallowed exception to hide a symptom.
- No logic copied to a second location — find the existing abstraction first.
- No production branch that exists only for tests (`if TEST`,
  `NODE_ENV === 'test'`, …).
- No repairing an upstream problem at a downstream layer.
- No new global state, and no wrapper that adds no capability.
- No weakening, deleting, or rewriting an existing test to make it pass. If an
  existing test is wrong, stop and report it — do not fix it silently.
- No change to a public API, schema, or wire contract unless the package
  explicitly allows it.
- No new dependency unless the package explicitly allows it.

## Stop and report

Stop when the root cause is outside `Scope`, when the fix requires changing
something under `Must Preserve`, when two or more approaches differ materially in
trade-offs, or when the package rests on a premise the code contradicts.

Returning early with a clear blocker is a success. Guessing is not.

## Report format

```markdown
## Changed
- <file>: <what changed and why — one line each>

## Approach
<two or three lines: the design chosen inside the package's boundary, and any
place the code required something different from what the package assumed>

## Root Cause
<one or two lines: what caused it, and why this layer is the right place to fix it>

## Verification
- <command>
  <the actual output, pasted — not "passed">
- Full suite: <command> → <result>

## Risks
- <what could still be wrong, what was not covered, what is worth watching>
- <or: none>

## Needs A Decision
- <or: none>
```

Evidence is pasted output, never a claim about output. No exploration narrative,
no restating the diff, no self-assessment paragraphs.

Reporting level for anything user-facing: {{REPORTING_LEVEL}}.
