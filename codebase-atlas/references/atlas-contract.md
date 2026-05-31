# Atlas Contract

Use this contract for every Codebase Atlas initialization or rebuild.

The atlas is a compact engineering map, not a full architecture book. Keep
generated docs concise, navigable, and grounded in repository-persistent facts.

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
- `workflow_entrypoints`: platform detection runs silently in Step 1 (`.claude/`
  → Claude Code, `.agents/` → Codex). Detected platforms are pre-selected in
  the Step 3 confirmation. The generic `docs/` adapter is always generated.
  Platform-native adapters are generated only for platforms confirmed by the
  user.

Internal decision keys are for atlas generation only. User-facing confirmation
must present these decisions as plain-language questions in the working
language, with the recommended value and reason. Do not expose internal setting
names such as `mode`, `reference_template_mode`, `delivery_policy`,
`reporting_level`, `workflow_entrypoints`, or `feature_parity` directly to the
user.

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
  <project>_investigate_workflow.md
  <project>_change_workflow.md
  <project>_techniques/
    debugging.md
    tdd.md
    verification.md
    code-review.md
    design-grilling.md
  <project>_adapter.md
```

Reference-assisted output:

```text
docs/
  <project>_<reference>_index.md
  <project>_<reference>/
    <module_slug>.md
  <project>_<reference>_investigate_workflow.md
  <project>_<reference>_change_workflow.md
  <project>_<reference>_techniques/
    debugging.md
    tdd.md
    verification.md
    code-review.md
    design-grilling.md
  <project>_<reference>_adapter.md
