# {{ATLAS_TITLE}} Investigate Workflow

## Role

This is an internal agent module routed by the adapter's entry step.
The user does not need to know this workflow exists.

Use it internally for all read-only work — anything where the user wants to
*know* something rather than change it: explanations, ownership and feasibility
questions, investigations, behavior checks, reviews, reproductions, profiling,
CI or build failure analysis, and risk assessment. It never edits files; if a
fix is needed it hands off to the change workflow.

## Internal Reasoning Layer

Do not output this layer to the user.

1. Preserve the user's question, symptom, or risk.
1. Receive the task and the already-read index summary from the entry step.
1. Choose the most relevant module docs for the question. Do not read every
   module doc by default.
1. If you are unfamiliar with the area, **zoom out first**: go up a layer of
   abstraction and map the relevant modules and callers from the atlas before
   diving into code. Build the big-picture mental model, then narrow.
1. Internally classify the read question and apply the matching evidence
   approach:
   - **Behavior check** — does the code do what the user expects? Trace the
     path; confirm or refute against the expected behavior.
   - **Review** — is a recent change correct, safe, consistent? Pull in
     `{{TECHNIQUES_DIR}}/code-review.md` and read the diff against the owning
     and boundary modules.
   - **Reproduction / why-broken / CI failure** — pull in
     `{{TECHNIQUES_DIR}}/debugging.md` and build a feedback loop; for CI, read
     the failing log lines and the changed surface the pipeline exercises, and
     distinguish a flake from a real regression.
   - **Profiling** — capture a real measurement (timing, profiler, query log,
     bundle analysis), not an inferred bottleneck; record a baseline.
   - **Feasibility / ownership / explanation** — answer from atlas plus the
     minimum code needed. For an open "should we do X / how should we design Y"
     question with several interdependent unresolved decisions, follow
     `{{TECHNIQUES_DIR}}/design-grilling.md` — interview one question at a time,
     each with a recommended answer — instead of guessing a single answer.
   - **Risk assessment** — name callers, persistence, generated artifacts,
     downstream systems, and rollback path; state each risk with plain-language
     likelihood and severity.
1. Inspect code, tests, docs, logs, or config only when module context is not
   enough to answer accurately.
1. Internally separate:
   - Confirmed facts supported by docs or code.
   - Reasonable assumptions that have not been verified.
   - Unknowns that remain.

## External Reporting Layer

1. Answer the user's question in plain language.
1. State any assumptions or unknowns directly as uncertainty.
1. If the answer implies a fix or change is needed, ask whether the user wants
   to continue with a change. Do not start editing — hand off to the change
   workflow only after the user agrees.

## Reporting Rules

- Before / After is the only confirmation gate before any follow-up edit; a pure
  investigation answer needs no gate.
- Reporting level for this project: {{REPORTING_LEVEL}}
  - Plain: do not expose module names, file paths, function names, or code
    snippets in user-facing reports.
  - Technical: include module names, file paths, and relevant code context in
    user-facing reports to help the developer locate things.
- Keep internal reasoning separate from the user-facing summary.

## Before / After Format

Used only if the investigation leads to a follow-up edit. The change workflow
owns the edit; this gate applies before any file change.

**Before**: In one to three plain sentences, explain the current situation and
the diagnosed problem — what is wrong, unclear, missing, or risky, and your
read of the root cause.

**After**: In one to three plain sentences, explain what will be true after the
follow-up operation, and how it will be verified.

Wait for explicit user confirmation before any file-editing operation.

## Atlas Update Conditions

Update the atlas only when this investigation finds existing atlas facts are
inaccurate, such as incorrect module boundary descriptions or changed ownership.
Report newly discovered risks to the user; do not write them back to the atlas
unless they make existing atlas facts inaccurate.

When an update is needed, apply it incrementally:

1. Update only the affected module doc or docs.
2. If the module list or summaries in the index changed, update the index.
3. Do not rescan unrelated modules or regenerate workflow docs.
4. Note what changed and why in the report.

## Delivery Policy

{{DELIVERY_POLICY}}
