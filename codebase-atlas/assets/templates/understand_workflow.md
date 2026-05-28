# {{ATLAS_TITLE}} Understand Workflow

## Role

This is an internal agent module routed by the main workflow.
The user does not need to know this workflow exists.

Use it internally for introductions, explanations, ownership questions,
feasibility questions, and investigations.

## Internal Reasoning Layer

Do not output this layer to the user.

1. Preserve the user's question or symptom.
1. Receive the task and already-read index summary from the main workflow.
1. Choose the most relevant module docs for the task. Do not read every module
   doc by default.
1. Inspect code, tests, docs, logs, or config only when module context is not
   enough to answer accurately.
1. Internally separate:
   - Confirmed facts supported by docs or code.
   - Reasonable assumptions that have not been verified.
   - Unknowns that remain.

## External Reporting Layer

1. Answer the user's question in plain language.
1. If there are assumptions or unknowns, state them directly as uncertainty.
1. If follow-up implementation is needed, ask whether the user wants to
   continue with a change.

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

Wait for explicit user confirmation before any file-editing operation.

## Atlas Update Conditions

Update the atlas only when this investigation finds existing atlas facts are
inaccurate, such as incorrect module boundary descriptions or changed
ownership. Report newly discovered risks to the user; do not write them back to
the atlas unless they make existing atlas facts inaccurate.

When an update is needed, apply it incrementally:

1. Update only the affected module doc or docs.
2. If the module list or summaries in the index changed, update the index.
3. Do not rescan unrelated modules or regenerate workflow docs.
4. Note what changed and why in the report.

## Delivery Policy

{{DELIVERY_POLICY}}
