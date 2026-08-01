---
name: codebase-atlas
description: "Initialize, refresh, or rebuild a repository atlas under docs/ for AI-assisted code navigation. Only for an explicit atlas build, refresh, rebuild, or rescan requested by a human — never for ordinary development, and never while executing a task package."
---

# Codebase Atlas

Codebase Atlas turns a repository into an engineering map, then generates the
role-split entrypoints for a human-mediated three-tier workflow: a lead that
specifies and reviews, a relay lead the human hands one dispatch plan to, and
implementation agents the relay lead dispatches one package each. Use it for
atlas initialization, a deliberate full rebuild, or an incremental refresh of an
existing atlas — not for ordinary follow-up development.

**Do not run this skill while executing a task package or a dispatch plan.** If
your instructions arrived with a `ROLE: worker` or `ROLE: relay-lead` header, an
atlas rebuild is out of scope — report that instead.

Keep this skill simple:

- Generated Markdown under `docs/` is the canonical atlas.
- References define the rules; templates define the output shape.
- This skill contains only rules, references, and templates — no runtime
  assumptions, helper scripts, or product-specific behavior.
- Two principles govern the design: avoid over-design — only what a task needs,
  nothing speculative; and avoid defensive design — ownership and intent over
  prohibition lists.
- Delegate the per-module scan/draft pass and the per-file verify/fix pass to
  subagents run in parallel (Agent tool). Keep module-boundary judgment, the
  index, and adapter generation centralized.

  This is **build-time** parallelism, separate from the dispatch the generated
  relay adapter describes.
- The atlas this skill generates is built for a **human-mediated three-tier**
  workflow. It produces **three** entrypoints per platform — a lead adapter for
  the agent talking to the human, a relay adapter for the agent the human hands
  the dispatch plan to, and a worker adapter for the implementation agents the
  relay lead dispatches. The relay and worker tiers run on GPT-5.6-Luna,
  reasoning Max. Read `references/delegation.md` before generating any of them.
- Determine the working language before any user-facing output. Prefer an
  explicit repository language rule, then the user's initialization request
  language, then English. Use the selected language for user-facing output and
  generated atlas docs.
- Generated Markdown is host-neutral text. Every path and link uses forward
  slashes and stays relative, even when generating on Windows, and no file is
  rewritten merely to normalize its line endings. See
  `references/atlas-contract.md` → Path And Shell Portability.

## Before Scanning

If the user only asks to run Codebase Atlas on a target repository, silently
detect the working language and whether old atlas files exist before any
user-facing output. Then introduce the skill before any full scan or
user-facing decision.

### Step 0: Detect Language Silently

Before outputting anything, determine the working language:

1. Check the repository root for an explicit language rule in files such as
   `.cursorrules`, `CONTRIBUTING.md`, `README`, or existing docs.
2. If the repository has no explicit language rule, use the language of the
   user's initialization request.
3. If neither provides a clear signal, use English.

Use this language for the introduction, confirmation dialog, and generated
atlas documents. Keep this step silent; do not report the language decision
until the confirmation dialog.

### Step 1: Detect Old Atlas And Platforms Silently

Before outputting anything, scan only for old Codebase Atlas artifacts:

1. Detect whether old atlas docs exist under `docs/`.
2. Detect whether generated Codebase Atlas entrypoints exist under `.agents/`
   or other configured prompt or skill directories.
3. Detect existence only — deep reading of old atlas content waits until the
   user asks to preserve part of it.
4. If old atlas docs or generated entrypoints exist, record them, and read one
   thing out of the existing index: its build provenance line. This is the only
   exception to "existence only" in item 3.
5. Present the choice in Step 2 and wait for the user to pick refresh, rebuild,
   or a partial preservation before continuing.
6. If the user chooses delete and rebuild, delete all of these:
   - Old atlas docs (index and module docs).
   - Legacy structures from earlier atlas versions: `*_investigate_workflow.md`,
     `*_change_workflow.md`, and `*_techniques/` folders.
   - Generated Codebase Atlas entrypoints (adapters) that point to those old
     docs, including the pre-split single adapter — `docs/<project>_adapter.md`
     and any `<project-slug>-atlas` skill whose body carries worker-side
     execution rules rather than the lead role check. A single self-contained
     adapter is the design this version replaces; it must not survive a rebuild.
     The same applies to a format-3 lead/worker pair with no `<slug>-relay`
     sibling: replace the whole set rather than adding a relay adapter alongside
     it, since the lead and worker bodies both assume the human returns.
   - Any "run the atlas skill before every operation" mandate that a previous
     atlas wrote into `CLAUDE.md` or `AGENTS.md` (remove only that block, not
     the whole file).
