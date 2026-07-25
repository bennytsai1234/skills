---
name: codebase-atlas
description: "Initialize or rebuild a repository atlas under docs/ for AI-assisted code navigation. Only for an explicit atlas build, rebuild, refresh, or rescan requested by a human — never for ordinary development, and never inside a delegated subagent task."
---

# Codebase Atlas

Codebase Atlas turns a repository into a compact engineering map, then generates
the role-split entrypoints that let a lead agent and cheap worker subagents work
on it without tripping over each other. Use it for atlas initialization or a
deliberate full rebuild, not for ordinary follow-up development.

**Do not run this skill inside a delegated subagent task.** If your instructions
arrived as a task contract from another agent (a prompt whose header says
`ROLE: worker`), an atlas rebuild is out of scope — report that instead.

Keep this skill simple:

- Generated Markdown under `docs/` is the canonical atlas.
- References define the rules; templates define the output shape.
- Do not add runtime assumptions, helper scripts, or product-specific behavior
  to this skill.
- Delegate the per-module scan/draft pass and the per-file verify/fix pass to
  subagents run in parallel (Agent tool). Keep module-boundary judgment, the
  index, and adapter generation centralized — those need a single holistic
  view across files that independent subagents do not share.
- The atlas this skill generates is built for a lead-plus-workers setup. It
  produces **two** entrypoints per platform — a lead adapter and a worker
  adapter — split by role rather than by activity. Read
  `references/delegation.md` before generating either.
- Determine the working language before any user-facing output. Prefer an
  explicit repository language rule, then the user's initialization request
  language, then English. Use the selected language for user-facing output and
  generated atlas docs.

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
3. Detect existence only. Do not deeply read old atlas content.
4. If old atlas docs or generated entrypoints exist, record them and tell the
   user after the skill introduction.
5. After the introduction, wait for the user to decide whether to delete and
   rebuild before continuing.
6. If the user chooses delete and rebuild, delete all of these:
   - Old atlas docs (index and module docs).
   - Legacy structures from earlier atlas versions: `*_investigate_workflow.md`,
     `*_change_workflow.md`, and `*_techniques/` folders.
   - Generated Codebase Atlas entrypoints (adapters) that point to those old
     docs, including the pre-split single adapter — `docs/<project>_adapter.md`
     and any `<project-slug>-atlas` skill whose body carries worker-side
     execution rules rather than the lead role check. A single self-contained
     adapter is the design this version replaces; it must not survive a rebuild.
   - Any "run the atlas skill before every operation" mandate that a previous
     atlas wrote into `CLAUDE.md` or `AGENTS.md` (remove only that block, not
     the whole file).
7. Do not delete unrelated `.agents/` content or any file whose Codebase Atlas
   origin cannot be confirmed.
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
Before we start, let me explain what this skill will create for your project.

**What it creates:**
This skill scans your repo once and creates a durable engineering map under
`docs/`.
That map includes:
- The project's module structure and boundaries.
- A universal entrypoint skill that future work on this project should start
  from.

**How to use it later:**
After the map exists, you do not need to run this skill again.
For future requests in this project, the universal entrypoint skill will
automatically identify what you want to do and choose the right workflow,
whether the task is understanding the project, changing code, or validating
behavior.

**Why it works:**
Before every operation, the agent reads the map instead of blindly searching the
entire repo again. This helps the agent locate the right area precisely instead
of guessing.

More importantly, every file-editing operation first explains in plain language:
- Before: what the current situation is and where the problem is.
- After: what will become true after the change.

This Before / After is the main thing you need to judge. By default the agent
reports in plain language, so you can usually confirm from the Before / After
alone without reading code. If the Before description matches the real problem
and the After description is the result you want, you can confirm. If the agent
misunderstood, the Before will be wrong and you can catch it immediately.