```

Use lowercase snake_case slugs for generated files and folders. Use relative
links for generated Markdown.

## Required Templates

Use the templates under `assets/templates/`:

- `index.md`
- `module.md`
- `investigate_workflow.md`
- `change_workflow.md`
- `adapter.md`
- `claude_code_adapter.md` (Claude Code only)

Replace every init-time placeholder with concrete project values. Do not leave
init-time tokens such as `{{ATLAS_TITLE}}` or `{{DELIVERY_POLICY}}` in generated
docs. The only exceptions are the two runtime tokens `{{DATE}}` and `{{SLUG}}` in
the change workflow — leave them intact; the daily workflow fills them per change.
See the placeholder map below.

Copy the discipline docs under `assets/techniques/` (`debugging.md`, `tdd.md`,
`verification.md`, `code-review.md`, `design-grilling.md`) verbatim into
`docs/<project>_techniques/`.
They are constant content with no placeholders to replace.

## Placeholder Map

Replace every token below at initialization **except** the two runtime tokens,
which must survive verbatim into the generated change workflow.

Init-time tokens (replace with concrete values):

| Token | Value | Appears in |
|---|---|---|
| `{{ATLAS_TITLE}}` | Project name; `<project>_<reference>` in reference-assisted mode | index, both workflows |
| `{{PROJECT_NAME}}` | Human-readable project name | adapters |
| `{{PROJECT_SLUG}}` | kebab-case project slug | Claude Code / Codex adapters only |
| `{{ATLAS_MODE}}` | `standalone` or `reference-assisted` (derived) | index |
| `{{WORKING_LANGUAGE}}` | Selected working language | index |
| `{{REFERENCE_TEMPLATE_MODE}}` | `none` / `partial reference` / `full alignment` | index |
| `{{DELIVERY_POLICY}}` | `no commit` / `commit only` / `commit and push` | index, both workflows, adapters |
| `{{REPORTING_LEVEL}}` | `plain` or `technical` | index, both workflows, adapters |
| `{{WORKFLOW_ENTRYPOINT_POLICY}}` | One-line summary of which adapters were generated (e.g. "Generic + Claude Code") | index |
| `{{WORKFLOW_ENTRYPOINTS}}` | List of generated adapter paths/links | index |
| `{{REFERENCE_BOUNDARY}}` | Reference boundary block in reference-assisted mode; empty otherwise | index |
| `{{PROJECT_OPERATING_CONSTRAINTS}}` | Inherited project rules | index |
| `{{ARCHITECTURE_DECISIONS}}` | Empty-table marker at initialization | index |
| `{{TECHNIQUES_DIR}}` | Relative path from the doc to `<project>_techniques/` | index, both workflows |
| `{{INVESTIGATE_WORKFLOW_LINK}}` / `{{CHANGE_WORKFLOW_LINK}}` | Relative links from the index to each workflow | index |
| `{{INDEX_FILE}}` / `{{INVESTIGATE_WORKFLOW_FILE}}` / `{{CHANGE_WORKFLOW_FILE}}` | Relative paths from the adapter to those `docs/` files | adapters |
| `{{MODULE_LINKS}}` / `{{MODULE_SUMMARIES}}` | Generated module links and routing summaries | index |
| `{{MODULE_TITLE}}` | Module name | each module doc |

Runtime tokens (leave intact — the daily change workflow fills them per change):

| Token | Value |
|---|---|
| `{{DATE}}` | The change date (`YYYY-MM-DD`) when a plan is written |
| `{{SLUG}}` | The per-change plan slug |

## Index Requirements

The index must include:

- Purpose and usage rules.
- Initial decisions: mode, working language, reference template mode, delivery
  policy, reporting level, and entrypoints.
- Project operating constraints inherited from existing guidance. This section
  must capture concrete rules that all workflows must follow, such as language,
  architecture, testing, release flow, maintenance state, CI, and work style.
- Rebuild semantics: rerunning Codebase Atlas means a full rescan and atlas
  rebuild from current repository reality.
- Links to the two workflow docs (investigate, change) and a pointer to the
  techniques folder. The adapter is the daily entrypoint and reads the index
  first.
- Links to every module doc.
- Routing-oriented summaries for each module: what it owns, when future work
  should start there, and what symptoms or task types point to it.
- Architecture Decisions table for cross-module decisions recorded during
  development. Starts empty at initialization.
- Reference boundary when in reference-assisted mode.

## Module Requirements

Each module doc must include:

- Current responsibility.
- Scope: representative folders, files, public APIs, entrypoints, commands, or
  tests.
- Dependencies and downstream impact.
- Key flows.
- Common change entry points.
- Change routes: where to start and what must stay synchronized.
- Known risks.
- Do not do boundaries.
- Reference notes only when reference-assisted mode makes them useful.

Avoid file inventories. A module doc is successful when it helps a future agent
decide whether to start there.

## Workflow Requirements

Generate two canonical workflows, split on the read/write boundary. The ten
change task types and the investigate read-question types are demoted to internal
hints the agent picks — they are no longer separate workflows.

- `investigate` (read-only): explanations, ownership and feasibility questions,
  investigations, behavior checks, reviews, reproductions, profiling, CI or
  build failure analysis, and risk assessment. It never edits files; it hands
  off to `change` when a fix is needed. It reads `debugging.md` (why-broken /
  CI), `code-review.md` (review), and `design-grilling.md` (open
  feasibility/approach questions) on demand, and zooms out to the module map
  when unfamiliar with an area.
- `change` (write): all code-changing tasks. It opens by judging a discipline
  tier, classifies the task into one of ten internal types, and pulls in the
  technique docs on demand instead of inlining them.

The entry router lives in the adapter, not in a separate workflow doc: it reads
the index first, confirms in one plain sentence what the project does, and
routes read→investigate / write→change, composing them for mixed intent and
passing conclusions forward so later steps do not reread the index. After each
task it asks whether anything else needs handling and routes the next request
without rereading the index.

All workflows must:

- Inspect code only after reading relevant atlas context.
- Read a technique doc from `<project>_techniques/` only when the task calls for
  it; never inline technique content into the workflow docs.
- Record the same delivery policy as the index.
- Report to the user according to the selected reporting level (plain: no module
  names, file paths, or code; technical: include them), keeping internal
  reasoning separate from the user-facing summary.
- Require atlas updates only when module boundaries, ownership, external APIs, or
  documented repository facts change.
- Choose the relevant module context and any necessary boundary context before
  inspecting code.
- Treat Before / After as the only human confirmation interface.

### Discipline tiers (the `change` workflow)

The `change` workflow opens by judging how much discipline the task warrants and
scales technique use, plan recording, and verification to it:

- **T0 trivial** (no behaviour-logic change, reversible, single file): no
  debugging/TDD; one-line Before/After; skip the plan file; run the single
  most relevant check.
- **T1 normal** (contained, reversible, clear diagnosis): light technique path;
  one focused test when a cheap seam exists; short plan as uncommitted scratch;
  type-appropriate test subset.
- **T2 hard/risky** (intermittent/async/stateful bug, multi-module, external
  API, irreversible, performance regression, or uncertain diagnosis): full
  discipline; usually triggers the Decision Gate; full verification.

Hard floor: irreversible, cross-module, external-API, and migration work is at
least T2 — conditions that usually also trip the Decision Gate, though
multi-module work that leaves boundaries intact may not. The agent judges the
tier automatically; a plain user override ("be quick" / "be thorough") is
honoured but never drops below the hard floor.

### Gates and verification

The `change` workflow must require a plain Before / After gate before file
edits; `investigate` must require the same gate before any follow-up edit. The
Before statement must state the diagnosed root cause or nature of the problem in
plain language, and the After must state how the result will be verified — this
is what lets the user catch a shallow or wrong diagnosis. The gate is the
user-facing checkpoint; do not replace it with secondary engineering reports.

The `change` workflow must escalate to a Decision Gate when the change alters
module boundaries, affects external API contracts, involves irreversible
operations, has multiple viable approaches with different trade-offs, or is
classified internally as a migration. When the decision tree is deep or
requirements are unclear, the Decision Gate first resolves them via
`design-grilling.md` (one question at a time, each with a recommended answer);
it then presents options and trade-offs before the Before / After step.

The `change` workflow must run a minimum verification step after edits, scaled
to the tier and following `verification.md`. The verification result is included
in the user-facing report regardless of reporting level. If verification fails,
the workflow does not claim completion.

At tier T1 or T2 the `change` workflow writes a short engineering plan to
`docs/changes/<YYYY-MM-DD>-<slug>.md` before editing source files; T0 skips this.
At T1 the plan is uncommitted scratch. At T2 the workflow commits it
(`plan: <slug>`) only when the delivery policy allows commits (`commit only` or
`commit and push`); under `no commit` the plan stays uncommitted. The plan is
internal scratch and does not replace the Before / After gate.

Before any proposed implementation route, workflows must calibrate scope:
owning module, boundary modules, contracts, shared state, persistence, generated
artifacts, tests, downstream users, and uncertain surfaces. Prefer complete,
bounded plans over shortcut-oriented local patches. Scope calibration is
reasoning support; the user-facing confirmation remains Before / After.



## Incremental Atlas Updates

During ordinary workflow operations, atlas updates are incremental:

1. Update only the affected module doc or docs.
2. If the module list or module summaries in the index changed, update the
   index to match.
3. Do not rescan unrelated modules or regenerate workflow docs.
4. Note what changed and why in the report.

A full rescan and rebuild requires the user to explicitly request it by running
Codebase Atlas again.

## Decision Recording

When a Decision Gate is used during a workflow:

- Cross-module decisions: add a row to the Architecture Decisions table in the
  index with the decision title, chosen option, affected modules, and rationale.
- Module-level decisions: add a note to the affected module's Known Risks or
  Do Not Do section, referencing the index entry if cross-module.
- Do not create separate decision log files.

## Entrypoint Adapters

Generate adapters for every initialization or rebuild based on platform
detection and user confirmation.

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
    shown here): `Codebase Atlas entrypoint for <PROJECT_NAME> — reads the atlas
    index and routes before acting.`
- Set `{{INDEX_FILE}}`, `{{INVESTIGATE_WORKFLOW_FILE}}`, and
  `{{CHANGE_WORKFLOW_FILE}}` to relative paths from
  `.claude/skills/<project-slug>-atlas/` to `docs/`
  (e.g., `../../../docs/<project>_index.md`). Also set `{{PROJECT_NAME}}`,
  `{{PROJECT_SLUG}}`, `{{DELIVERY_POLICY}}`, and `{{REPORTING_LEVEL}}`.
- Create `.claude/skills/` and the `.claude/skills/<project-slug>-atlas/`
  directory at the project root if they do not exist.

### Codex Adapter (when selected)

- **Path:** `.agents/skills/<project-slug>/SKILL.md`
- Uses the same thin-adapter pattern with frontmatter `name` and `description`.
- `description` format (render in the working language selected in Step 0;
  English shown here): `Codebase Atlas entrypoint for <PROJECT_NAME> — reads the atlas index and routes before acting.`
- Set `{{INDEX_FILE}}`, `{{INVESTIGATE_WORKFLOW_FILE}}`, and
  `{{CHANGE_WORKFLOW_FILE}}` to relative paths from
  `.agents/skills/<project-slug>/` to `docs/`
  (e.g., `../../../docs/<project>_index.md`).
- Create `.agents/skills/<project-slug>/` if it does not exist.

### All Adapters Must

- Embed the entry router and point to the index and the two workflows, not to a
  single workflow as the sole target.
- Include the delivery policy and reporting level.
- Read the atlas index before any operation.
- Stay thin — do not copy any workflow body or technique content.
- Be included in delete-and-rebuild detection during Step 1 of a rebuild.