7. `docs/changes/` is accumulated work history, not atlas output — a rebuild
   replaces the map, not the record of what was done to the project. Deletions
   are limited to files whose Codebase Atlas origin is confirmed; unrelated
   `.agents/` content is left alone.
8. If the user wants to preserve any part, read only the parts the user asked
   to preserve after the user gives preservation instructions.
9. Detect whether a `.claude/` directory exists at the project root. If found,
   record Claude Code as a detected platform.
10. Detect whether a `.agents/` directory exists at the project root. If found,
    record Codex as a detected platform.
11. If neither `.claude/` nor `.agents/` is found, record that platform
    detection is inconclusive. The confirmation dialog in Step 3 must ask the
    user which platform they use rather than pre-selecting.

### Step 2: Introduce This Skill

Before starting any full scan or question, explain what this skill will create
for the user's project. Use the working language selected in Step 0. Render the
following meaning in that language; do not output this English template verbatim
unless English was selected:

```markdown
Before we start, here is what this skill will create for your project.

**What it creates:**
A durable engineering map under `docs/` — your project's module structure and
boundaries — plus two entrypoint skills: one for the agent you talk to, and one
for the agent that implements changes.

**How to use it later:**
You do not run this skill again. Future requests load the first entrypoint
automatically, which reads the map and routes the task.

**What you will see on every code change:**
- Before: what the current situation is and where the problem is.
- After: what will become true after the change.

Confirm from that Before / After. If the Before does not match the real problem,
say so and I will re-diagnose before anything is written.

This initialization only needs to happen once.
```

**Skip the introduction above entirely when Step 1 found an existing atlas.** Go
straight to the choice below.

If Step 1 found an existing atlas **with** a build provenance line, present this
in the working language, filling in the recorded date and commit:

```markdown
This project already has an atlas, built on <date> from commit <commit>.

A. Refresh it (recommended). I compare the repository against that commit and
   re-scan only the parts that changed, leaving everything else as it is.
B. Rebuild it from scratch. I delete the current atlas and scan the whole
   project again — slower, and any notes added to the docs by hand are lost.

Either way, tell me if there are parts you want kept as they are.
```

If an atlas exists but has **no** provenance line, no drift can be computed. Say
so and offer the two workable options:

```markdown
This project already has an atlas, but it does not record which commit it was
built from, so I cannot work out what has changed since. I can rebuild it from
scratch, or refresh only the areas you name.
```

Then route:

- **Refresh** → stop here and go to the Refresh Workflow. Do not continue to
  Step 3; a refresh inherits its decisions from the index.
- **Rebuild** → carry out the Step 1 deletions, then continue to Step 3.
- **No existing atlas** → continue directly to Step 3.

### Step 3: Pre-Scan Existing Rules

After the introduction and any old-atlas handling, pre-scan existing rules
before asking for configuration decisions:

1. Scan the repository root and `docs/` for `CONTRIBUTING.md`, `README`,
   `.cursorrules`, and any language or maintenance policy files.
2. Scan for explicit language rules, such as Traditional Chinese, Simplified
   Chinese, or English.
3. Scan for maintenance policy signals, such as pure maintenance mode, feature
   freeze, or active development.
4. Bring those findings into a confirmation dialog that explains:
   - Each existing rule found, grouped by category.
   - The concrete content of each rule, not a vague summary.
   - How each rule will be handled in the atlas.
   - Which rules will be written into the index as project operating
     constraints.
   - Which rules may need adjustment or removal.
   - The selected working language and why it was selected.
   - Recommended values for the initial decisions.
5. Present the initial decisions as plain-language questions in the working
   language. Internal setting names such as `mode`, `delivery_policy`,
   `reporting_level`, `platform_targets`, `reference_template_mode`, or
   `feature_parity` stay internal. For each decision, include the question the
   user needs to answer, the recommended value, and why that value is
   recommended.
