# Quality Checklist

Run this checklist before reporting that an atlas initialization or rebuild is
complete.

## Decisions

- Working language is recorded and follows explicit repository rules first, user
  initialization language second, English third.
- Reference template mode is resolved as none, partial reference, or full
  alignment.
- Delivery policy and reporting level are recorded in the index.
- Partial reference output records the selected reference scope; full alignment
  output records that reference functionality is in scope.
- User-facing confirmation used plain-language questions instead of exposing
  internal decision keys, and used no reference / partial reference / full
  alignment choices instead of the term "feature parity".
- Preserved project rules were confirmed with concrete rule content and handling,
  not vague "will preserve" statements.

## Output Shape

- Output follows the standalone or reference-assisted tree from
  `references/atlas-contract.md`: index and module docs only.
- No separate workflow docs exist (`*_investigate_workflow.md` /
  `*_change_workflow.md`).
- The index has no "Decisions" metadata block and no links to workflow docs.
- The index includes concrete project operating constraints, links to all module
  docs, and an Architecture Decisions section (empty at initialization).
- The index carries a build provenance line — build date, source commit, atlas
  format version — directly under the settings line. Without it this atlas can
  only ever be rebuilt, never refreshed.
- No stale legacy per-project entrypoint remains (`<project-slug>-atlas` /
  `-relay` / `-worker` under `.claude/skills/` or `.agents/skills/`) — including
  the pre-split single adapter and any generic `docs/<project>_*_adapter.md`
  set, all of which must be deleted rather than left in place. The global
  `atlas-planner` / `atlas-relay` / `atlas-worker` / `atlas-fast` skills replace
  them; nothing is generated per project for these roles.
- No generated file was compressed, trimmed, or summarized to hit a length
  target. There is no length budget. Check content type instead: search-answerable
  detail (call sites, symbol lists, file inventories) stays out of the map, and
  content that only matters once you are inside a module lives in that module's
  doc rather than the index.
- No "run the atlas skill before every operation" mandate was written into
  `CLAUDE.md`; at most a single pointer line to the index exists.
- Old generated entrypoints, workflow docs, and technique folders were removed or
  preserved according to the user's explicit choice; no unrelated `.agents/` or
  `.claude/` files were deleted.
- Local Markdown links resolve.
- Every path and link in the generated Markdown uses forward slashes and stays
  relative — no backslashes, no drive letters, no `~` — regardless of the host
  OS the atlas was generated on.
- No file was rewritten purely to normalize line endings. Diffs contain content
  changes only.
- No unreplaced init-time placeholders remain.

## Module Quality

- Module boundaries are stable change surfaces.
- Module summaries route future work instead of listing files.
- Each module doc names scope, dependencies, change entry points and routes,
  known risks, and boundaries.
- Boundaries and Known Risks contain repository-specific facts and hidden
  constraints, not generic engineering advice. `atlas-planner` copies only the
  items relevant to a task's Goal into that package's `Constraints`.
- Repository facts are supported by committed files or project docs; invocation-
  local facts are absent.

## Refresh

Run this section in place of the Decisions section when the run was a refresh.

- The run was routed as a refresh only because an atlas with a usable build
  provenance line existed. Missing provenance or an unreachable recorded commit
  was reported to the user, who then chose a rebuild or a hand-scoped refresh.
- The drift set came from the recorded commit to `HEAD` with Scan Boundaries
  exclusions applied — a changed lockfile or a rebuilt `dist/` did not mark a
  module stale.
- Every module was classified stale / unmapped / removed / untouched, and the
  classification was confirmed with the user before any subagent was dispatched.
- Unmapped changed files were resolved by an explicit decision — folded into an
  existing module, or given a new one — never silently dropped.
- Untouched module docs are byte-identical to their pre-refresh state.
- Re-scanned module docs were updated in place and kept the project-specific
  notes that are still true, rather than being rewritten from zero.
- Removed modules had their docs deleted and their index entries dropped.
- The Architecture Decisions table is unchanged, and so is everything under
  `docs/changes/`.
- The build provenance line was rewritten to today's date and the current `HEAD`
  only after verification passed, and records the current atlas format version.
- The cross-file pass ran even though only part of the atlas was written: the
  index's module list matches the module docs on disk, and local links resolve.
- The report names both what was re-scanned and what was deliberately left alone.

## Reference-Assisted Quality

- Target project remains the primary subject.
- Partial reference material is used only within the user-selected scope.
- Full alignment is used only when the user explicitly requested full alignment,
  parity, compatibility, migration equivalence, or reference-driven expansion.
- Reference notes prevent feature creep outside the selected mode.

## Self-Verification Actions

Per the Initialization Workflow, items 1-2 below are first checked by a
dedicated subagent per file (index / each module doc), which fixes what it can
directly. After all of them return, run this same list yourself once more as a
centralized pass, focused on cross-file consistency that no single-file subagent
can see.

On a refresh, only the files this run actually wrote get a subagent. The
centralized pass still runs in full.

1. Reread the index and confirm every module summary says when future work should
   start there, and that no Decisions block or workflow links remain.
2. Reread each module doc and confirm it names scope, dependencies, change entry
   points and routes, known risks, and boundaries, grounded in committed files.
3. Confirm no legacy per-project entrypoint skill remains under `.claude/skills/`
   or `.agents/skills/` — `<project-slug>-atlas` / `-relay` / `-worker`, the
   pre-split single adapter, or a generic `docs/<project>_*_adapter.md` set.
4. Confirm `CLAUDE.md` / `AGENTS.md` have no forced skill-invocation mandate.
5. Confirm every init-time placeholder is replaced per the placeholder map in
   `references/atlas-contract.md` — including `{{BUILD_DATE}}`,
   `{{BUILD_COMMIT}}`, and `{{ATLAS_FORMAT}}` in the index.

## Final Report

- Report created, updated, and removed files (including any stale legacy
  entrypoint deleted as redundant).
- Report remaining TODOs and why they represent real uncertainty.
- Report validation status.
- Apply the selected delivery policy only after validation, per
  `references/atlas-contract.md` → Delivery: stage only this run's files,
  commit when the policy calls for it, push only when the policy is
  `commit and push`, and never force-push — stop and ask if a push is
  rejected as non-fast-forward.
