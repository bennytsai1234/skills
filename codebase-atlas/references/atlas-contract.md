# Atlas Contract

Use this contract for every Codebase Atlas initialization, rebuild, or refresh.

Generated docs must be navigable and grounded in repository-persistent facts.

**There is no length limit on any generated file.** Do not compress, trim, or
summarize a doc after writing it. Write what routing a future agent requires,
then stop.

What is constrained is *what kind* of content goes where: the map answers *what
owns this, where do I start, what must I not break*; search answers *where
exactly is it*. Keep search-answerable detail out of the map. This is a content
rule, not a length rule.

The atlas targets a **human-mediated two-agent** setup. Two entrypoints are
generated, split by **role**: a lead adapter for the agent talking to the human,
and a worker adapter for the implementation agent the human hands a task package
to. The lead does not spawn the worker — it writes a package to a file and the
human carries it across. Read `references/delegation.md` before generating either
adapter.

## Atlas Format Version

**Current atlas format: `3`.** Format 3 is the human-mediated split: the lead
specifies and reviews but does not implement or dispatch, and the worker is a
strong agent that explores, designs across files, and owns its own tests and
build. Format 2 was the lead-dispatches-cheap-subagents split. Format 1 was the
single self-contained adapter with separate workflow docs.

Every generated index records the format it was built to. An index recording a
format below the current one has adapters built to a workflow that no longer
applies: regenerate the adapter pair — a refresh of the map alone will not fix
it.

Bump the format only when the generated file set or the adapter split changes
shape, never for wording changes inside a template.

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
  the Step 3 confirmation. Each confirmed platform gets a lead + worker adapter
  pair. The generic `docs/` adapters are generated only when no platform-native
  adapter exists — see Entrypoint Adapters → Generic Adapters.

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

## Map Tiers

The map is layered so no agent loads more of it than its task needs:

| Tier | Where | Who loads it |
|---|---|---|
| 1 — project overview | top of the index | any agent, once |
| 2 — module routing | index module list + summaries | the lead, once |
| 3 — module detail | `docs/<project>/<module_slug>.md` | whoever works in that module |
| 4 — live search | grep, symbol search, call hierarchy | whoever needs an exact location |

Tiers are scope classes, not size classes. None has a line budget and none is
trimmed to fit one. Tier 1-2 route *between* modules; tier 3 explains *inside*
one. Content that only matters once you are already working in a module belongs
in that module's doc, not the index.

A task package names tier-3 starting points. The worker reads those first, then
explores whatever the change requires.

Do not push search-answerable detail (call sites, symbol lists, file
inventories) into any tier of the map.

## Output Shape

Standalone output:

```text
docs/
  <project>_index.md
  <project>/
    <module_slug>.md
  <project>_lead_adapter.md     # only when no platform adapter exists — see
  <project>_worker_adapter.md   # Entrypoint Adapters → Generic Adapters
```

Reference-assisted output:

```text
docs/
  <project>_<reference>_index.md
  <project>_<reference>/
    <module_slug>.md
  <project>_<reference>_lead_adapter.md     # only when no platform adapter exists
  <project>_<reference>_worker_adapter.md
```

There are no separate workflow docs — change/investigate discipline lives inside
the lead adapter, and execution discipline inside the worker adapter.

Use lowercase snake_case slugs for generated files and folders. Use relative
links for generated Markdown.

## Path And Shell Portability

**Paths in generated Markdown are POSIX-shaped, always.** Forward slashes,
relative, no drive letters, no backslashes, no `~`. This holds for module doc
links, the `{{INDEX_FILE}}` value, and a task package's `Starting Points` and
`Scope` entries, on every host — including Windows, where mirroring what a shell
prints produces `docs\project\module.md` and breaks every link.

**Do not rewrite a file to change its line endings.** Write the lines that
changed and leave the rest of the file untouched.

**Commands written into the atlas must run in the shell that will run them.** A
worker executes the lead's `Acceptance` and evidence commands verbatim:

- Chain nothing. One command per line, not an `&&` chain — Windows PowerShell
  5.1 has no `&&`.