6. Present the reference-template decision in this plain-language shape,
   translated into the working language:

   ```markdown
   Do you have a reference template or specification?

   A. No. Build the atlas from this project only.
   B. Yes, but only use selected parts of the reference. Full feature alignment
      is not required.
   C. Yes, and this project must fully match the reference's functionality.

   If you choose B, what parts should I use as reference?
   For example: only its data-flow design, only its UI structure, or only its
   error-handling approach.
   ```

   The term "feature parity" stays internal; user-facing explanations describe
   the choice in plain language.
7. Present the reporting-level decision in this plain-language shape,
   translated into the working language:

   ```markdown
   How detailed should the reports be?

   A. Plain language only. Explain what changed without showing file names,
      code paths, or technical identifiers.
   B. Include technical details. Show file names, module names, and relevant
      code context alongside the plain-language explanation.

   Recommended: B for developer-maintained projects, A for projects managed
   by non-developers.
   ```
8. Present the delivery-policy decision in this plain-language shape, translated
   into the working language:

   ```markdown
   After I build the atlas, should I commit it to git?

   A. No commit — just write the files; you review and commit yourself
      (recommended).
   B. Commit only — commit the atlas locally.
   C. Commit and push — commit and push to the remote.
   ```

   Recommended: A, so you can review the generated atlas before it enters
   history. This same policy also governs how later change work is delivered.
9. Present the platform adapter decision in this plain-language shape,
   translated into the working language. Show detected platforms pre-selected.

   If both `.claude/` and `.agents/` were detected:

   ```markdown
   Which AI platforms should receive a project skill adapter?

   Detected: Claude Code ✓  Codex ✓

   A. Both (recommended)
   B. Claude Code only
   C. Codex only
   D. None — skip adapter generation
   ```

   If only `.claude/` was detected:

   ```markdown
   Which AI platforms should receive a project skill adapter?

   Detected: Claude Code ✓

   A. Claude Code (recommended)
   B. Also add Codex
   C. None — skip adapter generation
   ```

   If only `.agents/` was detected:

   ```markdown
   Which AI platforms should receive a project skill adapter?

   Detected: Codex ✓

   A. Codex (recommended)
   B. Also add Claude Code
   C. None — skip adapter generation
   ```

   If neither was detected:

   ```markdown
   No AI platform directories were detected. Which AI assistant do you use
   in this project?

   A. Claude Code
   B. Codex
   C. Both
   D. None — skip adapter generation
   ```

10. When at least one platform adapter will be generated, state plainly how the
    generated workflow runs, so the user is not surprised by it later. Render the
    meaning in the working language:

    ```markdown
    How work will run after this is set up:

    I understand the request, clarify the desired result and acceptance evidence
    with you, split the work into task packages, and write one dispatch plan.
    You hand that single plan to your execution manager; I do not launch
    anything. It reads the packages, decides the order, runs one agent per
    package, verifies each result itself, records what happened, and commits.

    You do not need to come back to me afterwards — the records are written for
    agents to read. If you do come back, I take a second look and update the map.

    I never edit the code myself, including for changes that look trivial. A
    one-off fix like a typo does not belong in this workflow at all; hand those
    straight to an execution model.
    ```

    Do not ask a model-tier question. The execution manager and the agents it
    dispatches run on GPT-5.6-Luna with reasoning Max.
11. Use this confirmation shape for preserved rules:

    ```text
    [Category]
    Rule: <specific inherited rule>
    Handling: <how this rule will be recorded or applied>
    ```
12. Wait for user confirmation before starting the full scan.

## Rebuild Or Refresh

Decide which one this is after Step 1's detection, as part of the Step 2
conversation.

- **No atlas exists** → initialization. Run the Initialization Workflow.
- **An atlas exists and the user asked to rebuild, rescan, or start over** →
  full rebuild. Run the Initialization Workflow, including the
  delete-and-rebuild confirmation.
- **An atlas exists and the user asked to refresh, update, or sync it — or just
  said the map is out of date** → run the Refresh Workflow. It re-scans only the
  modules the repository changed under and leaves the rest untouched.

When the request is ambiguous and an atlas exists, propose the refresh and say
what it will skip.

## Initialization Workflow

1. Read `references/atlas-contract.md`.
2. Run the language detection, old-atlas detection, introduction, and pre-scan
   above, then resolve the initial decisions with the user.
