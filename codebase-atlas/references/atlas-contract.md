# Atlas Contract

Use this contract for every Codebase Atlas initialization, rebuild, or refresh.

Generated docs must be navigable and grounded in repository-persistent facts.

Two principles govern everything this skill writes: **avoid over-design** — say
only what a future task needs, nothing speculative; and **avoid defensive
design** — state ownership and intent rather than prohibition lists.

**There is no length limit on any generated file.** Write what routing a future
agent requires, then stop; a finished doc stands as written.

What is constrained is *what kind* of content goes where: the map answers *what
owns this, where do I start, what must I not break*; search answers *where
exactly is it*. Search-answerable detail belongs to live search, not to the map.
This is a content rule, not a length rule.

This skill produces the map only. The agents that read it and do the day-to-day
work — `atlas-planner`, `atlas-relay`, `atlas-worker`, `atlas-fast` — are
already-installed skills that apply to every project; nothing about them is
generated here. Their doctrine lives in `atlas-planner`'s
`references/delegation.md`, not in this contract.

## Atlas Format Version

**Current atlas format: `5`.** Format 5 is the map alone — an index and module
docs, read by global skills that need no per-project generation. Format 4 was
the same map plus three generated per-project adapter skills implementing a
human-mediated three-tier workflow (lead / relay / worker). Format 3 was the
same split without the relay tier. Format 2 was the lead-dispatches-cheap-
subagents split. Format 1 was a single self-contained adapter with separate
workflow docs.

Every generated index records the format it was built to. An index recording
format 4 or below has legacy per-project entrypoint skills alongside it — see
Step 1 → Detect Old Atlas Silently in `SKILL.md` for how a rebuild removes them.

Bump the format only when the map's own required shape changes, never for
wording changes inside a template.

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
- `delivery_policy`: `no commit`, `commit only`, or `commit and push`. Read
  later by `atlas-planner` and `atlas-relay` from the index for their own
  writes.
- `reporting_level`: `plain` or `technical`. Plain hides module names, file
  paths, and code snippets from user-facing reports. Technical includes them
  for developer-oriented workflows.

Internal decision keys are for atlas generation only. User-facing confirmation
presents these decisions as plain-language questions in the working language,
with the recommended value and reason; internal setting names such as `mode`,
`reference_template_mode`, `delivery_policy`, `reporting_level`, or
`feature_parity` stay internal.

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

The atlas records repository-persistent facts. Invocation-local facts — current
agent, model, editor, shell, chat session, temporary workspace state, or
session-only tools — are outside its scope.

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

Generated code may be mentioned as downstream impact; it defines a module only
when engineers normally edit or review it directly.

## Map Tiers

The map is layered so no agent loads more of it than its task needs:

| Tier | Where | Who loads it |
|---|---|---|
| 1 — project overview | top of the index | any agent, once |
| 2 — module routing | index module list + summaries | `atlas-planner`, once |
| 3 — module detail | `docs/<project>/<module_slug>.md` | whoever works in that module |
| 4 — live search | grep, symbol search, call hierarchy | whoever needs an exact location |

Tiers are scope classes, not size classes. None has a line budget and none is
trimmed to fit one. Tier 1-2 route *between* modules; tier 3 explains *inside*
one. Content that only matters once you are already working in a module belongs
in that module's doc, not the index.

A task package names tier-3 starting points. `atlas-worker` reads those first,
then explores whatever the change requires.

Search-answerable detail (call sites, symbol lists, file inventories) belongs to
live search, not to any tier of the map.

## Output Shape

Standalone output:

```text
docs/
  <project>_index.md
  <project>/
    <module_slug>.md
```

Reference-assisted output:

```text
docs/
  <project>_<reference>_index.md
  <project>_<reference>/
    <module_slug>.md
```

Use lowercase snake_case slugs for generated files and folders. Use relative
links for generated Markdown.

## Path And Shell Portability

**Paths in generated Markdown are POSIX-shaped, always.** Forward slashes,
relative, no drive letters, no backslashes, no `~`. This holds for module doc
links and every value this skill writes, on every host — including Windows,
where mirroring what a shell prints produces `docs\project\module.md` and
breaks every link.

**Do not rewrite a file to change its line endings.** Write the lines that
changed and leave the rest of the file untouched.

## Required Templates

Use the templates under `assets/templates/`:

- `index.md`
- `module.md`

Replace every init-time placeholder with concrete project values at
initialization. See the placeholder map below.

## Placeholder Map

Replace every token below at initialization.

| Token | Value | Appears in |
|---|---|---|
| `{{ATLAS_TITLE}}` | Project name; `<project>_<reference>` in reference-assisted mode | index |
| `{{WORKING_LANGUAGE}}` | Selected working language | index |
| `{{BUILD_DATE}}` | ISO `YYYY-MM-DD` on which this atlas was built or last refreshed | index |
| `{{BUILD_COMMIT}}` | Short SHA of `HEAD` at build time; `not-a-git-repo` when the project is not under git | index |
| `{{ATLAS_FORMAT}}` | The atlas format version generated — see Atlas Format Version | index |
| `{{DELIVERY_POLICY}}` | `no commit` / `commit only` / `commit and push` | index |
| `{{REPORTING_LEVEL}}` | `plain` or `technical` | index |
| `{{REFERENCE_BOUNDARY}}` | Reference boundary block in reference-assisted mode; empty otherwise | index |
| `{{PROJECT_OPERATING_CONSTRAINTS}}` | Inherited project rules | index |
| `{{ARCHITECTURE_DECISIONS}}` | Empty-table marker at initialization | index |
| `{{MODULE_LINKS}}` / `{{MODULE_SUMMARIES}}` | Generated module links and routing summaries | index |
| `{{MODULE_TITLE}}` | Module name | each module doc |

