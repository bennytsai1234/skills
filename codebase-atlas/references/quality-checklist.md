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
- The worker model decision is resolved into two tiers and written into the lead
  adapter; where the user named no models, the placeholder-map fallbacks are used
  rather than invented model names.
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
- The index carries a build provenance line — build date, source commit, atlas
  format version — directly under the settings line. Without it this atlas can
  only ever be rebuilt, never refreshed.
- Every selected platform has **both** a lead adapter (`<project-slug>-atlas`)
  and a worker adapter (`<project-slug>-worker`). A lead adapter without its
  worker is a failed build, not a partial one.
- No stale generic adapter remains when a platform adapter exists — including
  the pre-split single `docs/<project>_adapter.md` from an earlier atlas
  version, which must be deleted rather than left in place.
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
- No unreplaced init-time placeholders remain (the runtime tokens `{{DATE}}` and
  `{{SLUG}}` in the lead adapter are intentionally kept).

## Module Quality

- Module boundaries are stable change surfaces.
- Module summaries route future work instead of listing files.
- Each module doc names scope, dependencies, change entry points and routes,
  known risks, and do-not-do boundaries.
- Do Not Do and Known Risks are written concretely enough to paste straight into
  a task package's `Must Preserve` and `Forbidden` sections.
- Repository facts are supported by committed files or project docs; invocation-
  local facts are absent.

## Role Separation

- The lead adapter opens by stating that it specifies and reviews but does not
  implement, and that it never spawns the worker — the package is a file the
  human carries across.
- The non-implementing rule is stated as absolute, with **no size exemption and
  no documented escape hatch**. An adapter containing "when the change is
  trivial" or "if the user asks" fails this check. The adapter does state what
  the lead may do: read code, run read-only checks, and re-run a verification
  that decides acceptance — and that a failing check is a gap to return, not
  something to fix.
- The lead adapter opens with a role check that hands off to
  `<project-slug>-worker` when invoked with a `ROLE: worker` package header;
  the worker adapter opens with the mirror check pointing back at
  `<project-slug>-atlas`.
- Both descriptions name the sibling skill.
- The lead adapter states the governance write gate: before writing an atlas
  doc, anything under `docs/changes/`, or an Architecture Decisions row, confirm
  the instructions came from a human rather than from a task package.
- The worker adapter contains none of: the index path, the module list, the tier
  model, planning, the Before/After gate, the Decision Gate, or the plan
  lifecycle.
- The worker adapter explicitly forbids writing plans, summaries, dated folders,
  completion docs, atlas docs, and Architecture Decisions rows — and committing
  or pushing.
- The worker adapter grants exploration explicitly: `Starting Points` orient it
  and do not cap what it may read, and it designs across whatever files the
  change requires inside `Scope`.
- The worker adapter states that the worker owns its own verification — build,
  suite, linter, type check — and fixes failures rather than handing them back.
  Neither adapter mentions `deferred-to-lead` or a shared-resource ban.
- The worker adapter requires a direct check against `Goal` and `Acceptance`
  rather than treating a green suite as sufficient.
- The worker adapter carries the forbidden-pattern catalogue
  (`references/delegation.md` §5) inline and a fixed report format whose
  `Verification` section demands pasted output rather than a claim.
- The worker adapter says a returned `## Gaps` list is fixed exactly and nothing
  else is touched.
- The lead adapter embeds the `atlas/v2` task package template inline.
- The lead adapter states the acceptance rule: every acceptance item is checkable
  by someone who was not in the conversation.
- The lead adapter carries the idle rule inline — while the package is out, do
  nothing: no `git status`, no diff inspection, no progress narration, no
  speculative reading.
- Neither adapter contains a `MODEL_TIER` field, a scheduling or disjoint-paths
  rule, a spawn instruction, or any other artifact of automated dispatch.

## Adapter Quality

- The lead adapter is self-contained: it reads the index first, confirms the
  project in one sentence, picks only relevant module docs, and routes
  know→investigate / change→change.
- Investigate is read-only, separates facts from assumptions/unknowns, and hands
  off to change rather than editing itself.
- Change opens by judging a discipline tier (T0/T1/T2), with the hard floor at T2
  for irreversible, cross-module, external-API, or migration work. The tier
  scales how much specification the change needs, not who does the work.