3. Inspect the target repository yourself, but only shallowly: manifests,
   top-level directories, README/config, and existing docs. This pass proposes
   candidate module boundaries; deep reading of individual source files happens
   per module in Step 6.
4. Read `references/modes.md` and follow either standalone or
   reference-assisted guidance.
5. Propose the module split from the shallow pass, using change-boundary
   quality, not a hard module count. Treat this split as provisional: a
   scanning subagent in Step 6 may report that its module should merge with
   another or split further. When that happens, adjust the split and reconcile —
   the boundary follows what the scan found.
6. Scan and draft in parallel. Dispatch one subagent per candidate module
   (Agent tool, `general-purpose`, all dispatches in one message so they run
   concurrently) to deep-scan that module's scope and write its module doc
   directly. Each subagent starts with no memory of this conversation, so its
   prompt must include, inline:
   - The module's name/slug and its provisional scope (folders/files) from
     Step 5.
   - The "Module Requirements" section from `references/atlas-contract.md` and
     the `assets/templates/module.md` template content, so the subagent knows
     the exact required sections and placeholder tokens to replace.
   - The "Scan Boundaries" exclusions from `references/atlas-contract.md`
     (ignore `node_modules/`, build output, vendored code, etc.).
   - The working language from Step 0 and the reporting level from Step 3.
   - An instruction to ground every claim in committed files, write real
     uncertainty as `TODO`, and prefer routing-oriented notes over file
     inventories.
   - The exact output path to write: `docs/<project>/<module_slug>.md` (or the
     reference-assisted `docs/<project>_<reference>/<module_slug>.md`). Forward
     slashes, even on Windows. One subagent writes exactly one file, on a path
     no other subagent targets.

   These prompts are build-time instructions, not the `atlas/v3` task packages
   the generated workflow uses. They carry only what the subagent cannot derive;
   the conversation is not pasted into them.
   After all module subagents return, read their brief findings (not the full
   file contents) to reconcile the module list per Step 5's provisional-split
   note. Then draft `index.md` yourself from the reconciled module list and
   findings — keep this step centralized. Fill its build provenance line while
   you are there: today's local date, the short SHA of `HEAD` (or
   `not-a-git-repo`), and the current atlas format version from
   `references/atlas-contract.md`.
7. Read `references/delegation.md`, then generate the adapters yourself
   (centralized) for all platforms selected in Step 3.

   Each platform gets **all three**, split by role: a lead adapter (entry router,
   investigate/change discipline, Decision Gate, Before/After gate, package and
   dispatch-plan authoring, review, atlas writes), a relay adapter (ordering,
   dispatch, waiting, acceptance, completion records, commits), and a worker
   adapter (implementation only). The set is generated together — without the
   relay adapter, acceptance and archival strand whenever the human does not
   return.
   - If Claude Code was selected: create
     `.claude/skills/<project-slug>-{atlas,relay,worker}/` if needed, then
     generate `SKILL.md` in each from `assets/templates/lead_adapter.md`,
     `assets/templates/relay_adapter.md`, and
     `assets/templates/worker_adapter.md`.
   - If Codex was selected: do the same under
     `.agents/skills/<project-slug>-{atlas,relay,worker}/`. Both platforms use
     identical adapter bodies; only the destination directory differs.
   - Generate the generic set `docs/<project>_{lead,relay,worker}_adapter.md`
     (same templates with the frontmatter block dropped) only when no platform
     adapter exists this run — the user chose "None" in Step 3, or detection was
     inconclusive and no platform was picked. If a platform set exists, skip the
     generic one (see `references/atlas-contract.md` → Entrypoint Adapters →
     Generic Adapters). If generic adapter files already exist from a prior run —
     including the pre-split single `docs/<project>_adapter.md` and the format-3
     lead/worker pair — and a platform adapter now exists too, delete them now as
     part of this step, not in a later pass.
   - In every adapter set `{{PROJECT_NAME}}`, `{{DELIVERY_POLICY}}`, and
     `{{REPORTING_LEVEL}}`; in platform adapters also set `{{PROJECT_SLUG}}`
     (lead `<slug>-atlas`, relay `<slug>-relay`, worker `<slug>-worker`). Set
     `{{INDEX_FILE}}` in the **lead adapter only**, to the relative path from
     the adapter's location to the index (e.g. from
     `.claude/skills/<project-slug>-atlas/` use
     `../../../docs/<project>_index.md`) — neither the relay nor the worker
     adapter may reference the index. Leave the runtime tokens `{{DATE}}` and
     `{{SLUG}}` intact (see the placeholder map in
     `references/atlas-contract.md`). There is no model token: the relay and
     worker adapters name GPT-5.6-Luna, reasoning Max, literally.
   - Render each adapter's `description` in the Step 0 working language, and keep
     the cross-references in it: every description names **both** sibling skills,
     so an agent that loaded the wrong one self-corrects on the first line.
   - `CLAUDE.md` or `AGENTS.md` get at most a single plain-language line noting
     the navigation map lives at `docs/<project>_index.md`, added only when the
     file has no pointer to the atlas. Render it in the Step 0 working language.
   - If a rebuild detects existing adapter files, include them in the
     delete-and-rebuild confirmation (Step 1) before overwriting.
