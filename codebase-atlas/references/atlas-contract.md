# Atlas Contract

Use this contract for every Codebase Atlas initialization or rebuild.

The atlas is a compact engineering map, not a full architecture book. Keep
generated docs concise, navigable, and grounded in repository-persistent facts.
The design goal is low daily context: a routine task should load only the
entrypoint skill for its role (lazily, on invocation) plus the index and one or
two module docs — never a chain of process files.

The atlas targets a lead-plus-workers setup, not a single long-context agent.
Two entrypoints are generated, split by **role**, not by activity: a lead
adapter for the agent talking to the human, and a worker adapter for delegated
subagents. `references/delegation.md` carries the doctrine behind that split —
read it before generating either adapter.

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

The map is layered so that no agent loads more of it than its task needs:

| Tier | Where | Who loads it | Budget |
|---|---|---|---|
| 1 — project overview | top of the index | any agent, once | ≤ 15 lines |
| 2 — module routing | index module list + summaries | the lead, once | ≤ 6 lines per module |
| 3 — module detail | `docs/<project>/<module_slug>.md` | whoever works in that module | ≤ 120 lines |
| 4 — live search | grep, symbol search, call hierarchy | whoever needs an exact location | — |

Tiers 1-2 must fit in one short read: an index over roughly 150 lines has
started absorbing module detail that belongs in tier 3. Workers are given tier-3
paths directly in their task contract and never read tiers 1-2 — the contract
already carries what they would have learned there.

The map answers *what owns this, where do I start, what must I not break*.
Search answers *where exactly is it*. Do not push search-answerable detail (call
sites, symbol lists, file inventories) into the map; it goes stale fastest and
costs the most.

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

## Required Templates

Use the templates under `assets/templates/`:

- `index.md`
- `module.md`
- `lead_adapter.md` — the lead entrypoint, for the agent in contact with a human
- `worker_adapter.md` — the worker entrypoint, for delegated subagents

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

## Optional Templates

These are not part of the required output shape and are generated only when the
project warrants them and the user opts in. They never expand the required
`index + module docs + adapter pair` shape.

- `design.md` — a generic, **format-only** scaffold for mapping a project's design
  system in the google-labs-code/design.md two-layer format (YAML token
  front-matter + prose rationale, canonical section order). Format-only: it never
  requires installing or running `@google/design.md` (its CLI / lint / export), so
  it suits no-build, supply-chain-restricted environments. Normativity follows the
  project's declared source of truth (mirror when code/CSS/tokens are canonical;
  normative only when the file is declared canonical). Record the mapped design
  system as a normal module doc and/or an index link; do not hardcode
  project-specific layering (e.g. a per-page override system) into the skill. See
  `references/modes.md` → "Optional: Design System Mapping".

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
decision metadata. It carries map tiers 1 and 2 (see Map Tiers) and should stay
under roughly 150 lines; past that, detail has leaked in from tier 3. It must
include:

- A one-line statement of what the project does and how daily work enters
  (through the lead adapter, which reads the index and carries its own
  discipline; workers enter through a task contract instead).
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
decide whether to start there. Keep it under roughly 120 lines — it is tier 3,
loaded by whoever works in this module, and paid for on every delegation that
names it.

Write **Do Not Do** and **Known Risks** so they can be pasted verbatim into a
task contract's `Must Preserve` and `Forbidden` sections. That is their main
consumer in a multi-agent workflow, and it makes each delegation nearly free to
constrain properly.

## Agent Roles And Write Ownership

Full doctrine in `references/delegation.md`. The parts every generated adapter
must enforce:

- **Lead** — the only agent in direct contact with a human. Owns the
  Before/After gate, decisions, delegation, every whole-project build and test
  run, acceptance, and every write to a governance file.
- **Worker** — a delegated subagent. Owns exactly one task contract: search,
  edit, contract-permitted checks, one structured report.

**Role resolution.** Do not sniff the environment; neither platform exposes a
reliable signal. An explicit `ROLE: worker` header in the invoking prompt wins;
with no header, assume lead, so the human-alignment gate is never silently
skipped. Backstop that with a **governance write gate**: before writing any
atlas doc, anything under `docs/changes/`, or an Architecture Decisions row, the
agent asks whether its instructions came from a human or from another agent's
task description — and if from another agent, does not write, but reports the
needed change upward.

**Single writer.** Exactly one agent writes any governance file: the lead.

**Governance files** (lead-only, always): `docs/*_index.md`,
`docs/<project>/*.md`, everything under `docs/changes/`, and the Architecture
Decisions table.