- On a Windows host, do not write inline environment prefixes
  (`NODE_ENV=test cmd`), `2>/dev/null`, `rm -rf`, or POSIX utilities (`grep`,
  `sed`, `head`) as though they were on `PATH`.
- Prefer the project's own runner — `npm test`, `pytest tests/auth -q`,
  `dotnet build`. Reach for shell syntax only when no runner covers the check.

## Required Templates

Use the templates under `assets/templates/`:

- `index.md`
- `module.md`
- `lead_adapter.md` — the lead entrypoint, for the agent in contact with a human
- `worker_adapter.md` — the worker entrypoint, for the implementation agent a
  human hands a task package to

Both adapter templates ship with platform frontmatter at the top. Generate a
platform adapter by keeping that frontmatter and filling `{{PROJECT_SLUG}}`;
generate a generic `docs/` adapter by dropping the frontmatter block entirely.
Claude Code and Codex use identical adapter bodies — only the destination path
differs, so there is one template per role rather than one per platform.

Replace every init-time placeholder with concrete project values. Do not leave
init-time tokens such as `{{ATLAS_TITLE}}` or `{{DELIVERY_POLICY}}` in generated
docs. The only exceptions are the two runtime tokens `{{DATE}}` and `{{SLUG}}` in
the lead adapter — leave them intact; the lead adapter fills them per change. See the
placeholder map below.

## Placeholder Map

Replace every token below at initialization **except** the two runtime tokens,
which must survive verbatim into the generated adapter.

Init-time tokens (replace with concrete values):

| Token | Value | Appears in |
|---|---|---|
| `{{ATLAS_TITLE}}` | Project name; `<project>_<reference>` in reference-assisted mode | index |
| `{{PROJECT_NAME}}` | Human-readable project name | adapters |
| `{{PROJECT_SLUG}}` | kebab-case project slug; the lead skill is `<slug>-atlas`, the worker skill `<slug>-worker` | platform adapters only |
| `{{WORKING_LANGUAGE}}` | Selected working language | index |
| `{{BUILD_DATE}}` | ISO `YYYY-MM-DD` on which this atlas was built or last refreshed | index |
| `{{BUILD_COMMIT}}` | Short SHA of `HEAD` at build time; `not-a-git-repo` when the project is not under git | index |
| `{{ATLAS_FORMAT}}` | The atlas format version generated — see Atlas Format Version | index |
| `{{DELIVERY_POLICY}}` | `no commit` / `commit only` / `commit and push` | index, adapters |
| `{{REPORTING_LEVEL}}` | `plain` or `technical` | index, adapters |
| `{{REFERENCE_BOUNDARY}}` | Reference boundary block in reference-assisted mode; empty otherwise | index |
| `{{PROJECT_OPERATING_CONSTRAINTS}}` | Inherited project rules | index |
| `{{ARCHITECTURE_DECISIONS}}` | Empty-table marker at initialization | index |
| `{{INDEX_FILE}}` | Relative path from the adapter to the index | lead adapter only — the worker adapter never reads the index |
| `{{MODULE_LINKS}}` / `{{MODULE_SUMMARIES}}` | Generated module links and routing summaries | index |
| `{{MODULE_TITLE}}` | Module name | each module doc |

Runtime tokens (leave intact — the lead adapter fills them per change):

| Token | Value |
|---|---|
| `{{DATE}}` | The change date in ISO 8601 `YYYY-MM-DD` (zero-padded, local date); the same string also names the day's completed folder and `summary.md` |
| `{{SLUG}}` | The per-change plan slug |

## Index Requirements

The index is the navigation map only — it holds no process and no internal
decision metadata. It carries map tiers 1 and 2 (see Map Tiers). There is no
length limit; write every module the project has, and route each one properly.
It must include:

- A one-line statement of what the project does and how daily work enters
  (through the lead adapter, which reads the index and carries its own
  discipline; the implementation agent enters through a task package instead).
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
decide whether to start there, and work confidently once it has. There is no line
budget — do not trim a finished doc to a target length.

Write **Do Not Do** and **Known Risks** so they can be pasted verbatim into a
task package's `Must Preserve` and `Forbidden` sections.

## Agent Roles And Write Ownership

Full doctrine in `references/delegation.md`. The parts every generated adapter
must enforce:

