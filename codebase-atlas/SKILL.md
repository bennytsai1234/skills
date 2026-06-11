---
name: codebase-atlas
description: "Initialize or rebuild a repository atlas under docs/ for AI-assisted code navigation."
---

# Codebase Atlas

Codebase Atlas turns a repository into a compact engineering map. Use it for
atlas initialization or a deliberate full rebuild, not for ordinary follow-up
development.

Keep this skill simple:

- Generated Markdown under `docs/` is the canonical atlas.
- References define the rules; templates define the output shape.
- Do not add runtime assumptions, helper scripts, or product-specific behavior
  to this skill.
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
6. If the user chooses delete and rebuild, delete both:
   - Old atlas docs.
   - Generated Codebase Atlas entrypoints that point to those old docs.
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
3. Inspect the target repository: manifests, entrypoints, source roots, tests,
   build/config files, existing docs, and major package or domain boundaries.
4. Read `references/modes.md` and follow either standalone or
   reference-assisted guidance.
5. Split the project into stable modules using change-boundary quality, not a
   hard module count.
6. Create or update the canonical atlas under `docs/` using templates from
   `assets/templates/`, then copy the five technique docs from
   `assets/techniques/` verbatim into `docs/<project>_techniques/`
   (debugging.md, tdd.md, verification.md, code-review.md, design-grilling.md).
   Technique docs are constant content and need no placeholder replacement.
7. Generate two canonical workflow docs:
   - `investigate`: all read-only work — explanations, ownership and feasibility
     questions, investigations, behavior checks, reviews, reproductions,
     profiling, CI or build failure analysis, and risk assessment. Never edits
     files; hands off to change when a fix is needed.
   - `change`: all code-changing tasks. It opens by judging a discipline tier
     (T0 trivial / T1 normal / T2 hard, with a hard floor at T2 for
     irreversible, cross-module, external-API, or migration work), demotes the
     ten task types to internal hints, and pulls in the technique docs on demand
     instead of inlining them.
   Set `{{TECHNIQUES_DIR}}` in both workflows to the relative path from `docs/`
   to the techniques folder (`<project>_techniques`). Also replace the other
   init-time tokens in both workflows — `{{ATLAS_TITLE}}`, `{{REPORTING_LEVEL}}`,
   and `{{DELIVERY_POLICY}}` — but leave the runtime tokens `{{DATE}}` and
   `{{SLUG}}` in the change workflow intact (see the placeholder map in
   `references/atlas-contract.md`).
8. Generate adapters for all platforms selected in the Step 3 confirmation. Each
   adapter embeds the entry router: read the index, confirm the project in one
   sentence, then route — the user wants to know → investigate, the user wants
   to change → change.
   - Always generate `docs/<project>_adapter.md` using
     `assets/templates/adapter.md` (generic, no frontmatter).
   - If Claude Code was selected: create `.claude/skills/` at the project root
     if it does not exist, then create `.claude/skills/<project-slug>-atlas/` if
     it does not exist, and generate
     `.claude/skills/<project-slug>-atlas/SKILL.md` using
     `assets/templates/claude_code_adapter.md`.
     After generating the skill adapter, create or update `CLAUDE.md` at the
     project root. If `CLAUDE.md` does not exist, create it. If it exists,
     append only if the invocation line is not already present. Render the
     following meaning in the working language selected in Step 0; do not
     insert this English template verbatim unless English was selected:
     ```
     ## At The Start Of Every Conversation

     Before any operation, run the `/<project-slug>-atlas` skill.
     ```
     The skill name `/<project-slug>-atlas` is always in kebab-case regardless
     of language.
   - If Codex was selected: create `.agents/skills/<project-slug>-atlas/` if it
     does not exist, then generate
     `.agents/skills/<project-slug>-atlas/SKILL.md` using
     `assets/templates/codex_adapter.md`. The frontmatter `name` must be
     `<project-slug>-atlas`, matching the Claude Code adapter naming pattern.
   - In every adapter, set `{{PROJECT_NAME}}`, `{{DELIVERY_POLICY}}`, and
     `{{REPORTING_LEVEL}}` to their chosen values; in the Claude Code and Codex
     adapters also set `{{PROJECT_SLUG}}` (the generic adapter has no slug token).
     Set `{{INDEX_FILE}}`, `{{INVESTIGATE_WORKFLOW_FILE}}`, and
     `{{CHANGE_WORKFLOW_FILE}}` to the relative paths from the adapter's location
     to those `docs/` files (e.g., from `.claude/skills/<project-slug>-atlas/`
     or `.agents/skills/<project-slug>-atlas/` use
     `../../../docs/<project>_index.md`).
   - All adapters embed the entry router and point to the index and the two
     workflows — never to a single workflow as the sole target.
   - If a rebuild detects existing adapter files, include them in the
     delete-and-rebuild confirmation (Step 1) before overwriting.
9. Run `references/quality-checklist.md` before reporting completion.

## Core Rules

- Do not blindly overwrite existing atlas docs. Preserve useful project-specific
  notes and remove stale boundaries during rebuilds.
- Generated docs must describe repository-persistent facts, not facts about the
  current agent, model, editor, shell, chat session, or temporary workspace.
- Code-changing workflows must require a plain Before / After gate before
  edits. This gate is the user-facing checkpoint; do not replace it with
  secondary engineering reports:
  - **Before**: current state and what is wrong, missing, confusing, or risky.
  - **After**: what the change will make true.
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
generated adapter already routes daily work: read-only tasks (explanations,
investigations, reviews, reproductions, profiling, CI failures, risk
assessment) go to the investigate workflow, and every code edit goes to the
change workflow, which scales its discipline to the task. Use the generated
atlas for all of these instead of rerunning Codebase Atlas.

Rerun Codebase Atlas only when the user explicitly asks for a rebuild,
refresh, regenerate, or rescan of the atlas itself.