8. Verify and fix in parallel. Dispatch one subagent per generated file — the
   index, every module doc, and every adapter (lead, relay, and worker), one file
   per subagent, all dispatches in one message so they run concurrently — to
   independently re-check that single file and fix problems directly rather than
   only reporting them (each subagent has Edit access to its own file). Each
   verification subagent's prompt must include, inline:
   - The single file's path, with an explicit instruction to read and edit
     only that path, never any other generated file.
   - The checklist items from `references/quality-checklist.md` relevant to
     that file's type (index / module / lead adapter / relay adapter / worker
     adapter) and the matching requirements from `references/atlas-contract.md`
     (Index Requirements, Module Requirements, Lead Adapter Requirements, Relay
     Adapter Requirements, or Worker Adapter Requirements as applicable).
   - An instruction to fix directly whatever it finds wrong — remaining
     init-time placeholders, missing required sections, invented facts not
     grounded in the repository, file inventories instead of routing
     summaries, broken relative links, or leftover Decisions-block/workflow-doc
     references — and to report back concisely what it changed and anything it
     was not confident enough to fix itself.
   After every verification subagent returns, read their change reports,
   resolve anything flagged as not-confident yourself, then run one final
   centralized pass over `references/quality-checklist.md` for the cross-file
   concerns no single-file subagent can see alone: do local Markdown links
   resolve across files, does the index's module list match the module docs
   actually on disk, does every platform have all three adapters, and do the
   frontmatter names follow `<project-slug>-atlas` / `<project-slug>-relay` /
   `<project-slug>-worker` consistently across Claude Code and Codex. Report
   completion only after this pass.
9. Apply the delivery policy resolved in Step 3, per
   `references/atlas-contract.md` → Delivery: `no commit` stops here; `commit
   only` stages exactly this run's created/modified/deleted atlas files
   (including any generic-adapter deletion from Step 7) and commits;
   `commit and push` also pushes, and if the push is rejected because the
   remote has commits this run does not have, stop and ask the user how to
   reconcile instead of force-pushing.

## Refresh Workflow

A refresh updates an existing atlas in place. It does not re-introduce the skill,
does not re-ask the initial decisions, and does not regenerate untouched files.
Read `references/atlas-contract.md` → Refresh before starting; it defines the
drift classification this workflow executes.

1. Read the index. Take the working language, delivery policy, reporting level,
   and reference mode from it — those decisions are settled, so do not re-ask
   them. Read the build provenance line: build date, commit, atlas format
   version. If there is no provenance line, this atlas predates it: say so, and
   offer either a full rebuild or a refresh scoped to modules the user names.
2. Compute the drift set per the contract's Refresh section —
   `git diff --name-only <recorded-commit>..HEAD`, with the documented fallback
   when the commit is unreachable, and the same Scan Boundaries exclusions a
   build uses. Add `git status --porcelain` only if the user wants uncommitted
   work counted.
3. Classify every module as stale, unmapped, removed, or untouched by matching
   the drift set against each module doc's **Scope** section. Read only the Scope
   sections — do not read whole module docs to classify.
4. Present the refresh plan and wait for confirmation, in the working language
   and in plain terms: which modules will be re-scanned, which unmapped files
   turned up and what you propose to do with them (fold into an existing module,
   or open a new one), which module docs will be deleted, and how many modules
   stay untouched. Confirmation comes before any subagent runs.

   If more than roughly half the modules come back stale, or the drift is in the
   boundaries rather than inside them, recommend a full rebuild instead and say
   why.