- **Lead** — the only agent in direct contact with a human. Owns understanding
  the need, the solution boundary, the Decision Gate, the Before/After gate, the
  task package, review of what comes back, final acceptance, delivery, and every
  write to a governance file. It does not implement, and it does not spawn the
  worker — it writes the package to a file and the human carries it across.
- **Worker** — a strong implementation agent, run by the human against one task
  package. Owns exploration, design inside the package's boundary, the change
  across whatever files it needs, its own tests and build, and one evidenced
  report.

**Role resolution.** Do not sniff the environment. An explicit `ROLE: worker`
header in the invoking prompt wins; with no header, assume lead. Backstop that
with a **governance write gate**: before writing any
atlas doc, anything under `docs/changes/`, or an Architecture Decisions row, the
agent asks whether its instructions came from a human turn or from a task
package — and if from a package, does not write, but reports the needed change
upward.

**Single writer.** Exactly one agent writes any governance file: the lead.

**Governance files** (lead-only, always): `docs/*_index.md`,
`docs/<project>/*.md`, everything under `docs/changes/`, and the Architecture
Decisions table.

**Working tree.** Only one agent is active on the tree at a time. Whoever holds
it owns it: while implementing, the worker runs whatever build, suite, server, or
migration its task needs. Encode no shared-resource negotiation and no
`deferred-to-lead`.

## Lead Adapter Requirements (carries the discipline)

The lead adapter is the entrypoint for the agent talking to a human. It specifies
and reviews; it does not implement and it does not dispatch. It must:

- **State the non-implementing role** up front, as a hard rule with no size
  exemption: the lead's output is a task package the human carries to an
  implementation agent, never code. It does not edit source or tests — not a
  typo, not a one-line constant. It may read code, run read-only checks, and
  re-run a verification that decides acceptance; when one fails, that is a gap to
  return, not something to fix. The adapter must contain no escape-hatch clause.
- **Role check** first: hand off to the worker adapter if invoked with a
  `ROLE: worker` package header, and state the governance write gate.
- **Entry / router**: preserve the request; read the index once; confirm in one
  plain sentence what the project does; pick only the relevant module doc(s)
  (zoom out to the module map first when unfamiliar); route by intent
  (know → investigate, change → change, mixed → investigate first); pass
  conclusions forward without rereading the index across steps.
- **Investigate (read-only)**: answer from the atlas plus the minimum code;
  separate facts from assumptions and unknowns; never edit; hand off to change
  after the user agrees. Carry one-line discipline pointers (debugging, review,
  design questions) instead of referencing external docs.
- **Change (any edit)**: judge a discipline tier. The tier scales how much
  specification the change needs:
  - **T0 trivial** (no logic change, reversible, single file): one-line
    Before/After; a minimal package — goal, the exact edit, one acceptance check;
    no Decision Gate.
  - **T1 normal** (contained, reversible, clear diagnosis): full package, naming
    the test that must exist afterwards.
  - **T2 hard/risky** (async/stateful, multi-module, external API, irreversible,
    perf regression, uncertain diagnosis): full package, a Decision Gate first,
    and explicit evidence requirements covering the risky behaviour rather than a
    green suite alone.

  Hard floor: irreversible, cross-module, external-API, and migration work is at
  least T2. A plain "be quick / be thorough" override is honoured but never drops
  below the floor.
- **Atlas update check** before completion: explicitly answer whether the change
  altered a module's boundary, ownership, or an external API/contract. If yes,
  update the affected atlas doc(s) now, as part of this same completion step —
  not a follow-up.
- **Before / After gate** as the only confirmation interface, and lead-only — it
  happens between the lead and the human, never agent-to-agent: Before states the
  current state and why the change is needed (the diagnosed root cause for a
  bug); After states what becomes true and how it will be verified. At T1/T2,
  wait for explicit confirmation before writing the package. At T0, state the
  one-line Before/After and proceed.
- **Decision Gate** when a change alters module boundaries, an external API
  contract, is irreversible or a migration, or has two or more viable approaches:
  present Context / Options (with trade-offs) / Recommendation and wait for a
  choice before the Before/After. For deep or unclear decision trees, interview
  one question at a time, each with a recommended answer, before presenting
  options.

  Once confirmed, a decision is settled: it goes into the package's
  `Solution Boundary`, and the worker may not re-open it.
