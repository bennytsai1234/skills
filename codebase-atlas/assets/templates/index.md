# {{ATLAS_TITLE}} Atlas Index

## Purpose And Usage

- Use this index to locate the relevant module before inspecting code.
- Keep this document high level; put details in the module documents.
- Codebase Atlas is normally run once to initialize this map.
- For later understanding, change, validation, or mixed work, use the main
  workflow listed below instead of running Codebase Atlas again.
- Run Codebase Atlas again only for an explicit rebuild, refresh, regenerate, or
  rescan. That means scanning the full codebase again and rebuilding this index
  from current repository reality.

## Decisions

- Atlas mode: {{ATLAS_MODE}}
- Working language: {{WORKING_LANGUAGE}}
- Reference template mode: {{REFERENCE_TEMPLATE_MODE}}
- Workflow delivery policy: {{DELIVERY_POLICY}}
- Reporting level: {{REPORTING_LEVEL}}
- Workflow entrypoints: {{WORKFLOW_ENTRYPOINT_POLICY}}
{{REFERENCE_BOUNDARY}}
{{WORKFLOW_ENTRYPOINTS}}

## Project Operating Constraints

Inherited rules from existing project guidance. All workflows must follow these:

{{PROJECT_OPERATING_CONSTRAINTS}}


## Architecture Decisions

Cross-module decisions recorded during development. Module-level decisions are
in each module's Known Risks or Do Not Do section.

{{ARCHITECTURE_DECISIONS}}

## Workflow Docs

Daily work enters through the adapter, which reads this index first, confirms in
one sentence what the project does, and routes to one of two workflows:

- Investigate workflow (read — explain, locate, review, reproduce, profile,
  assess risk): {{INVESTIGATE_WORKFLOW_LINK}}
- Change workflow (write — every code edit): {{CHANGE_WORKFLOW_LINK}}

Shared, self-contained discipline docs (debugging, TDD, verification, code
review, design grilling) live under `{{TECHNIQUES_DIR}}/` and are read on demand.

## Module List

{{MODULE_LINKS}}

## Module Summaries

{{MODULE_SUMMARIES}}
