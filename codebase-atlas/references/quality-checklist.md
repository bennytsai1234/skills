# Quality Checklist

Run this checklist before reporting that an atlas initialization or rebuild is
complete.

## Decisions

- Working language is recorded and follows explicit repository rules first, user
  initialization language second, English third.
- Reference template mode is resolved as none, partial reference, or full
  alignment.
- Delivery policy and reporting level are recorded in the index and every adapter.
- The platform adapter choices are recorded.
- Partial reference output records the selected reference scope; full alignment
  output records that reference functionality is in scope.
- User-facing confirmation used plain-language questions instead of exposing
  internal decision keys, and used no reference / partial reference / full
  alignment choices instead of the term "feature parity".
- Preserved project rules were confirmed with concrete rule content and handling,
  not vague "will preserve" statements.

## Output Shape

- Output follows the standalone or reference-assisted tree from
  `references/atlas-contract.md`: index, module docs, and adapter(s) only.
- No separate workflow docs exist (`*_investigate_workflow.md` /
  `*_change_workflow.md`).
- The index has no "Decisions" metadata block and no links to workflow docs.
- The index includes concrete project operating constraints, links to all module
  docs, and an Architecture Decisions section (empty at initialization).
- The adapter(s) exist and are self-contained (entry router + investigate/change
  discipline inline).
- No "run the atlas skill before every operation" mandate was written into
  `CLAUDE.md`; at most a single pointer line to the index exists.
- Old generated entrypoints, workflow docs, and technique folders were removed or
  preserved according to the user's explicit choice; no unrelated `.agents/` or
  `.claude/` files were deleted.
- Local Markdown links resolve.
- No unreplaced init-time placeholders remain (the runtime tokens `{{DATE}}` and
  `{{SLUG}}` in the adapter are intentionally kept).

## Module Quality

- Module boundaries are stable change surfaces.
- Module summaries route future work instead of listing files.
- Each module doc names scope, dependencies, change entry points and routes,
  known risks, and do-not-do boundaries.
- Repository facts are supported by committed files or project docs; invocation-
  local facts are absent.

## Adapter Quality

- The adapter is self-contained: it reads the index first, confirms the project
  in one sentence, picks only relevant module docs, and routes
  know→investigate / change→change.
- Investigate is read-only, separates facts from assumptions/unknowns, and hands
  off to change rather than editing itself.
- Change opens by judging a discipline tier (T0/T1/T2), with the hard floor at T2
  for irreversible, cross-module, external-API, or migration work, and scales
  test/plan/verification effort to the tier.
- Change states a Before / After before edits (Before = current state and why
  the change is needed, After = how it will be verified) as the only confirmation
  interface; T1/T2 wait for explicit confirmation, T0 announces the one-line
  Before/After and proceeds without waiting.
- Change includes a Decision Gate for module-boundary changes, external API
  changes, irreversible operations/migrations, or multi-option trade-offs.
- Change writes a scratch plan to `docs/changes/planning/{{DATE}}-{{SLUG}}.md`
  (`{{DATE}}` = ISO `YYYY-MM-DD`) before editing at T1/T2 (T0 skips), runs
  tier-appropriate verification, reports the verification result, moves the plan
  to `docs/changes/completed/{{DATE}}/{{SLUG}}.md` on completion, and appends its
  entry to that day's `docs/changes/completed/{{DATE}}/summary.md` (the daily work
  summary).
- The adapter reports per the selected reporting level (plain: no module names,
  paths, or code; technical: include them) and records the delivery policy.
- Atlas update instructions are incremental: update only affected module docs and
  index entries, not the full atlas.

## Reference-Assisted Quality

- Target project remains the primary subject.
- Partial reference material is used only within the user-selected scope.
- Full alignment is used only when the user explicitly requested full alignment,
  parity, compatibility, migration equivalence, or reference-driven expansion.
- Reference notes prevent feature creep outside the selected mode.

## Self-Verification Actions

Before the final report:

1. Reread the index and confirm every module summary says when future work should
   start there, and that no Decisions block or workflow links remain.
2. Reread each adapter and confirm the entry router reads the index first, the
   change discipline (tiers, Before/After, Decision Gate, plan lifecycle,
   verification) is present inline, and reporting respects the selected level.
3. Confirm platform skill frontmatter names and directories match the contract:
   both Claude Code and Codex use `<project-slug>-atlas`.
4. Confirm `CLAUDE.md` has no forced skill-invocation mandate.
5. Confirm every init-time placeholder is replaced per the placeholder map in
   `references/atlas-contract.md`, and that `{{DATE}}` and `{{SLUG}}` remain
   intact in the adapter (filled per change, not at initialization).

## Final Report

- Report created, updated, and removed files.
- Report remaining TODOs and why they represent real uncertainty.
- Report validation status.
- Apply the selected delivery policy only after validation.