5. Re-scan the stale and newly created modules in parallel — one subagent per
   module, all dispatches in one message, one file per subagent, disjoint paths.
   Use the same inline prompt contract as Initialization Step 6 (module scope,
   the contract's Module Requirements, the module template, scan boundaries,
   language and reporting level, ground-every-claim instruction, exact output
   path). Add one line the initialization prompt does not carry: the existing
   module doc's path, with an instruction to **update it in place** — preserve
   project-specific notes that are still true, and rewrite only what the code
   changed.
6. Update the index yourself, centrally, and only where it changed: add, remove,
   or rewrite the affected module links and summaries, and leave every untouched
   module's summary byte-identical. Delete the docs of removed modules. Do not
   touch the Architecture Decisions table.
7. Regenerate the adapters only when the index's recorded format version is
   behind the current one in `references/atlas-contract.md`, or when the user
   changed a decision this run. If you do regenerate, generate the full set of
   three per Initialization Step 7.
8. Verify only what this run wrote: one verification subagent per written file,
   same prompt shape as Initialization Step 8, then the centralized cross-file
   pass from `references/quality-checklist.md` → Refresh. Run that cross-file
   pass even for a single-module refresh.
9. Rewrite the build provenance line last, to today's date and the current
   `HEAD`, and only after verification passes.
10. Apply the delivery policy read from the index, per
    `references/atlas-contract.md` → Delivery. In the report, name both the
    modules re-scanned and the modules deliberately left alone.

## Core Rules

- Preserve useful project-specific notes and remove stale boundaries when
  overwriting atlas docs during rebuilds.
- Generated docs must describe repository-persistent facts, not facts about the
  current agent, model, editor, shell, chat session, or temporary workspace.
- Code-changing work must state a plain Before / After before any task package is
  written, and wait for explicit confirmation. It is the user-facing checkpoint;
  do not replace it with secondary engineering reports, and never run it
  agent-to-agent.
  - **Before**: current state and what is wrong, missing, confusing, or risky.
  - **After**: what the change will make true.
- There is no trivial tier. A typo, a constant, or a one-line config change goes
  straight to an execution model, not through this workflow.
- Governance files have one writer each, split by tier: the lead owns atlas docs
  and `docs/changes/planning/`; the relay lead owns completion records,
  `docs/changes/completed/`, and implementation commits. Both tiers push.
- Split generated entrypoints by role, not by activity. Understanding, deciding,
  specifying, reviewing, and knowledge maintenance ship in the lead adapter;
  ordering, dispatch, acceptance, and recording in the relay adapter;
  implementation in the worker adapter.
- The human crosses the workflow once: the lead writes files and stops, and the
  human carries the dispatch plan to the relay lead. Everything after that is
  agent-to-agent, because the human is not expected to return.
- One agent implements on the working tree at a time, and whoever holds it runs
  whatever build or test it needs. Where two packages would contend, the relay
  lead serializes them.
- The lead never edits source code or tests, at any size.
- Before proposing a change, calibrate scope: owning module, boundary modules,
  contracts, shared state, generated artifacts, tests, downstream users, and
  uncertain surfaces. Use this to reason, not as a substitute for the
  Before / After gate.
- Prefer complete, bounded plans over shortcut-oriented local patches.
- Update affected atlas docs only when module boundaries, ownership, external
  APIs, or documented repository facts change.
- Atlas updates during ordinary work are incremental: update only affected
  module docs and index entries. A scan of any kind requires the user to ask —
  a refresh re-scans only the modules that drifted, a rebuild scans everything.

## When Not To Use This Skill

Do not run Codebase Atlas for ordinary daily work after an atlas exists. The
generated lead adapter handles it: read-only tasks (explanations, investigations,
reviews, reproductions, profiling, CI failures, risk assessment) follow its
investigate path, and every code change follows its change path, ending in task
packages and one dispatch plan the user hands over.

Do not run it while executing a task package or a dispatch plan. A worker or
relay lead that finds the map stale reports that; it does not rebuild it.

Rerun Codebase Atlas only when a human explicitly asks for a rebuild, refresh,
regenerate, or rescan of the atlas itself. When they do, check which one they
need first — see Rebuild Or Refresh.