This initialization only needs to happen once.
```

If Step 1 detected old atlas artifacts, add this message after the introduction
in the working language:

```markdown
I found existing atlas artifacts for this project, including old atlas docs or
generated entrypoints. Should I delete them and rebuild the atlas from scratch?
If you want to preserve any parts, tell me which parts.
```

If old atlas artifacts were detected, wait for user confirmation before
continuing to Step 3. If no old atlas artifacts were detected, continue
directly to Step 3.

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
   language. Do not expose internal setting names such as `mode`,
   `delivery_policy`, `reporting_level`, `workflow_entrypoints`,
   `reference_template_mode`, or `feature_parity` to the user. For each decision, include the question the
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

   Do not use the term "feature parity" in user-facing explanations. Keep that
   term, if needed, for internal reasoning only.
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

10. Use this confirmation shape for preserved rules:

    ```text
    [Category]
    Rule: <specific inherited rule>
    Handling: <how this rule will be recorded or applied>
    ```

    The user must be able to judge whether the agent correctly understood the
    existing project guidance.
11. Wait for user confirmation before starting the full scan.

## Initialization Workflow

1. Read `references/atlas-contract.md`.
2. Run the language detection, old-atlas detection, introduction, and pre-scan
   above, then resolve the initial decisions with the user.
3. Inspect the target repository yourself, but only shallowly: manifests,
   top-level directories, README/config, and existing docs. This pass exists
   only to propose candidate module boundaries — do not deep-read individual
   source files here; that happens per module in Step 6.
4. Read `references/modes.md` and follow either standalone or
   reference-assisted guidance.
5. Propose the module split from the shallow pass, using change-boundary
   quality, not a hard module count. Treat this split as provisional: a
   scanning subagent in Step 6 may report that its module should merge with
   another or split further. When that happens, adjust the split and
   reconcile — do not force the subagent's file to fit a wrong boundary.
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
   - The resolved working language and reporting-level decisions from Step 2.
   - An instruction to ground every claim in committed files and write real
     uncertainty as `TODO` rather than inventing content, and to avoid file
     inventories in favor of routing-oriented notes.
   - The exact output path to write: `docs/<module_slug>.md` (or the
     reference-assisted path). One subagent writes exactly one file — never
     let two subagents target the same path. This is the disjoint-paths
     scheduling rule from `references/delegation.md` §4 applied to the build
     itself: these dispatches are safe to run concurrently precisely because no
     two of them can touch the same file.

   These prompts are task contracts. Keep them to what the subagent cannot
   derive, and do not paste this conversation into them.
   After all module subagents return, read their brief findings (not the full
   file contents) to reconcile the module list per Step 5's provisional-split
   note. Then draft `index.md` yourself from the reconciled module list and
   findings — the index needs a single view across every module, so keep this
   step centralized rather than delegated.
7. Read `references/delegation.md`, then generate the adapters yourself
   (centralized — adapter content follows fixed decisions and templates rather
   than per-module discovery, so delegating it adds coordination cost without
   benefit) for all platforms selected in Step 3.

   Each platform gets a **pair**, split by role: a lead adapter for the agent
   talking to the human (entry router, investigate/change discipline,
   Before/After gate, delegation, acceptance, governance writes) and a worker
   adapter for delegated subagents (contract execution only). Never generate one
   without the other — a lone lead adapter is the single-agent design this
   version replaces, and subagents will load it and start managing the project.
   - If Claude Code was selected: create `.claude/skills/<project-slug>-atlas/`
     and `.claude/skills/<project-slug>-worker/` if needed, then generate
     `SKILL.md` in each from `assets/templates/lead_adapter.md` and
     `assets/templates/worker_adapter.md`.
   - If Codex was selected: do the same under
     `.agents/skills/<project-slug>-atlas/` and
     `.agents/skills/<project-slug>-worker/`. Both platforms use identical
     adapter bodies; only the destination directory differs.
   - Generate the generic pair `docs/<project>_lead_adapter.md` and
     `docs/<project>_worker_adapter.md` (same templates with the frontmatter
     block dropped) only when no platform adapter exists this run — the user
     chose "None" in Step 3, or detection was inconclusive and no platform was
     picked. If a platform pair exists, skip the generic pair: nothing loads it
     automatically once a platform adapter does (see
     `references/atlas-contract.md` → Entrypoint Adapters → Generic Adapters).
     If generic adapter files already exist from a prior run — including the
     pre-split single `docs/<project>_adapter.md` — and a platform adapter now
     exists too, delete them now as part of this step, not in a later pass.
   - In every adapter set `{{PROJECT_NAME}}`, `{{DELIVERY_POLICY}}`, and
     `{{REPORTING_LEVEL}}`; in platform adapters also set `{{PROJECT_SLUG}}`
     (lead skill `<slug>-atlas`, worker skill `<slug>-worker`). Set
     `{{INDEX_FILE}}` in the **lead adapter only**, to the relative path from
     the adapter's location to the index (e.g. from
     `.claude/skills/<project-slug>-atlas/` use
     `../../../docs/<project>_index.md`) — the worker adapter must not reference
     the index at all. Leave the runtime tokens `{{DATE}}` and `{{SLUG}}` intact
     (see the placeholder map in `references/atlas-contract.md`).
   - Render each adapter's `description` in the Step 0 working language, and
     keep the cross-reference in it: the lead description points a subagent at
     `<project-slug>-worker`, and the worker description points a
     human-facing agent at `<project-slug>-atlas`. That description is the only
     part an agent reads before deciding to load a skill, so it carries the role
     boundary.
   - Do **not** write a forced "run the atlas skill before every operation"
     mandate into `CLAUDE.md` or `AGENTS.md`. Each skill's `description` makes
     it discoverable when a task needs it. At most, if the file has no pointer to
     the atlas, add a single plain-language line noting the navigation map lives
     at `docs/<project>_index.md`. Render it in the Step 0 working language.
   - If a rebuild detects existing adapter files, include them in the
     delete-and-rebuild confirmation (Step 1) before overwriting.
8. Verify and fix in parallel. Dispatch one subagent per generated file — the
   index, every module doc, and every adapter (lead and worker), one file per
   subagent, all dispatches in one message so they run concurrently — to
   independently re-check that single file and fix problems directly rather than
   only reporting them (each subagent has Edit access to its own file). Each
   verification subagent's prompt must include, inline:
   - The single file's path, with an explicit instruction to read and edit
     only that path, never any other generated file.
   - The checklist items from `references/quality-checklist.md` relevant to
     that file's type (index / module / lead adapter / worker adapter) and the
     matching requirements from `references/atlas-contract.md` (Index
     Requirements, Module Requirements, Lead Adapter Requirements, or Worker
     Adapter Requirements as applicable).
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
   actually on disk, does every platform have both a lead and a worker adapter,
   and do the frontmatter names follow `<project-slug>-atlas` /
   `<project-slug>-worker` consistently across Claude Code and Codex. Report
   completion only after this pass.
9. Apply the delivery policy resolved in Step 2, per
   `references/atlas-contract.md` → Delivery: `no commit` stops here; `commit
   only` stages exactly this run's created/modified/deleted atlas files
   (including any generic-adapter deletion from Step 7) and commits;
   `commit and push` also pushes, and if the push is rejected because the
   remote has commits this run does not have, stop and ask the user how to
   reconcile instead of force-pushing.

## Core Rules

- Do not blindly overwrite existing atlas docs. Preserve useful project-specific
  notes and remove stale boundaries during rebuilds.
- Generated docs must describe repository-persistent facts, not facts about the
  current agent, model, editor, shell, chat session, or temporary workspace.
- Code-changing work must state a plain Before / After before edits. This is the
  user-facing checkpoint; do not replace it with secondary engineering reports.
  It belongs to the agent talking to the human — a delegated subagent never runs
  it, because nobody is reading. At T1/T2, wait for confirmation before editing
  or dispatching; at T0 (trivial, reversible, single file), announce the
  one-line Before / After and proceed, then report:
  - **Before**: current state and what is wrong, missing, confusing, or risky.
  - **After**: what the change will make true.
- Split generated entrypoints by role, not by activity. Planning, alignment,
  review, and knowledge maintenance all belong to the same agent on the same
  timeline, so they ship in one lead adapter; execution ships separately.
- Exactly one agent writes any governance file. Whole-project builds, test
  suites, and process restarts belong to that same agent, and run only with no
  worker in flight.
- Before proposing a change, calibrate scope: owning module, boundary modules,
  contracts, shared state, generated artifacts, tests, downstream users, and
  uncertain surfaces. Use this to reason, not as a substitute for the
  Before / After gate.
- Prefer complete, bounded plans over shortcut-oriented local patches.
- Update affected atlas docs only when module boundaries, ownership, external
  APIs, or documented repository facts change.
- Atlas updates during ordinary work are incremental: update only affected
  module docs and index entries. A full rescan requires the user to explicitly
  request a rebuild.

## When Not To Use This Skill

Do not run Codebase Atlas for ordinary daily work after an atlas exists. The
generated lead adapter is self-contained and already handles daily work:
read-only tasks (explanations, investigations, reviews, reproductions, profiling,
CI failures, risk assessment) follow its investigate path, and every code edit
follows its change path, which scales discipline to the task and delegates when
the task is bounded enough to be worth a contract. Use the generated atlas for
all of these instead of rerunning Codebase Atlas.

Do not run it inside a delegated subagent task at all. A worker that decides the
map is stale reports that; it does not rebuild it.

Rerun Codebase Atlas only when a human explicitly asks for a rebuild,
refresh, regenerate, or rescan of the atlas itself.
