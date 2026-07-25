# {{ATLAS_TITLE}} Atlas Index

The navigation map for this project. Daily work enters through the lead
entrypoint skill, which reads this index, picks the relevant module(s), and
carries its own change/investigate discipline — this index holds the map, not the
process.

- Use it to locate the relevant module before inspecting code; keep details in the
  module docs. This index answers *what owns this, where do I start, what must I
  not break*; grep answers *where exactly is it*.
- Delegated subagents do not read this file. They receive the module doc paths
  they need in their task contract.
- Codebase Atlas runs once to build this map. Rerun it only for an explicit
  rebuild/refresh/rescan — a full scan that rebuilds this index from current
  repository reality.

Working language: {{WORKING_LANGUAGE}} · Delivery: {{DELIVERY_POLICY}} ·
Reporting: {{REPORTING_LEVEL}}
{{REFERENCE_BOUNDARY}}

## Project Operating Constraints

Inherited rules from existing project guidance. All work must follow these:

{{PROJECT_OPERATING_CONSTRAINTS}}

## Architecture Decisions

Cross-module decisions recorded during development. Module-level decisions live in
each module's Known Risks or Do Not Do section.

{{ARCHITECTURE_DECISIONS}}

## Module List

{{MODULE_LINKS}}

## Module Summaries

{{MODULE_SUMMARIES}}
