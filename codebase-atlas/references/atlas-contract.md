# Atlas Contract

Use this contract for every Codebase Atlas initialization or rebuild.

The atlas is a compact engineering map, not a full architecture book. Keep
generated docs concise, navigable, and grounded in repository-persistent facts.
The design goal is low daily context: a routine task should load only the
self-contained entrypoint skill (lazily, on invocation) plus the index and one or
two module docs — never a chain of process files.

## Initial Decisions

Resolve these before the full scan:

- `mode`: `standalone` or `reference-assisted`. Derived from
  `reference_template_mode` (standalone when `none`, reference-assisted
  otherwise) — never asked as a separate question.
- `working_language`: explicit repository language rule first, user's
  initialization request language second, English third.
- `reference_template_mode`: `none`, `partial reference`, or `full alignment`.
  This user-facing decision determines whether the run is standalone or
  reference-assisted, and whether reference functionality is in scope.
- `delivery_policy`: `no commit`, `commit only`, or `commit and push`.
- `reporting_level`: `plain` or `technical`. Plain hides module names, file
  paths, and code snippets from user-facing reports. Technical includes them
  for developer-oriented workflows.
- `platform_targets`: platform detection runs silently in Step 1 (`.claude/`
  → Claude Code, `.agents/` → Codex). Detected platforms are pre-selected in
  the Step 3 confirmation. The generic `docs/` adapter is always generated.
  Platform-native adapters are generated only for platforms confirmed by the
  user.

Internal decision keys are for atlas generation only. User-facing confirmation
must present these decisions as plain-language questions in the working language,
with the recommended value and reason. Do not expose internal setting names such
as `mode`, `reference_template_mode`, `delivery_policy`, `reporting_level`,
`platform_targets`, or `feature_parity` directly to the user.

The reference-template decision must be presented as three plain-language
choices:

- No reference: build the atlas from the target project only.
- Partial reference: use only the user-selected parts of the reference.
- Full alignment: fully match the reference's functionality, only when the user
  explicitly asks for full alignment, parity, compatibility, migration
  equivalence, or reference-driven expansion.

When existing project guidance is found, the confirmation dialog must list each
preserved rule with concrete content and handling:

```text
[Category]
Rule: <specific inherited rule>
Handling: <how this rule will be recorded or applied>
```

## Source Of Truth

Generated docs must describe facts supported by committed files, project docs,
configuration, templates, commands, public APIs, package metadata, or explicit
integrations in the repository.

Do not write invocation-local facts into the atlas: current agent, model,
editor, shell, chat session, temporary workspace state, or session-only tools.

For every dependency, risk, flow, and ownership note, ask whether a committed
file or project doc proves it. If not, remove it or write it as uncertainty.

## Scan Boundaries

Ignore generated, vendored, dependency, cache, build, and VCS directories when
inferring module boundaries unless the user explicitly asks to document them:

- `.git/`, `.hg/`, `.svn/`
- `node_modules/`, `vendor/`, `third_party/`
- `.venv/`, `venv/`, `env/`, `.tox/`
- `dist/`, `build/`, `out/`, `target/`, `.next/`, `.nuxt/`
- `coverage/`, `.cache/`, `.turbo/`, `.parcel-cache/`
- compiled artifacts, minified bundles, and binary assets that do not define
  source ownership

Generated code may be mentioned as downstream impact, but should not define a
module unless engineers normally edit or review it directly.

## Output Shape

Standalone output:

```text
docs/
  <project>_index.md
  <project>/
    <module_slug>.md
  <project>_adapter.md
```

Reference-assisted output:

```text
docs/
  <project>_<reference>_index.md
  <project>_<reference>/
    <module_slug>.md
  <project>_<reference>_adapter.md
```

There are no separate workflow docs — change/investigate discipline lives inside
the adapter.

Use lowercase snake_case slugs for generated files and folders. Use relative
links for generated Markdown.

## Required Templates

Use the templates under `assets/templates/`:

- `index.md`
- `module.md`
- `adapter.md` (generic `docs/` adapter, no frontmatter)
- `claude_code_adapter.md` (Claude Code only)
- `codex_adapter.md` (Codex only)

Replace every init-time placeholder with concrete project values. Do not leave
init-time tokens such as `{{ATLAS_TITLE}}` or `{{DELIVERY_POLICY}}` in generated
docs. The only exceptions are the two runtime tokens `{{DATE}}` and `{{SLUG}}` in
the adapter — leave them intact; the adapter fills them per change. See the
placeholder map below.

## Placeholder Map

Replace every token below at initialization **except** the two runtime tokens,
which must survive verbatim into the generated adapter.

Init-time tokens (replace with concrete values):

