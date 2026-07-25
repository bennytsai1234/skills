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
- Every selected platform has **both** a lead adapter (`<project-slug>-atlas`)
  and a worker adapter (`<project-slug>-worker`). A lead adapter without its
  worker is a failed build, not a partial one.
- No stale generic adapter remains when a platform adapter exists — including
  the pre-split single `docs/<project>_adapter.md` from an earlier atlas
  version, which must be deleted rather than left in place.
- The index stays within its tier budget (roughly 150 lines); module docs stay
  within theirs (roughly 120 lines). Overrun means tier-3 detail leaked into
  the index, or search-answerable detail leaked into a module doc.
- No "run the atlas skill before every operation" mandate was written into
  `CLAUDE.md`; at most a single pointer line to the index exists.
- Old generated entrypoints, workflow docs, and technique folders were removed or
  preserved according to the user's explicit choice; no unrelated `.agents/` or
  `.claude/` files were deleted.
- Local Markdown links resolve.
- No unreplaced init-time placeholders remain (the runtime tokens `{{DATE}}` and
  `{{SLUG}}` in the lead adapter are intentionally kept).

## Module Quality

- Module boundaries are stable change surfaces.
- Module summaries route future work instead of listing files.
- Each module doc names scope, dependencies, change entry points and routes,
  known risks, and do-not-do boundaries.
- Do Not Do and Known Risks are written concretely enough to paste straight into
  a task contract's `Must Preserve` and `Forbidden` sections.
- Repository facts are supported by committed files or project docs; invocation-
  local facts are absent.

## Role Separation

- The lead adapter opens with a role check that hands off to
  `<project-slug>-worker` when invoked with a `ROLE: worker` contract header;
  the worker adapter opens with the mirror check pointing back at
  `<project-slug>-atlas`.
- Both descriptions name the sibling skill, so a mis-triggered load self-corrects
  on the first line.
- The lead adapter states the governance write gate: before writing an atlas
  doc, anything under `docs/changes/`, or an Architecture Decisions row, confirm
  the instructions came from a human rather than another agent's task
  description.
- The worker adapter contains none of: the index path, the module list, the tier
  model, planning, the Before/After gate, the Decision Gate, or the plan
  lifecycle.
- The worker adapter explicitly forbids writing plans, summaries, dated folders,
  completion docs, atlas docs, and Architecture Decisions rows.
- The worker adapter explicitly forbids shared-resource commands — whole-project
  build, full test suite, dev server, port binding, database, migration,
  dependency install, process kill — and defines
  `verification: deferred-to-lead` as the alternative.
- The worker adapter carries the forbidden-pattern catalogue
  (`references/delegation.md` §5) inline and a fixed report format.
- The lead adapter embeds the `atlas/v1` task contract template inline, so
  delegating costs no extra file read.
- The lead adapter states the disjoint-`Allowed Paths` scheduling rule, that
  full-build-dependent tasks run solo, and that shared resources run only with
  zero workers in flight.
- The lead adapter reserves a separate review subagent for T2 or self-written
  code, and reviews inline otherwise.

## Adapter Quality

- The lead adapter is self-contained: it reads the index first, confirms the
  project in one sentence, picks only relevant module docs, and routes
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
- The Before / After gate is stated as lead-only, happening between the lead and
  the human and never agent-to-agent, and T1/T2 waits for confirmation before
  dispatching a worker as well as before editing.
- Acceptance checks worker output against the contract — acceptance items,
  `Allowed Paths` containment, `Must Preserve` integrity, root cause versus
  symptom, and the forbidden-pattern catalogue — before the lead's authoritative
  build.
- Both adapters report per the selected reporting level (plain: no module names,
  paths, or code; technical: include them); the lead records the delivery policy
  and the worker records that delivery is the lead's.
- Atlas update instructions are incremental and lead-only: update only affected
  module docs and index entries, not the full atlas.

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
that no single-file subagent can see:

1. Reread the index and confirm every module summary says when future work should
   start there, and that no Decisions block or workflow links remain.
2. Reread the lead adapter and confirm the role check comes first, the entry
   router reads the index, the change discipline (tiers, Before/After, Decision
   Gate, plan lifecycle, verification) is present inline, the contract template
   is embedded, and reporting respects the selected level.
3. Reread the worker adapter and confirm it is short, opens with the mirror role
   check, forbids governance writes and shared-resource commands, carries the
   forbidden-pattern catalogue and the report format, and never mentions the
   index, the module list, or the plan lifecycle.
4. Confirm platform skill frontmatter names and directories match the contract:
   Claude Code and Codex both use `<project-slug>-atlas` for the lead and
   `<project-slug>-worker` for the worker, and both exist for every selected
   platform.
5. Confirm `CLAUDE.md` / `AGENTS.md` have no forced skill-invocation mandate.
6. Confirm every init-time placeholder is replaced per the placeholder map in
   `references/atlas-contract.md`, that `{{INDEX_FILE}}` appears in the lead
   adapter and not the worker, and that `{{DATE}}` and `{{SLUG}}` remain intact
   in the lead adapter (filled per change, not at initialization).

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