**Shared resources** (lead-only, and only with zero workers in flight):
whole-project builds, the full test suite, dev servers and anything binding a
port, databases and migrations, dependency installs, process restarts. A worker
that can only verify through a shared resource reports
`verification: deferred-to-lead` rather than producing an unreliable result.

## Lead Adapter Requirements (carries the discipline)

The lead adapter is the entrypoint for the agent talking to a human. It replaces
the old single adapter plus two workflow docs. It must:

- **Role check** first: hand off to the worker adapter if invoked with a
  `ROLE: worker` contract header, and state the governance write gate.
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
- **Atlas update check** before completion: explicitly answer whether the change
  altered a module's boundary, ownership, or an external API/contract. If yes,
  update the affected atlas doc(s) now, as part of this same completion step —
  not a follow-up.
- **Before / After gate** as the only confirmation interface, and lead-only — it
  happens between the lead and the human, never agent-to-agent: Before states the
  current state and why the change is needed (the diagnosed root cause for a
  bug); After states what becomes true and how it will be verified. At T1/T2,
  wait for explicit confirmation before editing any file *or dispatching any
  worker*. At T0 (trivial, reversible, single file), state the one-line
  Before/After and proceed without waiting, then report after.
- **Decision Gate** when a change alters module boundaries, an external API
  contract, is irreversible or a migration, or has two or more viable approaches:
  present Context / Options (with trade-offs) / Recommendation and wait for a
  choice before the Before/After. For deep or unclear decision trees, interview
  one question at a time, each with a recommended answer, before presenting
  options.

  Once confirmed, a decision is settled: it is condensed into any worker
  contract, and a worker may not re-open it.
- **Delegate**, after the Before/After is confirmed, by sending a task contract
  (the `atlas/v1` shape in `references/delegation.md` §3) — never chat history,
  never the index, never a spec dump. The contract's `Must Preserve` and
  `Forbidden` sections are normally copied from the owning module doc's **Do Not
  Do** and **Known Risks**. Embed the contract template inline in the lead adapter so
  the lead needs no extra file read.
- **Schedule** dispatches so that concurrent workers hold disjoint
  `Allowed Paths`; on overlap, serialize or re-cut the task; when in doubt,
  serial. A task needing full-build feedback to iterate runs solo or stays with
  the lead. Shared resources stay lead-only per Agent Roles above.
- **Accept** worker output against the contract: every acceptance item holds, the
  diff stayed inside `Allowed Paths`, nothing under `Must Preserve` moved, the
  fix addresses the root cause, and none of the forbidden patterns
  (`references/delegation.md` §5) appear. Then run the authoritative build and
  suite plus anything marked `deferred-to-lead`. A separate review subagent is
  spent only at T2, or when the lead wrote the code itself — dispatched as the
  same contract with `TASK_TYPE: review`, on the stronger model.
- **Verification** scaled to the tier after edits; the verification result is in
  the user-facing report regardless of reporting level; never claim completion on
  a failed check. On completion move the plan to
  `docs/changes/completed/{{DATE}}/{{SLUG}}.md` and append its entry to that day's
  `docs/changes/completed/{{DATE}}/summary.md`, noting the atlas update check's
  outcome (see Plan File Lifecycle).
- **Reporting & delivery**: honour the reporting level (plain: no module names,
  paths, or code; technical: include them) and record the delivery policy. While
  workers are running, show the user the task list and status, not worker
  intermediate output; on a worker failure, report in one or two plain sentences
  what failed and what happens next.
- Do not rerun Codebase Atlas initialization unless the user explicitly asks for a
  full rebuild.

## Worker Adapter Requirements

The worker adapter is the entrypoint for a delegated subagent. It is short by
design — a worker that reads more than it needs has already lost the saving that
delegation exists for. It must:

- **Scope itself** to prompts carrying a `ROLE: worker` contract header, and
  point anything else at the lead adapter.
- **Order the work**: read the contract; read only the files under `Read First`;
  locate exact code by search rather than by browsing the map; run the root-cause
  preflight; edit inside `Allowed Paths`; run only permitted checks; report; stop.
- **State the prohibitions explicitly**, because a cheap model needs them
  concrete: no plan/summary/dated folder/completion doc, no atlas or Architecture
  Decisions edit, no Before/After to a human, no re-opening settled decisions, no
  self-widened scope, and no shared-resource command (whole-project build, full
  suite, dev server, port binding, database, migration, dependency install,
  process kill) — report `verification: deferred-to-lead` instead.
