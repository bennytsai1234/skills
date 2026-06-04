# Quality Checklist

Run this checklist before reporting that an atlas initialization or rebuild is
complete.

## Decisions

- Mode is recorded.
- Working language is recorded and follows explicit repository rules first,
  user initialization language second, English third.
- Reference template mode is recorded as none, partial reference, or full
  alignment.
- Delivery policy is recorded in the index and every workflow.
- Reporting level is recorded in the index and every workflow.
- The default adapter and any additional entrypoint choices are recorded.
- Partial reference output records the selected reference scope.
- Full alignment output records that reference functionality is in scope.
- User-facing confirmation used plain-language questions instead of exposing
  internal decision keys.
- User-facing reference-template confirmation used no reference, partial
  reference, and full alignment choices instead of the term "feature parity".
- Preserved project rules were confirmed with concrete rule content and
  handling, not vague "will preserve" statements.

## Output Shape

- Output follows the standalone or reference-assisted tree from
  `references/atlas-contract.md`.
- Index links to both workflow docs (investigate, change) and points to the
  techniques folder.
- Index includes project operating constraints inherited from existing guidance.
- Project operating constraints are concrete enough for all workflows to follow.
- Old generated Codebase Atlas entrypoints were removed or preserved according
  to the user's explicit choice.
- No unrelated `.agents/` files were deleted.
- Both workflows (investigate, change) exist.
- The five technique docs were copied into `<project>_techniques/`.
- The adapter exists and embeds the entry router.
- Index links to all module docs.
- Index includes an Architecture Decisions section (empty at initialization).
- Local Markdown links resolve.
- No unreplaced init-time placeholders remain (the runtime tokens `{{DATE}}` and
  `{{SLUG}}` in the change workflow are intentionally kept).

## Module Quality

- Module boundaries are stable change surfaces.
- Module summaries route future work instead of listing files.
- Each module doc names scope, dependencies, change entry points, change routes,
  known risks, and do-not-do boundaries.
- Repository facts are supported by committed files or project docs.
- Invocation-local facts are absent.

## Workflow Quality

- Both workflows (investigate, change) exist.
- The adapter embeds the entry router: it reads the index first, confirms the
  project in one sentence, and routes read→investigate / write→change.
- The adapter reports according to the selected reporting level (plain: no
  module names, file paths, function names, or code snippets; technical:
  includes them) and uses Before / After as the only human confirmation
  interface.
- Investigate and change are internal modules routed by the adapter; both select
  relevant module context and any necessary boundary context before code
  inspection.
- The five technique docs under `<project>_techniques/` are self-contained (no
  references to external skills, files, or tools) and are referenced by the
  workflows on demand, never inlined.
- Investigate covers the read-only questions (explanation, ownership,
  feasibility, behavior check, review, reproduction, profiling, CI failure, risk
  assessment) and captures real evidence for profiling and CI types, not
  guesses.
- Change opens by judging a discipline tier (T0/T1/T2), with the hard floor at
  T2 for irreversible, cross-module, external-API, or migration work, and scales
  technique use, plan recording, and verification to the tier.
- Change requires a Before / After gate before edits; the Before states the
  diagnosed root cause and the After states how it will be verified.
- Change includes a Decision Gate that triggers for module boundary changes,
  external API changes, irreversible operations, multi-option trade-offs, or any
  task internally classified as Migration.
- Change classifies every task into one of the ten internal task types (bug,
  feature, optimization, refactor, release, dependency, migration, config,
  hotfix, cleanup) and runs the tier-appropriate minimum verification (following
  `verification.md`) after edits.
- Change writes a plan to `docs/changes/planning/` before editing at T1 or T2
  (T0 skips it): T1 leaves it as uncommitted scratch; T2 commits it
  (`plan: <slug>`) only when the delivery policy allows commits, otherwise
  leaves it uncommitted. After verification passes, the plan moves to
  `docs/changes/completed/`; a plan produced without implementation stays in
  `docs/changes/planning/`.
- Investigate requires a Before / After gate before any follow-up edit and hands
  off to change rather than editing itself.
- Workflows use Before / After as the user-facing confirmation gate, not
  secondary engineering reports; reason through scope; and require atlas updates
  only when module boundaries, ownership, external APIs, or documented
  repository facts change.
- Atlas update instructions are incremental: update only affected module docs
  and index entries, not the full atlas.
- The adapter embeds the router and points to the index and both workflows, not
  to a single workflow.


## Reference-Assisted Quality

- Target project remains the primary subject.
- Partial reference material is used only within the user-selected scope.
- Full alignment is used only when the user explicitly requested full
  alignment, parity, compatibility, migration equivalence, or reference-driven
  expansion.
- Reference notes prevent feature creep outside the selected mode.

## Self-Verification Actions

Before the final report:

1. Reread the index and confirm every module summary includes a situational
   description of when future work should start there.
2. Reread the adapter and confirm its entry router reads the index first and its
   user-facing report rules respect the selected reporting level.
3. Confirm the adapter routes to both workflows (investigate, change) and that
   the technique docs were copied in and are referenced on demand.
4. Confirm every init-time placeholder is replaced per the placeholder map in
   `references/atlas-contract.md`, and that the runtime tokens `{{DATE}}` and
   `{{SLUG}}` remain intact in the change workflow (they are filled per change,
   not at initialization).

## Final Report

- Report created, updated, and removed files.
- Report remaining TODOs and why they represent real uncertainty.
- Report validation status.
- Apply the selected delivery policy only after validation.
