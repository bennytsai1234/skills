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
- No model-tier decision was asked or recorded: the execution tiers are fixed at
  GPT-5.6-Luna, reasoning Max, written literally into the relay and worker
  adapters.
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
- Every selected platform has **all three** adapters: `<project-slug>-atlas`,
  `<project-slug>-relay`, `<project-slug>-worker`. A partial set is a failed
  build, not a partial one — without the relay adapter, acceptance and archival
  strand whenever the human does not return.
- No stale generic adapter remains when a platform adapter exists — including
  the pre-split single `docs/<project>_adapter.md` and the format-3 lead/worker
  pair, both of which must be deleted rather than left in place.
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
  known risks, and boundaries.
- Boundaries and Known Risks contain repository-specific facts and hidden
  constraints, not generic engineering advice. A task package copies only the
  items relevant to its Goal into `Constraints`.
- Repository facts are supported by committed files or project docs; invocation-
  local facts are absent.

## Role Separation

- The lead adapter opens by stating that it specifies and reviews but does not
  implement, and that it never dispatches — it writes files and the human carries
  the dispatch plan across.
- The non-implementing rule is stated as absolute, with **no size exemption and
  no documented escape hatch**. An adapter containing "when the change is
  trivial" or "if the user asks" fails this check. The adapter does state what
  the lead may do: read code, run read-only checks, and re-run a verification
  that decides acceptance — and that a failing check is a gap to return, not
  something to fix.
- Each adapter opens with a role check naming **both** siblings: the lead hands
  off to `<slug>-worker` on `ROLE: worker` and `<slug>-relay` on
  `ROLE: relay-lead`; the relay and worker adapters mirror it.
- All three descriptions name both sibling skills.
- The lead adapter states the governance write gate and what is *not* its to
  write: completion records, `docs/changes/completed/**`, implementation commits.
- The relay adapter contains none of: the index path, the module list, the tier
  model, the Before/After gate, the Decision Gate, or package-authoring rules.
- The worker adapter contains none of: the index path, the module list, the tier
  model, planning, the Before/After gate, the Decision Gate, dispatch mechanics,
  or the plan lifecycle.
- The worker adapter states what belongs to other tiers as **ownership rather
  than prohibition**: records and delivery to the relay lead, the atlas and
  Architecture Decisions to the lead, the Before/After gate already spent, a
  settled decision stays settled.
- The worker adapter grants exploration explicitly: `Starting Points` orient it
  but do not cap what it may read or change, and it chooses the implementation
  across whatever files the change requires.
- The worker adapter states that the worker owns the checks needed to establish
  acceptance — including a whole-project build and the full suite — and reports
  their actual output. No adapter mentions `deferred-to-lead` or a
  shared-resource ban.
- The worker adapter requires a direct check against `Goal` and `Acceptance`
  rather than treating a green suite as sufficient. Its shortcut rule is **one
  principle plus its usual shapes, with deliberate deviation allowed when
  explained** — a catalogue of absolute bans fails this check.
- The worker adapter carries a concise report format whose `Verification` section
  demands pasted output rather than a claim.
- The worker adapter says a returned `## Gaps` list is fixed exactly and
  everything else is already accepted.
- The lead adapter embeds the `atlas/v3` task package template inline: Goal,
  Background, objective Acceptance checks, optional explicit Constraints, optional
  Starting Points, Evidence, and an empty `Completion record`. It does not require
  Why, Solution Boundary, Scope, Must Preserve, Forbidden, Allowed Paths, or
  generic stop conditions.
- The lead adapter explains `Background` with no length limit, as the section that
  makes a package portable to a model with zero conversation history.
- The lead adapter embeds the dispatch-plan template inline and requires one even
  for a single package.
- The lead adapter states the acceptance rules: checkable by a stranger, exact
  values over existence claims, the negative case, what must not change, and that
  passing by weakening is deliberate and explained.
- The lead adapter carries the idle rule inline — while the batch is out, the
  work belongs to the execution tier: no `git status`, no diff inspection, no
  progress narration, no speculative reading — and states that the user may never
  return.
- The relay adapter waits with `wait_agent` rather than `sleep`, sets
  `timeout_ms: 3600000`, treats `timed_out: true` as "still running, wait again",
  and re-waits on remaining ids when several subagents are in flight.
- The relay adapter attributes `/goal` to the human, never invoking it for itself
  or applying it to a subagent.
- The relay adapter accepts by re-running the decisive checks, never on the
  subagent's text, and leaves specification defects to the planning tier.
- The relay adapter states it is the human's window during the batch: mid-course
  additions are relayed to the same worker as an appended package (no new task
  package), and the relay runs the atlas refresh at batch end.
- Model assignment appears literally as GPT-5.6-Luna, reasoning Max, in the relay
  adapter, the worker adapter, and both embedded template headers. No adapter
  contains a `MODEL_TIER` field or any other abstract tier system.

## Adapter Quality

- The lead adapter is self-contained: it reads the index first, confirms the
  project in one sentence, picks only relevant module docs, and routes
  know→investigate / change→change.
