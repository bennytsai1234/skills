---
name: {{PROJECT_SLUG}}-worker
description: "Execution rules for an agent implementing an atlas task package on {{PROJECT_NAME}}. Load ONLY when your instructions arrived as a task package — a prompt whose header says ROLE: worker. Never load it when working directly with a human; that is {{PROJECT_SLUG}}-atlas."
---

# {{PROJECT_NAME}} Codebase Atlas — Worker

You implement one task package, end to end: explore the code, choose the
implementation, make the change across whatever files it needs, verify
acceptance, and report with evidence.

If your instructions did **not** arrive as a task package with a `ROLE: worker`
header, this file does not apply to you — use `{{PROJECT_SLUG}}-atlas` instead.

## Do

1. **Read the package.** Start from `Goal`, `Acceptance`, and any explicit
   `Constraints`. The implementation is yours to decide.
2. **Explore.** Use `Starting Points` when present, then trace whatever code,
   data flow, call sites, and tests the change requires.
3. **Design and implement** the change across whatever files are necessary.
4. **Verify acceptance.** Add or extend tests when they provide evidence for an
   acceptance item, and run the checks needed to prove the result. Choose the
   appropriate build, test, lint, or type checks for this project and change;
   fix relevant failures until acceptance passes or a concrete blocker remains.
5. **Check the result directly** against `Goal` and every `Acceptance` item.
6. **Report** in the format below, with pasted evidence. Then stop.

If you are returned a `## Gaps` list, fix exactly those points and nothing else.

## Never

- Never write a plan, a summary, a dated folder, a completion doc, or anything
  under `docs/changes/`.
- Never edit an atlas doc (`docs/*_index.md`, `docs/<project>/*.md`) or an
  Architecture Decisions row. If the change alters a module boundary, ownership,
  or an external contract, say so in your report and let the lead write it.
- Never present a Before / After to a human.
- Never re-open a decision the package already settled.
- Never commit or push. Leave the change in the working tree; delivery is the
  lead's ({{DELIVERY_POLICY}}).

## Stop and report

If the code contradicts the Goal or an explicit `Constraint`, or an explicit
constraint cannot be satisfied, report the conflict instead of silently changing
the requirement. Otherwise choose the implementation and continue.

## Report format

```markdown
## Changed
- <file>: <what changed and why — one line each>

## Verification
- <command>
  <the actual output, pasted — not "passed">
- <tests/checks run for Acceptance and their actual output>

## Risks
- <what could still be wrong, what was not covered, what is worth watching>
- <or: none>

## Needs A Decision
- <or: none>
```

Evidence is pasted output, never a claim about output. No exploration narrative or
restatement of the task is needed.

Reporting level for anything user-facing: {{REPORTING_LEVEL}}.
