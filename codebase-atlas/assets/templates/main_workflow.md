# {{ATLAS_TITLE}} Main Workflow

## Role

This is the only daily entrypoint for this project.
The user does not need to know that understand, change, and validate workflows
exist. The agent routes automatically based on task intent and may compose
workflows when needed.

## Workflow

1. Open `{{INDEX_FILE}}` before any other operation, while preserving the
   user's original request and intent.
1. Confirm in one plain sentence what this project does.
1. Route by task intent:
   - Understanding, explanation, investigation, or feasibility: use the
     understand workflow.
   - Modification, bug fix, feature, optimization, refactor, release,
     dependency upgrade, schema or data migration, configuration change,
     hotfix, or cleanup: use the change workflow with the matching internal
     task type.
   - Validation, review, safety check, reproduction, profiling, CI or build
     failure investigation, or risk assessment: use the validate workflow.
   - Mixed intent: compose workflows in understand, validate, change order.
1. Run the matching workflow internally.
1. Report the result to the user in plain language.
1. If the task edits files, provide the Before / After gate and wait for
   explicit confirmation before editing.
1. Finish according to this delivery policy: {{DELIVERY_POLICY}}

## Routing Principles

When intent is unclear, start with understand, then decide whether validate or
change is needed. Never edit files without Before / After confirmation.

When composing workflows, pass the conclusions from the previous workflow into
the next workflow. Do not reread the index or module docs unless the next
workflow needs context that was not already gathered.

Daily maintenance tasks route to the change workflow with an explicit internal
task type. The change workflow has dedicated verification steps for each type.

## Reporting Rules

- Before / After is the only human confirmation interface.
- Reporting level for this project: {{REPORTING_LEVEL}}
  - Plain: do not expose module names, file paths, function names, or code
    snippets in user-facing reports.
  - Technical: include module names, file paths, and relevant code context in
    user-facing reports to help the developer locate changes.
- Keep internal reasoning separate from the user-facing summary.

## Before / After Format

**Before**: In one to three plain sentences, explain the current situation and
what is wrong, unclear, missing, or risky.

**After**: In one to three plain sentences, explain what will be true after the
operation is complete.

Wait for explicit user confirmation before executing.

## Continuous Work Mode

After each task is complete, ask the user in plain language:

```text
Is there anything else that needs to be handled?
```

If the user continues with another request:

- Do not reread the index.
- Continue from routing judgment.
- Keep plain-language reporting and the Before / After mechanism.

End only when the user says there is nothing else to handle.