- **Write the task package** after the Before/After is confirmed, to
  `docs/changes/planning/{{DATE}}-{{SLUG}}.md` — the plan file and the handoff
  artifact are the same file. Use the `atlas/v2` shape in
  `references/delegation.md` §4, embedded inline in the lead adapter so the lead
  needs no extra file read. Never chat history, never the index, never a spec
  dump. `Must Preserve` and `Forbidden` are normally copied from the owning
  module doc's **Do Not Do** and **Known Risks**. Then tell the user the package
  is ready and where it is; do not spawn anything.
- **State the acceptance rule**: every acceptance item must be checkable by
  someone who was not in the conversation — an exact command with an expected
  result, or an observable behaviour. "Works correctly" is not an acceptance
  criterion.
- **Command portability**, inline: write `Acceptance` and evidence commands for
  the shell the worker will actually get — one command per line, no `&&` chain,
  and on Windows no inline env prefixes, no `2>/dev/null`, no POSIX utilities
  assumed on `PATH`. Prefer the project's own runner.
- **Idle rule**, inline and explicit: while the package is out, do nothing at all
  — no `git status`, no diff inspection, no progress narration, no speculative
  reading. `references/delegation.md` §8 is never loaded at runtime, so the
  adapter must carry this itself.
- **Review** what the human brings back, in order: requirement conformance
  (against pasted evidence, re-running anything whose result decides acceptance —
  a claim of a passing check is not a passing check); architecture against the
  atlas's module boundaries and `Must Preserve`; the diff for `Scope` containment
  and the forbidden-pattern catalogue (`references/delegation.md` §5); and the
  tests, for whether they assert real behaviour and would fail if the bug
  returned. State that everything found at this step is a gap, including a check
  that fails on re-run, and that the lead does not fix it.
- **Return gaps, and only gaps**: a numbered list of what is wrong and what fixed
  looks like, ending with the required line "everything else is accepted, change
  nothing outside these points". Cap it at two returns; on a third, withdraw the
  package and reissue it.
- **Verification and completion**: the verification result is in the user-facing
  report regardless of reporting level; never claim completion on a failed check.
  On completion move the package to
  `docs/changes/completed/{{DATE}}/{{SLUG}}.md` and append its entry to that day's
  `docs/changes/completed/{{DATE}}/summary.md`, noting the atlas update check's
  outcome (see Plan File Lifecycle).
- **Reporting & delivery**: honour the reporting level (plain: no module names,
  paths, or code; technical: include them) and record the delivery policy. Carry
  conclusions forward across steps rather than re-reading the index at review
  time.
- Do not rerun Codebase Atlas unless the user explicitly asks; when they do,
  distinguish a refresh from a rebuild before spending either.

## Decision Recording (Lead-Only)

Where a settled decision goes. A worker writes none of these; it reports the
needed record upward and the lead writes it.

- Cross-module decisions: add a row to the Architecture Decisions table in the
  index (title, chosen option, affected modules, rationale).
- Module-level decisions: add a note to the affected module's Known Risks or Do
  Not Do section, referencing the index entry if cross-module.
- Do not create separate decision log files.

## Worker Adapter Requirements

The worker adapter is the entrypoint for the implementation agent the human hands
a task package to. It must:

- **Scope itself** to prompts carrying a `ROLE: worker` package header, and point
  anything else at the lead adapter.
- **Order the work**: read the package; treat `Goal` / `Why` / `Solution
  Boundary` as settled; explore whatever the change requires, with
  `Starting Points` as orientation rather than a reading cap; run the root-cause
  preflight; design and implement across the files the change needs, inside
  `Scope`; add and run the tests; run the build and suite; fix failures until
  they pass; check the result against `Goal` and `Acceptance` directly; report;
  stop.
- **State that the worker owns verification**: it runs its own build, suite,
  linter, and type check, and fixes what fails rather than handing it back. State
  also that a green suite does not substitute for checking the change against
  `Goal` and `Acceptance` directly.