| Token | Value | Appears in |
|---|---|---|
| `{{ATLAS_TITLE}}` | Project name; `<project>_<reference>` in reference-assisted mode | index |
| `{{PROJECT_NAME}}` | Human-readable project name | adapters |
| `{{PROJECT_SLUG}}` | kebab-case project slug | Claude Code / Codex adapters only |
| `{{WORKING_LANGUAGE}}` | Selected working language | index |
| `{{DELIVERY_POLICY}}` | `no commit` / `commit only` / `commit and push` | index, adapters |
| `{{REPORTING_LEVEL}}` | `plain` or `technical` | index, adapters |
| `{{REFERENCE_BOUNDARY}}` | Reference boundary block in reference-assisted mode; empty otherwise | index |
| `{{PROJECT_OPERATING_CONSTRAINTS}}` | Inherited project rules | index |
| `{{ARCHITECTURE_DECISIONS}}` | Empty-table marker at initialization | index |
| `{{INDEX_FILE}}` | Relative path from the adapter to the index | adapters |
| `{{MODULE_LINKS}}` / `{{MODULE_SUMMARIES}}` | Generated module links and routing summaries | index |
| `{{MODULE_TITLE}}` | Module name | each module doc |

Runtime tokens (leave intact — the adapter fills them per change):

| Token | Value |
|---|---|
| `{{DATE}}` | The change date in ISO 8601 `YYYY-MM-DD` (zero-padded, local date); the same string also names the day's completed folder and `summary.md` |
| `{{SLUG}}` | The per-change plan slug |

## Index Requirements

The index is the navigation map only — it holds no process and no internal
decision metadata. It must include:

- A one-line statement of what the project does and how daily work enters (through
  the adapter, which reads the index and carries its own discipline).
- A single inline line for working language, delivery policy, and reporting level.
- Project operating constraints inherited from existing guidance: concrete rules
  all work must follow, such as language, architecture, testing, release flow,
  maintenance state, CI, and work style.
- Rebuild semantics: rerunning Codebase Atlas means a full rescan and atlas
  rebuild from current repository reality.
- Links to every module doc.
- Routing-oriented summaries for each module: what it owns, when future work
  should start there, and what symptoms or task types point to it.
- Architecture Decisions table for cross-module decisions. Starts empty.
- Reference boundary when in reference-assisted mode.

Do not add a "Decisions" metadata block (atlas mode, reference template mode,
entrypoint policy) or links to workflow docs — neither exists anymore.

## Module Requirements

Each module doc must include:

- Responsibility.
- Scope: representative folders, files, public APIs, entrypoints, commands, or
  tests.
- Dependencies and downstream impact.
- Key flows.
- Change entry points and routes: where to start and what must stay synchronized.
- Known risks.
- Do not do boundaries.
- A Reference Notes section only when reference-assisted mode makes it useful.

Avoid file inventories. A module doc is successful when it helps a future agent
decide whether to start there.

## Adapter Requirements (carries the discipline)

The adapter is the single self-contained entrypoint. It replaces the old
adapter + two workflow docs. Each adapter must:

- **Entry / router**: preserve the request; read the index once; confirm in one
  plain sentence what the project does; pick only the relevant module doc(s)
  (zoom out to the module map first when unfamiliar); route by intent
  (know → investigate, change → change, mixed → investigate first); pass
  conclusions forward without rereading the index across steps.
- **Investigate (read-only)**: answer from the atlas plus the minimum code;
  separate facts from assumptions and unknowns; never edit; hand off to change
  after the user agrees. Carry one-line discipline pointers (debugging, review,
  design questions) instead of referencing external docs.
- **Change (any edit)**: judge a discipline tier and scale effort:
  - **T0 trivial** (no logic change, reversible, single file): one-line
    Before/After; skip the plan file; single most relevant check.
  - **T1 normal** (contained, reversible, clear diagnosis): one focused test when
    a cheap seam exists; scratch plan
    `docs/changes/planning/{{DATE}}-{{SLUG}}.md` before editing source.
  - **T2 hard/risky** (async/stateful, multi-module, external API, irreversible,
    perf regression, uncertain diagnosis): full discipline; same plan file;
    usually a Decision Gate.

  Hard floor: irreversible, cross-module, external-API, and migration work is at
  least T2. A plain "be quick / be thorough" override is honoured but never drops
  below the floor.
- **Before / After gate** as the only confirmation interface: Before states the
  current state and why the change is needed (the diagnosed root cause for a
  bug); After states what becomes true and how it will be verified. At T1/T2,
  wait for explicit confirmation before editing any file. At T0 (trivial,
  reversible, single file), state the one-line Before/After and proceed without
  waiting, then report after.
- **Decision Gate** when a change alters module boundaries, an external API
  contract, is irreversible or a migration, or has two or more viable approaches:
  present Context / Options (with trade-offs) / Recommendation and wait for a
  choice before the Before/After. For deep or unclear decision trees, interview
  one question at a time, each with a recommended answer, before presenting
  options.
- **Verification** scaled to the tier after edits; the verification result is in
  the user-facing report regardless of reporting level; never claim completion on
  a failed check. On completion move the plan to
  `docs/changes/completed/{{DATE}}/{{SLUG}}.md` and append its entry to that day's
  `docs/changes/completed/{{DATE}}/summary.md` (see Plan File Lifecycle).