- **Carry the forbidden-pattern catalogue** from `references/delegation.md` §5
  inline, plus the contract's own `Forbidden` additions.
- **Prefer stopping over guessing**: define the stop-and-report conditions and
  state that an early return with a clear blocker is a success.
- **Fix the report format** (`references/delegation.md` §6): changed files, root
  cause, verification, risks/blockers, needs-a-decision. No exploration
  narrative, no restating the diff.
- Record the reporting level, and that delivery is the lead's.

The worker adapter must not contain: the index path, the module list, the tier
model, planning, the Before/After gate, the Decision Gate, or the plan
lifecycle. If a worker needs any of that, the contract was written wrong.

### Decision recording

- Cross-module decisions: add a row to the Architecture Decisions table in the
  index (title, chosen option, affected modules, rationale).
- Module-level decisions: add a note to the affected module's Known Risks or Do
  Not Do section, referencing the index entry if cross-module.
- Do not create separate decision log files.

## Plan File Lifecycle

Change-tier work records plans and a daily summary under `docs/changes/`. T0
trivial changes skip all of this; T1 and T2 follow it.

**Lead-only.** Everything under `docs/changes/` is a governance file. A worker
never creates a plan, a dated folder, a completion doc, or a summary line, no
matter how large its task was. One task produces one plan written by the lead,
however many workers it took to carry out.

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
   - {{SLUG}} — <one-line what changed> · T<tier> · <verification result> · <delivery> · atlas: <updated <module(s)> / no change needed>
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

Every initialization or rebuild generates **a pair** of adapters — one lead, one
worker — for each confirmed platform. Never generate a lead adapter without its
worker: a project with only a lead adapter is exactly the single-agent design
this contract replaced, and its subagents will load the lead adapter and start
managing the project.

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
  <PROJECT_NAME> — navigation map, change discipline, and delegation, for the
  agent talking directly to a human. Load once at the start of work on this
  project; do not re-invoke later in the same conversation. A delegated subagent
  must not load this — it uses <project-slug>-worker instead.`
- Worker — `name: <project-slug>-worker`, `description`: `Execution rules for a
  delegated subagent on <PROJECT_NAME>. Load ONLY when your instructions arrived
  as an atlas task contract — a prompt whose header says ROLE: worker. Never
  load it when working directly with a human; that is <project-slug>-atlas.`

The descriptions carry the role boundary because a description is the only part
of a skill an agent sees before deciding to load it. Each must name the sibling
skill so a mis-triggered load self-corrects on the first line.

Set `{{PROJECT_NAME}}`, `{{PROJECT_SLUG}}`, `{{DELIVERY_POLICY}}`, and
`{{REPORTING_LEVEL}}` in both. Set `{{INDEX_FILE}}` in the lead adapter only, to
the relative path from its directory to the index (e.g.
`../../../docs/<project>_index.md`).

### Generic Adapters (only when no platform adapter exists)

- **Paths:** `docs/<project>_lead_adapter.md` and
  `docs/<project>_worker_adapter.md`
- **Templates:** the same two, with the frontmatter block dropped. They work as
  plain reference docs.
- Generate these only when Step 3's platform confirmation produced no
  platform-specific adapter — the user chose "None — skip adapter generation,"
  or platform detection was inconclusive and the user picked no platform. When
  at least one platform adapter pair exists, that platform loads its own
  adapters automatically; the generic `docs/` copies would then be duplicates
  that nothing loads and no workflow keeps in sync, so skip them. Generate both
  forms only if the user explicitly says they also need a plain-markdown
  entrypoint alongside a platform adapter (e.g. for a tool without skill
  support).
- **Cleanup:** on any initialization or rebuild, if generic adapter files exist
  from a prior run — including the pre-split single `docs/<project>_adapter.md`
  — and at least one platform adapter exists or is being generated this run,
  delete them. Do this as part of adapter generation, not as a follow-up task.

### Do Not Force-Load The Skill

Do not write a "run the atlas skill before every operation" mandate into
`CLAUDE.md`, `AGENTS.md`, or any always-on config. Each skill's `description`
lets an agent discover it when a task actually needs it. At most, add a single
plain-language pointer line noting that the navigation map lives at
`docs/<project>_index.md`, and only if that file does not already say so.

### Both Adapters Must

- Be self-contained for their role, per the Lead and Worker Adapter Requirements
  above. Do not point to separate workflow docs, and do not point at each other
  for content — only for role handoff.
- Open with the role check, so a mis-triggered load costs one line instead of a
  polluted repository.
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
