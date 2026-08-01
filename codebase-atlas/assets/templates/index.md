# {{ATLAS_TITLE}} Atlas Index

The navigation map for this project. Daily work enters through the lead
entrypoint skill, which reads this index, picks the relevant module(s), and
carries its own change/investigate discipline — this index holds the map, not the
process.

- Use it to locate the relevant module before inspecting code; keep details in the
  module docs. This index answers *what owns this, where do I start, what must I
  not break*; grep answers *where exactly is it*.
- Neither the execution manager nor an implementation agent reads this file. One
  enters through a dispatch plan, the other receives the module doc paths it
  needs as starting points in its task package.
- Codebase Atlas runs once to build this map, and is rerun only when a human
  asks. A **refresh** re-scans just the modules the repository changed under
  since the build below; a **rebuild** discards the map and scans everything.

Working language: {{WORKING_LANGUAGE}} · Delivery: {{DELIVERY_POLICY}} ·
Reporting: {{REPORTING_LEVEL}}
Atlas built: {{BUILD_DATE}} · from commit {{BUILD_COMMIT}} · format {{ATLAS_FORMAT}}
{{REFERENCE_BOUNDARY}}

## Project Operating Constraints

Inherited rules from existing project guidance. All work must follow these:

{{PROJECT_OPERATING_CONSTRAINTS}}

## Architecture Decisions

Cross-module decisions recorded during development. Module-level decisions live in
each module's Known Risks or Boundaries section.

{{ARCHITECTURE_DECISIONS}}

## Module List

{{MODULE_LINKS}}

## Module Summaries

{{MODULE_SUMMARIES}}