- **State the prohibitions explicitly**: no plan/summary/dated folder/completion
  doc or anything else under `docs/changes/`, no atlas or Architecture Decisions
  edit, no Before/After to a human, no re-opening a settled decision, no
  self-widened scope, and no commit or push.
- **Carry the forbidden-pattern catalogue** from `references/delegation.md` §5
  inline, plus the package's own `Forbidden` additions.
- **Prefer stopping over guessing**: define the stop-and-report conditions —
  root cause outside `Scope`, a fix requiring a `Must Preserve` change, two
  materially different approaches, or a package premise the code contradicts —
  and state that an early return with a clear blocker is a success.
- **Handle a returned `## Gaps` list**: fix exactly the named points and nothing
  else.
- **Fix the report format** (`references/delegation.md` §6): changed files,
  approach, root cause, verification with **pasted output rather than a claim**,
  risks, needs-a-decision. No exploration narrative, no restating the diff.
- Record the reporting level, and that delivery is the lead's.

The worker adapter must not contain: the index path, the module list, the tier
model, planning, the Before/After gate, the Decision Gate, or the plan
lifecycle. If a worker needs any of that, the package was written wrong.

## Plan File Lifecycle

**The plan file and the task package are the same file.** There is no separate
spec to keep in sync.

Every tier writes one. What differs is what happens to it afterwards: T0's is
deleted on completion, T1 and T2 are archived with a summary line.

**Lead-only.** Everything under `docs/changes/` is a governance file. A worker
never creates a plan, a dated folder, a completion doc, or a summary line —
including the package it was handed.

**Date format.** Every `{{DATE}}` is ISO 8601 `YYYY-MM-DD` — zero-padded, local
date (for example `2026-06-09`, never `2026-6-9` or `06/09/2026`). The same date
string names the package file, the day's completed folder, and that day's summary
file, so they always match.

**Layout.**

```text
docs/changes/
  planning/
    {{DATE}}-{{SLUG}}.md       # the task package, written before handoff
  completed/
    {{DATE}}/                  # one folder per calendar day
      {{SLUG}}.md              # the finished package, moved here on completion
      summary.md               # that day's work summary, appended per change
```

**Lifecycle.**

1. After the Before/After is confirmed, write the package to
   `planning/{{DATE}}-{{SLUG}}.md`, then tell the user it is ready and where it
   is. Append each review `## Gaps` list to the same file.
2. On completion at T1/T2, move it to `completed/{{DATE}}/{{SLUG}}.md` (create the
   date folder if missing). No copy is left behind in `planning/`. At T0, delete
   it instead.
3. At T1/T2, in the same step, append one line for the change to
   `completed/{{DATE}}/summary.md` (create it if missing), newest last:

   ```text
   - {{SLUG}} — <one-line what changed> · T<tier> · <verification result> · <delivery> · atlas: <updated <module(s)> / no change needed>
   ```

   This file accumulates every completed change for that date.

Packages and summaries may name modules and files regardless of reporting level;
the reporting level governs only user-facing chat reports. Their delivery
(commit/push) follows the same delivery policy as the rest of the change.

## Incremental Atlas Updates

During ordinary work, atlas updates are incremental:

1. Update only the affected module doc or docs.
2. If the module list or module summaries in the index changed, update the index.
3. Do not rescan unrelated modules.
4. Note what changed and why in the report.

This applies when the lead's own completed change invalidated a doc. When the map
has drifted from work the lead did not do, run a Refresh instead.

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
past what its doc claims, or a boundary moved. The lead resolves this centrally
and confirms it with the user; never let a scanning subagent infer it.

**Escalate to a full rebuild** — after saying why and getting agreement — when
there is no usable provenance, when more than roughly half the modules come back
stale, or when the drift is in the boundaries themselves rather than inside them.

**What a refresh never touches:** the Architecture Decisions table, anything
under `docs/changes/`, and the adapters — unless the index's recorded format
version is behind the current one, or the user changed a decision this run.

**Provenance is rewritten last**, to the current date and `HEAD`, and only after
verification passes.

## Entrypoint Adapters

Every initialization or rebuild generates **a pair** of adapters — one lead, one
worker — for each confirmed platform. Never generate a lead adapter without its
worker.