- **Reporting & delivery**: honour the reporting level (plain: no module names,
  paths, or code; technical: include them) and record the delivery policy.
- Do not rerun Codebase Atlas initialization unless the user explicitly asks for a
  full rebuild.

### Decision recording

- Cross-module decisions: add a row to the Architecture Decisions table in the
  index (title, chosen option, affected modules, rationale).
- Module-level decisions: add a note to the affected module's Known Risks or Do
  Not Do section, referencing the index entry if cross-module.
- Do not create separate decision log files.

## Plan File Lifecycle

Change-tier work records plans and a daily summary under `docs/changes/`. T0
trivial changes skip all of this; T1 and T2 follow it.

**Date format.** Every `{{DATE}}` is ISO 8601 `YYYY-MM-DD` — zero-padded, local
date (for example `2026-06-09`, never `2026-6-9` or `06/09/2026`). The same date
string names the plan file, the day's completed folder, and that day's summary
file, so they always match.

**Layout.**

```text
docs/changes/
  planning/
    {{DATE}}-{{SLUG}}.md       # transient scratch plan, written before editing
  completed/
    {{DATE}}/                  # one folder per calendar day
      {{SLUG}}.md              # the finished plan, moved here on completion
      summary.md               # that day's work summary, appended per change
```

**Lifecycle.**

1. Before editing at T1/T2, write the plan to `planning/{{DATE}}-{{SLUG}}.md`.
2. On completion, move it to `completed/{{DATE}}/{{SLUG}}.md` (create the date
   folder if missing). No copy is left behind in `planning/`.
3. In the same step, append one line for the change to
   `completed/{{DATE}}/summary.md` (create it if missing), newest last:

   ```text
   - {{SLUG}} — <one-line what changed> · T<tier> · <verification result> · <delivery>
   ```

   This file is the daily work summary; it accumulates every completed change for
   that date.

The plan files and summary are developer artifacts and may name modules and files
regardless of reporting level — the reporting level governs only user-facing chat
reports. Their delivery (commit/push) follows the same delivery policy as the rest
of the change.

## Incremental Atlas Updates

During ordinary work, atlas updates are incremental:

1. Update only the affected module doc or docs.
2. If the module list or module summaries in the index changed, update the index.
3. Do not rescan unrelated modules.
4. Note what changed and why in the report.

A full rescan and rebuild requires the user to explicitly request it by running
Codebase Atlas again.

## Entrypoint Adapters

Generate adapters for every initialization or rebuild based on platform detection
and user confirmation. Every adapter is self-contained per the Adapter
Requirements above and reads the index before acting.

### Generic Adapter (always generated)

- **Path:** `docs/<project>_adapter.md`
- **Template:** `assets/templates/adapter.md`
- No frontmatter. Works as a plain reference doc.

### Claude Code Adapter (when selected)

- **Path:** `.claude/skills/<project-slug>-atlas/SKILL.md`
- **Template:** `assets/templates/claude_code_adapter.md`
- **Frontmatter required:**
  - `name: <project-slug>-atlas`
  - `description` (render in the working language selected in Step 0; English
    shown here): `Codebase Atlas for <PROJECT_NAME> — navigation map and change
    discipline. Use before investigating or editing this project's code.`
- Set `{{INDEX_FILE}}` to the relative path from
  `.claude/skills/<project-slug>-atlas/` to the index
  (e.g., `../../../docs/<project>_index.md`). Also set `{{PROJECT_NAME}}`,
  `{{PROJECT_SLUG}}`, `{{DELIVERY_POLICY}}`, and `{{REPORTING_LEVEL}}`.
- Create `.claude/skills/` and the `.claude/skills/<project-slug>-atlas/`
  directory at the project root if they do not exist.

### Codex Adapter (when selected)

- **Path:** `.agents/skills/<project-slug>-atlas/SKILL.md`
- **Template:** `assets/templates/codex_adapter.md`
- **Frontmatter required:**
  - `name: <project-slug>-atlas`
  - `description` (render in the working language; English shown here): `Codebase
    Atlas for <PROJECT_NAME> — navigation map and change discipline. Use before
    investigating or editing this project's code.`
- Set `{{INDEX_FILE}}` to the relative path from
  `.agents/skills/<project-slug>-atlas/` to the index.
- Create `.agents/skills/<project-slug>-atlas/` if it does not exist.

### Do Not Force-Load The Skill

Do not write a "run the atlas skill before every operation" mandate into
`CLAUDE.md` or any always-on config. The skill's `description` lets the assistant
discover it when a task actually needs repo navigation. At most, add a single
plain-language pointer line to `CLAUDE.md` noting that the navigation map lives at
`docs/<project>_index.md`, and only if `CLAUDE.md` does not already say so.

### All Adapters Must

- Be self-contained: embed the entry router and the change/investigate discipline
  per the Adapter Requirements. Do not point to separate workflow docs.
- Read the atlas index before any operation.
- Include the delivery policy and reporting level.
- Be included in delete-and-rebuild detection during Step 1 of a rebuild.