- Change states a Before / After before the package is written (Before = current
  state and why the change is needed, After = what becomes true and how it will
  be verified) as the only confirmation interface; T1/T2 wait for explicit
  confirmation, T0 announces the one-line Before/After and proceeds.
- Change includes a Decision Gate for module-boundary changes, external API
  changes, irreversible operations/migrations, or multi-option trade-offs, and
  states that a confirmed decision goes into the package's `Solution Boundary`
  where the worker may not re-open it.
- The package is written to `docs/changes/planning/{{DATE}}-{{SLUG}}.md`
  (`{{DATE}}` = ISO `YYYY-MM-DD`) — the same file serves as plan and handoff
  artifact — and the lead then tells the user it is ready and where it is. On
  completion at T1/T2 it moves to `docs/changes/completed/{{DATE}}/{{SLUG}}.md`
  with an entry appended to that day's summary; at T0 it is deleted.
- The Before / After gate is stated as lead-only, happening between the lead and
  the human and never agent-to-agent.
- Review is specified in order — requirement conformance against pasted evidence
  (re-running anything whose result decides acceptance), architecture against the
  atlas boundaries and `Must Preserve`, the diff for `Scope` containment and the
  forbidden-pattern catalogue, then the tests for whether they assert real
  behaviour.
- Returning is specified as gaps only, with the explicit "everything else is
  accepted, change nothing outside these points" line, capped at two returns
  before the package itself is withdrawn and reissued.
- Both adapters report per the selected reporting level (plain: no module names,
  paths, or code; technical: include them); the lead records the delivery policy
  and the worker records that delivery is the lead's.
- Atlas update instructions are incremental and lead-only: update only affected
  module docs and index entries, not the full atlas.
- The lead adapter carries the command-portability rule: `Acceptance` and
  evidence commands are written for the shell the worker will actually get, one
  command per line rather than an `&&` chain.

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
- Adapters were regenerated only because the recorded format version was behind
  the current one or because a decision changed — and if regenerated, as a full
  lead + worker pair.
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

Per the Initialization Workflow, items 1-6 below are first checked by a
dedicated subagent per file (index / each module doc / each adapter), which
fixes what it can directly. After all of them return, run this same list
yourself once more as a centralized pass, focused on cross-file consistency
that no single-file subagent can see.

On a refresh, only the files this run actually wrote get a subagent. The
centralized pass still runs in full.

1. Reread the index and confirm every module summary says when future work should
   start there, and that no Decisions block or workflow links remain.
2. Reread the lead adapter and confirm it states the non-implementing,
   non-dispatching role; the role check comes first; the entry router reads the
   index; the change discipline (tiers, Decision Gate, Before/After, package
   lifecycle) is present inline; the `atlas/v2` package template is embedded; the
   idle rule, the acceptance-is-the-whole-contract rule, the review order, and
   the gaps-only return are present inline; and reporting respects the selected
   level.
3. Reread the worker adapter and confirm it opens with the mirror role check,
   grants exploration and cross-file design, makes the worker own its tests and
   build, forbids governance writes and commits, carries the forbidden-pattern
   catalogue and the evidence-based report format, handles a returned gaps list,
   and never mentions the index, the module list, or the plan lifecycle.
4. Confirm platform skill frontmatter names and directories match the contract:
   Claude Code and Codex both use `<project-slug>-atlas` for the lead and
   `<project-slug>-worker` for the worker, and both exist for every selected
   platform.
5. Confirm `CLAUDE.md` / `AGENTS.md` have no forced skill-invocation mandate.
6. Confirm every init-time placeholder is replaced per the placeholder map in
   `references/atlas-contract.md` — including `{{BUILD_DATE}}`,
   `{{BUILD_COMMIT}}`, and `{{ATLAS_FORMAT}}` in the index — that
   `{{INDEX_FILE}}` appears in the lead adapter and not the worker, and that
   `{{DATE}}` and `{{SLUG}}` remain intact in the lead adapter (filled per
   change, not at initialization).

## Final Report

- Report created, updated, and removed files (including any stale generic
  adapter deleted as redundant).
- Report remaining TODOs and why they represent real uncertainty.
- Report validation status.
- Apply the selected delivery policy only after validation, per
  `references/atlas-contract.md` → Delivery: stage only this run's files,
  commit when the policy calls for it, push only when the policy is
  `commit and push`, and never force-push — stop and ask if a push is
  rejected as non-fast-forward.