- Investigate is read-only, separates facts from assumptions/unknowns, and hands
  off to change rather than editing itself.
- Change opens by judging a discipline tier (T1/T2 only), with the hard floor at
  T2 for irreversible, cross-module, external-API, or migration work. The tier
  scales how much specification the change needs, not who does the work.
- Change states explicitly that **there is no trivial tier** — a typo or one-line
  config change goes straight to an execution model, and the lead neither invents
  a shortcut path nor edits it itself.
- Change states a Before / After before packages are written (Before = current
  state and why the change is needed, After = what becomes true and how it will
  be verified) as the only confirmation interface, and waits for explicit
  confirmation.
- Change uses a Decision Gate only for choices the repository cannot settle, and
  records a confirmed choice as an explicit package `Constraints` item rather
  than prescribing an implementation.
- Packages are written to `docs/changes/planning/{{DATE}}-{{SLUG}}.md` (`{{DATE}}`
  = ISO `YYYY-MM-DD`) — the same file serves as plan and handoff artifact — with
  the dispatch plan alongside them, all committed and pushed before the lead tells
  the user which single file to hand over.
- The completion protocol appears in order with the correct owner: the relay lead
  fills the `Completion record`, moves the package to
  `docs/changes/completed/{{DATE}}/{{SLUG}}.md`, archives the batch's dispatch
  plan at `completed/{{DATE}}/{{SLUG}}-dispatch-plan.md` after the last package,
  appends that day's summary line after the move, then commits and pushes code
  and records together. No completed package is deleted, and `planning/` holds
  only pending batches.
- The Before / After gate is stated as lead-only, happening between the lead and
  the human and never agent-to-agent.
- Acceptance is specified in order and assigned to the right tier: the relay lead
  re-runs the decisive checks as the primary gate, and the lead's review is a
  second pass that may never happen.
- Returning is specified as gaps only, with the explicit "everything else is
  accepted, change nothing outside these points" line, capped at two returns
  before the specification itself is the suspect.
- All three adapters report per the selected reporting level (plain: no module
  names, paths, or code; technical: include them); the lead records the delivery
  policy and the worker records that delivery belongs to the relay lead.
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
  the current one or because a decision changed — and if regenerated, as the full
  set of three.
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

Per the Initialization Workflow, items 1-7 below are first checked by a
dedicated subagent per file (index / each module doc / each adapter), which
fixes what it can directly. After all of them return, run this same list
yourself once more as a centralized pass, focused on cross-file consistency
that no single-file subagent can see.

On a refresh, only the files this run actually wrote get a subagent. The
centralized pass still runs in full.

1. Reread the index and confirm every module summary says when future work should
   start there, and that no Decisions block or workflow links remain.
2. Reread the lead adapter and confirm it states the non-implementing,
   non-dispatching role; the role check comes first and names both siblings; the
   entry router reads the index; the change discipline (T1/T2 with no trivial
   tier, Decision Gate, Before/After) is present inline; the `atlas/v3` package
   template and the dispatch-plan template are both embedded; the `Background`
   guidance, acceptance rules, `Starting Points`-is-a-map rule, commit-and-push
   before handover, idle rule, escalated second-pass review order, and gaps-only
   return are present inline; and reporting respects the selected level.
3. Reread the relay adapter and confirm it enters only through a dispatch plan,
   respects hard ordering while owning parallelism, dispatches with the literal
   model parameters, waits with `wait_agent` at `timeout_ms: 3600000`, treats a
   timeout as "still running", re-waits on remaining ids, accepts by re-running
   checks, never repairs a specification, relays human mid-course additions to
   the same worker, archives the dispatch plan with the batch, runs the atlas
   refresh at batch end, and carries the completion protocol in order ending in
   commit and push.
4. Reread the worker adapter and confirm it opens with the mirror role check,
   grants exploration and implementation choice, makes the worker own the checks
   needed for acceptance including full builds and suites, states other tiers'
   ownership rather than a prohibition list, carries the shortcut rule as a
   principle rather than a ban catalogue, carries the evidence-based report
   format, handles a returned gaps list, treats appended human additions as part
   of the same package, and never mentions the index, the module list, the plan
   lifecycle, or dispatch mechanics.
5. Confirm platform skill frontmatter names and directories match the contract:
   Claude Code and Codex both use `<project-slug>-atlas`, `<project-slug>-relay`,
   and `<project-slug>-worker`, and all three exist for every selected platform.
6. Confirm `CLAUDE.md` / `AGENTS.md` have no forced skill-invocation mandate.
7. Confirm every init-time placeholder is replaced per the placeholder map in
   `references/atlas-contract.md` — including `{{BUILD_DATE}}`,
   `{{BUILD_COMMIT}}`, and `{{ATLAS_FORMAT}}` in the index — that
   `{{INDEX_FILE}}` appears in the lead adapter and in neither of the others, and
   that `{{DATE}}` and `{{SLUG}}` remain intact in the lead and relay adapters
   (filled per change, not at initialization).

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
