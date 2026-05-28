# {{ATLAS_TITLE}} Validate Workflow

## Role

This is an internal agent module routed by the main workflow.
The user does not need to know this workflow exists.

Use it internally for checks, reviews, reproductions, verification, profiling,
CI or build failure investigation, and risk assessment when the user is not
asking for immediate implementation.

## Internal Reasoning Layer

Do not output this layer to the user.

1. Preserve the validation question, expected behavior, or risk.
1. Receive the task and already-read index summary from the main workflow.
1. Choose the most relevant module docs for the validation question.
1. Internally classify the validation type and apply the type-specific
   evidence approach listed under **Validation Types** below.
1. Internally confirm validation scope:
   - The specific behavior or assumption being validated.
   - Relevant boundaries and downstream impact.
1. Collect evidence:
   - Read relevant code, tests, configuration, or docs.
   - Read only the minimum content needed to answer the validation question.
   - For performance and CI types, capture actual measurements or logs, not
     guesses.
1. Internally separate:
   - Conclusions supported by evidence.
   - Parts that still cannot be confirmed.

## Validation Types

Pick exactly one type. Each type names the kind of question and what evidence
counts as sufficient.

- **Behavior check**: does the code do what the user expects?
  Evidence: trace the code path, confirm or refute against the expected
  behavior.

- **Review**: is the recent change correct, safe, and consistent?
  Evidence: read the diff against the surrounding module and atlas context;
  look for missing tests, contract drift, or hidden coupling.

- **Reproduction**: can the reported symptom be reproduced?
  Evidence: minimum reproduction case; record the exact steps and the
  observed output.

- **Profiling**: where is the time, memory, or query cost going?
  Evidence: a real measurement (timing, query log, profiler output, bundle
  analyzer, etc.) — not an inferred bottleneck. Capture a baseline before
  recommending any fix.

- **CI or build failure**: why did the pipeline break?
  Evidence: the failing log lines, the changed surface that the pipeline
  exercises, and the most recent commit that touched it. Distinguish flaky
  failures from real regressions.

- **Risk assessment**: what could go wrong if this change ships?
  Evidence: callers, persistence, generated artifacts, downstream systems,
  rollback path. State each risk with its likelihood and severity in plain
  language.

If the task does not cleanly match one type, pick the closest and note the
deviation in internal reasoning.

## External Reporting Layer

1. Report using the Before / After format below.
1. If validation shows a fix is needed, ask whether the user wants to continue
   with a change. Do not start editing immediately.

## Reporting Rules

- Before / After is the only human confirmation interface.
- Reporting level for this project: {{REPORTING_LEVEL}}
  - Plain: do not expose module names, file paths, function names, or code
    snippets in user-facing reports.
  - Technical: include module names, file paths, and relevant code context in
    user-facing reports to help the developer locate changes.
- Keep internal reasoning separate from the user-facing summary.

## Before / After Format

**Before**: In one to three plain sentences, explain what is being validated and
what was uncertain or risky before validation.

**After**: In one to three plain sentences, explain the validation result or
what still cannot be confirmed.

Wait for explicit user confirmation before any file-editing operation.

## Atlas Update Conditions

Update the atlas only when this validation finds existing atlas facts are
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