### Platform Adapters (when selected)

| Platform | Lead path | Worker path |
|---|---|---|
| Claude Code | `.claude/skills/<project-slug>-atlas/SKILL.md` | `.claude/skills/<project-slug>-worker/SKILL.md` |
| Codex | `.agents/skills/<project-slug>-atlas/SKILL.md` | `.agents/skills/<project-slug>-worker/SKILL.md` |

Both platforms use the same bodies: `assets/templates/lead_adapter.md` and
`assets/templates/worker_adapter.md`. Only the destination directory differs.
Create the directories at the project root if they do not exist.

**Frontmatter required** (render `description` in the Step 0 working language;
English shown here):

- Lead — `name: <project-slug>-atlas`, `description`: `Codebase Atlas for
  <PROJECT_NAME> — navigation map, change discipline, and task-package authoring,
  for the agent talking directly to a human. Load once at the start of work on
  this project; do not re-invoke later in the same conversation. An agent
  executing an atlas task package must not load this — it uses
  <project-slug>-worker instead.`
- Worker — `name: <project-slug>-worker`, `description`: `Execution rules for an
  agent implementing an atlas task package on <PROJECT_NAME>. Load ONLY when your
  instructions arrived as a task package — a prompt whose header says ROLE:
  worker. Never load it when working directly with a human; that is
  <project-slug>-atlas.`

The two adapters commonly run on different platforms — the lead where the human
works, the worker wherever the implementation agent runs. Generate the pair for
every selected platform regardless.

Each description must name the sibling skill.

Set `{{PROJECT_NAME}}`, `{{PROJECT_SLUG}}`, `{{DELIVERY_POLICY}}`, and
`{{REPORTING_LEVEL}}` in both. Set `{{INDEX_FILE}}` in the lead adapter only, to
the relative path from its directory to the index (e.g.
`../../../docs/<project>_index.md`) — the worker adapter never reads the index.

### Generic Adapters (only when no platform adapter exists)

- **Paths:** `docs/<project>_lead_adapter.md` and
  `docs/<project>_worker_adapter.md`
- **Templates:** the same two, with the frontmatter block dropped. They work as
  plain reference docs.
- Generate these only when Step 3's platform confirmation produced no
  platform-specific adapter — the user chose "None — skip adapter generation,"
  or platform detection was inconclusive and the user picked no platform. When
  at least one platform adapter pair exists, skip them. Generate both forms only
  if the user explicitly asks for a plain-markdown entrypoint alongside a
  platform adapter.
- **Cleanup:** on any initialization or rebuild, if generic adapter files exist
  from a prior run — including the pre-split single `docs/<project>_adapter.md`
  — and at least one platform adapter exists or is being generated this run,
  delete them. Do this as part of adapter generation, not as a follow-up task.

### Do Not Force-Load The Skill

Do not write a "run the atlas skill before every operation" mandate into
`CLAUDE.md`, `AGENTS.md`, or any always-on config. At most, add a single
plain-language pointer line noting that the navigation map lives at
`docs/<project>_index.md`, and only if that file does not already say so.

### Both Adapters Must

- Be self-contained for their role, per the Lead and Worker Adapter Requirements
  above. Do not point to separate workflow docs, and do not point at each other
  for content — only for role handoff.
- Open with the role check.
- Include the reporting level, and the delivery policy or the fact that delivery
  is the lead's.
- Be included in delete-and-rebuild detection during Step 1 of a rebuild.

## Delivery

Apply the resolved `delivery_policy` once the atlas has been generated,
adapter cleanup (above) is done, and verification (`references/quality-checklist.md`)
has passed:

- `no commit`: stop. Leave the working tree for the user to review and commit
  themselves.
- `commit only`: stage exactly the files this run created, modified, or
  deleted (index, module docs, adapters, any generic-adapter deletion, and a
  `CLAUDE.md` pointer line if added) and commit with a message describing the
  atlas change. Do not stage unrelated pending changes and do not push.
- `commit and push`: do the same commit, then push. If the push is rejected
  because the remote has commits this run does not have, stop and ask the
  user how to reconcile (merge or rebase) rather than force-pushing. Never
  force-push atlas commits.