## Index Requirements

The index is the navigation map only — it holds no process and no internal
decision metadata. It carries map tiers 1 and 2 (see Map Tiers). There is no
length limit; write every module the project has, and route each one properly.
It must include:

- A one-line statement of what the project does and how daily work enters
  (through `atlas-planner`, which reads the index and carries its own
  discipline; `atlas-relay` enters through a dispatch plan and `atlas-worker`
  through a task package — neither reads the index).
- A single inline line for working language, delivery policy, and reporting level.
- A **build provenance line**, required: when this atlas was built or last
  refreshed, the commit it was built from, and the atlas format version. Keep it
  on one line directly under the settings line. Refresh reads this line to
  compute what drifted.
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

The index has no "Decisions" metadata block (atlas mode, reference template
mode) and no workflow-doc links — workflow docs do not exist.

## Module Requirements

Each module doc must include:

- Responsibility.
- Scope: representative folders, files, public APIs, entrypoints, commands, or
  tests.
- Dependencies and downstream impact.
- Key flows.
- Change entry points and routes: where to start and what must stay synchronized.
- Known risks.
- Boundaries.
- A Reference Notes section only when reference-assisted mode makes it useful.

File inventories do not serve routing. A module doc succeeds when it helps a
future agent decide whether to start there, and work confidently once it has.
There is no line budget — write for routing, not for a target length.

Write **Boundaries** and **Known Risks** as repository-specific facts,
invariants, and hidden constraints — not a catalogue of generic engineering
rules. `atlas-planner` copies only the items relevant to a task into a package's
`Constraints` section.

## Incremental Atlas Updates

During ordinary work, atlas updates are incremental — this is `atlas-planner`'s
and `atlas-relay`'s job, not this skill's:

1. Update only the affected module doc or docs.
2. If the module list or module summaries in the index changed, update the index.
3. Do not rescan unrelated modules.
4. Note what changed and why in the report.

When the map has drifted from work this skill did not track, run a Refresh
instead.

## Refresh

A refresh brings an existing atlas back in line with the repository without
rebuilding it.

**Preconditions.** An atlas exists, and its index carries a build provenance
line. With no provenance, no drift set can be computed — offer a full rebuild, or
a refresh scoped to modules the user names by hand.

**Decisions are not re-asked.** Working language, delivery policy, reporting
level, and reference mode are read back out of the index. A refresh re-opens a
decision only if the user raises it.

**Drift set.** The changed files between the recorded commit and `HEAD`:

- `git diff --name-only <recorded-commit>..HEAD` when the commit is reachable.
- When it is not (rebased, squashed, shallow clone), fall back to
  `git log --since=<recorded-date> --name-only --pretty=format:` and tell the
  user — that form over-reports.
- Apply the same Scan Boundaries exclusions as a build. A refreshed lockfile or a
  rebuilt `dist/` is not module drift.

**Classification.** Map the drift set onto modules through each module doc's
**Scope** section:

| Class | Meaning | Action |
|---|---|---|
| stale | the module owns at least one changed file | re-scan, update its doc in place |
| unmapped | a changed file falls in no module's scope | needs a boundary judgement — see below |
| removed | the module's whole scope is gone from the tree | delete the doc, drop it from the index |
| untouched | everything else | do not re-scan, do not re-read, do not rewrite |

Leave untouched docs byte-identical.

**Unmapped files** mean a new module was added, an existing module's scope grew
past what its doc claims, or a boundary moved. This skill resolves this centrally
and confirms it with the user; never let a scanning subagent infer it.

**Escalate to a full rebuild** — after saying why and getting agreement — when
there is no usable provenance, when more than roughly half the modules come back
stale, or when the drift is in the boundaries themselves rather than inside them.

**What a refresh never touches:** the Architecture Decisions table and anything
under `docs/changes/`.

**Provenance is rewritten last**, to the current date and `HEAD`, and only after
verification passes.

## Delivery

Apply the resolved `delivery_policy` once the atlas has been generated and
verification (`references/quality-checklist.md`) has passed:

- `no commit`: stop. Leave the working tree for the user to review and commit
  themselves.
- `commit only`: stage exactly the files this run created, modified, or
  deleted (index, module docs, any legacy-entrypoint deletion, and a
  `CLAUDE.md` pointer line if added) and commit with a message describing the
  atlas change. Do not stage unrelated pending changes and do not push.
- `commit and push`: do the same commit, then push. If the push is rejected
  because the remote has commits this run does not have, stop and ask the
  user how to reconcile (merge or rebase) rather than force-pushing. Never
  force-push atlas commits.
