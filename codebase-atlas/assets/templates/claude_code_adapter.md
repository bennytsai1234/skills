---
name: {{PROJECT_SLUG}}-atlas
description: "Use this for every task in this project — reads the atlas before acting."
---

# {{PROJECT_NAME}} Codebase Atlas

This is the Codebase Atlas entrypoint and router for this project. It is the
only entrypoint for daily work — follow it for every operation.

## Entry (read the index first, then route)

1. Preserve the user's original request.
1. Open `{{INDEX_FILE}}` before any other operation.
1. Confirm in one plain sentence what this project does.
1. Route by intent:
   - The user wants to **know** something — explain, locate, feasibility,
     ownership, behavior check, review, reproduction, profiling, CI failure,
     risk assessment → follow `{{INVESTIGATE_WORKFLOW_FILE}}`.
   - The user wants to **change** something — any code edit → follow
     `{{CHANGE_WORKFLOW_FILE}}`.
   - Mixed or unclear → start with investigate, then decide whether a change is
     needed.
1. When composing, pass conclusions forward; do not reread the index or module
   docs unless the next step needs context not already gathered.
1. For any operation that edits files, provide Before / After and wait for
   explicit user confirmation before editing.
1. Finish according to this delivery policy: {{DELIVERY_POLICY}}
1. After a task completes, ask in plain language whether anything else needs
   handling. If the user continues, route the next request without rereading the
   index.

## Reporting

- Before / After is the only human confirmation interface.
- Reporting level: {{REPORTING_LEVEL}}
  - Plain: do not mention module names, file paths, or code snippets to the user.
  - Technical: include module names, file paths, and relevant code context.

## Do Not Do

- Do not rerun Codebase Atlas initialization unless the user explicitly asks for
  a full rebuild.
- Do not skip reading the atlas index.
- Do not edit files before the user confirms Before / After.
