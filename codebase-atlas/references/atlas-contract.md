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

The atlas targets a **human-mediated three-tier** setup. Three entrypoints are
generated, split by **role**:

| Tier | Adapter | Model | Owns |
|---|---|---|---|
| Planning & review | `<slug>-atlas` | strongest available | alignment, diagnosis, decomposition, packages, dispatch plan, atlas writes |
| Execution management | `<slug>-relay` | GPT-5.6-Luna, reasoning Max | ordering, dispatch, waiting, acceptance, completion records, commits |
| Implementation | `<slug>-worker` | GPT-5.6-Luna, reasoning Max | one task package, end to end |

The lead never spawns anything — it writes files and the human carries **one** of
them, the dispatch plan, across to the relay lead. Everything after that crossing
is agent-to-agent, because the human is not expected to come back. Read
`references/delegation.md` before generating any adapter.

## Atlas Format Version

**Current atlas format: `4`.** Format 4 is the human-mediated three-tier split:
the lead specifies and reviews but never implements or dispatches; a relay lead
receives one dispatch plan, orders the batch, dispatches implementation agents,
accepts their work by re-running checks, and records completion; the worker is a
strong agent that explores, designs across files, and owns its own tests and
build. Format 3 was the same human-mediated split without the relay tier, which
left archival and acceptance stranded whenever the human did not return. Format 2
was the lead-dispatches-cheap-subagents split. Format 1 was the single
self-contained adapter with separate workflow docs.

Every generated index records the format it was built to. An index recording a
format below the current one has adapters built to a workflow that no longer
applies: regenerate the full adapter set — a refresh of the map alone will not
fix it.

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
  the Step 3 confirmation. Each confirmed platform gets all three adapters —
  lead, relay, worker. The generic `docs/` adapters are generated only when no
  platform-native adapter exists — see Entrypoint Adapters → Generic Adapters.

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
  <project>_relay_adapter.md    # Entrypoint Adapters → Generic Adapters
  <project>_worker_adapter.md
```

Reference-assisted output:

```text
docs/
  <project>_<reference>_index.md
  <project>_<reference>/
    <module_slug>.md
  <project>_<reference>_lead_adapter.md     # only when no platform adapter exists
  <project>_<reference>_relay_adapter.md
  <project>_<reference>_worker_adapter.md
```

There are no separate workflow docs — change/investigate discipline lives inside
the lead adapter, ordering and acceptance inside the relay adapter, and
implementation discipline inside the worker adapter.

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
| `{{PROJECT_SLUG}}` | kebab-case project slug; the lead skill is `<slug>-atlas`, the relay skill `<slug>-relay`, the worker skill `<slug>-worker` | platform adapters only |
| `{{WORKING_LANGUAGE}}` | Selected working language | index |
| `{{BUILD_DATE}}` | ISO `YYYY-MM-DD` on which this atlas was built or last refreshed | index |
| `{{BUILD_COMMIT}}` | Short SHA of `HEAD` at build time; `not-a-git-repo` when the project is not under git | index |
| `{{ATLAS_FORMAT}}` | The atlas format version generated — see Atlas Format Version | index |
| `{{DELIVERY_POLICY}}` | `no commit` / `commit only` / `commit and push` | index, adapters |
| `{{REPORTING_LEVEL}}` | `plain` or `technical` | index, adapters |
| `{{REFERENCE_BOUNDARY}}` | Reference boundary block in reference-assisted mode; empty otherwise | index |
| `{{PROJECT_OPERATING_CONSTRAINTS}}` | Inherited project rules | index |
| `{{ARCHITECTURE_DECISIONS}}` | Empty-table marker at initialization | index |
| `{{INDEX_FILE}}` | Relative path from the adapter to the index | lead adapter only — neither the relay nor the worker adapter reads the index |

There is no model-tier token. The execution tiers are fixed: the relay lead and
every worker it dispatches run on **GPT-5.6-Luna, reasoning Max**, written
literally into the relay and worker adapters and into the package and
dispatch-plan headers. A user running a different execution model edits the
adapters; the skill does not abstract this into a tier system.
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
  discipline; the relay lead enters through a dispatch plan and an implementation
  agent through a task package — neither reads the index).
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

Write **Do Not Do** and **Known Risks** as repository-specific facts, invariants,
and hidden constraints. A lead may copy only the items relevant to a task into
its `Constraints` section; do not treat these sections as a catalogue of generic
engineering rules.

## Agent Roles And Write Ownership

Full doctrine in `references/delegation.md`. The parts every generated adapter
must enforce:

- **Lead** — the only agent in direct contact with a human. Owns understanding
  the need, choices the repository cannot settle, the Decision Gate, the
  Before/After gate, diagnosis, decomposition, every task package and the dispatch
  plan, atlas writes, and a second-pass review of whatever the human brings back.
  It does not implement and it does not dispatch — it writes files, commits and
  pushes them, and the human carries the dispatch plan across.
- **Relay lead** — the execution manager, started by the human with the dispatch
  plan. Owns ordering within the plan's dependencies, the real parallelism
  decision, dispatch, waiting, acceptance by re-running the decisive checks,
  completion records, the completed folder, the daily summary, and the commit and
  push.
- **Worker** — a strong implementation agent, dispatched against one task package.
  Owns exploration, implementation decisions, the change across whatever files it
  needs, the checks needed to prove acceptance, and one evidenced report.

**Role resolution.** Do not sniff the environment. Resolve from the prompt
header: `ROLE: worker` → worker; `ROLE: relay-lead` → relay lead; no header →
lead. Backstop that with a **governance write gate**: before writing any
governance file, the agent asks whether that file belongs to its own tier, and if
not, reports the needed change instead of writing it.

**Governance ownership**, split by tier:

| File | Written by | Committed and pushed by |
|---|---|---|
| `docs/*_index.md`, `docs/<project>/*.md` | Lead | Lead |
| Architecture Decisions rows | Lead | Lead |
| `docs/changes/planning/**` | Lead | Lead, before handover |
| `Completion record` inside a package | Relay lead | Relay lead |
| `docs/changes/completed/**` | Relay lead | Relay lead |
| Source and tests | Worker (working tree only) | Relay lead |

Both tiers push. The execution tier reads the packages out of the repository, so
unpushed planning files may not be there when it looks.

**Working tree.** One agent implements on the tree at a time. Whoever holds it
owns it: while implementing, the worker runs whatever build, suite, server, or
migration its task needs. Encode no shared-resource negotiation and no
`deferred-to-lead`. Where two packages would contend, the relay lead serializes
them rather than fencing either.

## Lead Adapter Requirements (carries the discipline)

The lead adapter is the entrypoint for the agent talking to a human. It specifies
and reviews; it does not implement and it does not dispatch. It must:

- **State the non-implementing role** up front, as a hard rule with no size
  exemption: the lead's output is a task package the human carries to an
  implementation agent, never code. It does not edit source or tests — not a
  typo, not a one-line constant. It may read code, run read-only checks, and
  re-run a verification that decides acceptance; when one fails, that is a gap to
  return, not something to fix. The adapter must contain no escape-hatch clause.
- **Role check** first: hand off to `<slug>-worker` on a `ROLE: worker` header and
  to `<slug>-relay` on a `ROLE: relay-lead` header. State the governance write
  gate, and what is *not* the lead's to write: completion records,
  `docs/changes/completed/**`, implementation commits.
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
  - **T1 normal** (contained, reversible, clear diagnosis): full package with
    objective acceptance checks and any explicit constraints.
  - **T2 hard/risky** (async/stateful, multi-module, external API, irreversible,
    perf regression, uncertain diagnosis): full package, a Decision Gate only for
    choices the repository cannot settle, and acceptance evidence covering the
    risky behaviour.

  Hard floor: irreversible, cross-module, external-API, and migration work is at
  least T2. A plain "be quick / be thorough" override is honoured but never drops
  below the floor.

  **There is no trivial tier.** State explicitly that a typo, a constant, or a
  one-line config change does not enter this workflow at all and goes straight to
  an execution model — and that the lead neither invents a shortcut path nor edits
  it itself.
- **Atlas update** when a returned `Completion record` reports that the change
  altered a module's boundary, ownership, or an external API/contract: update the
  affected module doc, index entry, and Architecture Decisions row, and only
  those. State that this is the one governance step that survives the human not
  returning, so it happens whenever results come back, however late.
- **Before / After gate** as the only confirmation interface, and lead-only — it
  happens between the lead and the human, never agent-to-agent: Before states the
  current state and why the change is needed (the diagnosed root cause for a
  bug); After states what becomes true and how it will be verified. Wait for
  explicit confirmation before writing packages.
- **Decision Gate** when a change alters module boundaries, an external API
  contract, is irreversible or a migration, or has a product choice the code
  cannot settle: present Context / Options / Recommendation and wait for a choice
  before the Before/After. Do not use the gate to prescribe implementation. For
  deep or unclear decision trees, interview one question at a time, each with a
  recommended answer, before presenting options.

  Once confirmed, record the decision as an explicit `Constraints` item. The
  worker follows it while choosing the implementation.
- **Write the task packages** after the Before/After is confirmed, to
  `docs/changes/planning/{{DATE}}-{{SLUG}}.md` — the plan file and the handoff
  artifact are the same file. Use the `atlas/v3` shape in
  `references/delegation.md` §5, embedded inline in the lead adapter so the lead
  needs no extra file read. It carries the Goal, Background, objective Acceptance
  checks, explicit Constraints only when needed, optional Starting Points,
  Evidence, and an empty `Completion record` the relay lead fills in. Never chat
  history, never the index, never a spec dump, never a prescribed implementation.
- **Explain `Background` at length**: it is what makes a package portable to a
  model with zero conversation history, on another platform. No length limit;
  quote the wrong code; show real input against real wrong output; carry forward
  any inventory already done, marking entries that are "currently correct but only
  by luck"; state the known limits of the analysis.
- **Write the dispatch plan** to
  `docs/changes/planning/{{DATE}}-{{SLUG}}-dispatch-plan.md` (§4), required **even
  for a single package** — a package handed over alone carries a `ROLE: worker`
  header, so its receiver becomes a worker and the ordering tier disappears. It
  carries the objective, the package table, the hard execution order with reasons,
  permitted parallel groups, the batch-level shared verification, and the
  completion protocol.
- **Commit and push the packages and the dispatch plan before handover**, then
  tell the user which single file to hand over. Do not spawn anything.
- **State the acceptance rules**: every item checkable by someone who was not in
  the conversation — an exact command with an expected result, or an observable
  behaviour ("works correctly" is not one); exact expected values over existence
  claims; the negative case and what a negative fixture must contain; what must
  not change; a ban on passing by weakening a rule, threshold, detector, or
  assertion, with any drop in a previously passing count explained item by item;
  and skippable items for checks depending on something that may not exist on the
  execution machine.
- **State that `Starting Points` is a map, not a fence**: the worker explores and
  changes whatever the goal requires, including a full architectural correction.
  Scope is restricted only in `Constraints`, and when two packages would conflict
  they are scheduled serially rather than both fenced.
- **State the granularity rule**: cut along change boundaries, never by file.
- **Command portability**, inline: write `Acceptance` and evidence commands for
  the shell the worker will actually get — one command per line, no `&&` chain,
  and on Windows no inline env prefixes, no `2>/dev/null`, no POSIX utilities
  assumed on `PATH`. Prefer the project's own runner.
- **Idle rule**, inline and explicit: while the batch is out, do nothing at all —
  no `git status`, no diff inspection, no progress narration, no speculative
  reading. `references/delegation.md` §11 is never loaded at runtime, so the
  adapter must carry this itself. State that the user may never return to the
  conversation, and that this is expected rather than a failure.
- **Review as a second pass**, when and if the human brings results back — the
  relay lead already accepted each package and is the primary gate. Read in
  order: requirement conformance (against the `Completion record`, re-running
  anything whose result decides acceptance — a claim of a passing check is not a
  passing check); the diff against the Goal and explicit `Constraints`; and
  whether the completion records state limits and residual risk honestly. State
  that everything found is a gap, including a check that fails on re-run, and that
  the lead does not fix it — but that a wrong specification is the lead's to
  withdraw, fix, and reissue.
- **Return gaps, and only gaps**: a numbered list of what is wrong and what fixed
  looks like, ending with the required line "everything else is accepted, change
  nothing outside these points".
- **Verification reporting**: the verification result is in the user-facing report
  regardless of reporting level; never claim completion on a failed check. State
  that archival and the daily summary were already done by the relay lead and are
  not redone here.
- **Reporting & delivery**: honour the reporting level (plain: no module names,
  paths, or code; technical: include them) and record the delivery policy, noting
  that implementation commits are the relay lead's. Carry conclusions forward
  across steps rather than re-reading the index at review time.
- Do not rerun Codebase Atlas unless the user explicitly asks; when they do,
  distinguish a refresh from a rebuild before spending either.

The lead adapter must not contain: dispatch mechanics, waiting rules, or the
completion protocol's write steps. Those are the relay adapter's.

## Relay Adapter Requirements

The relay adapter is the entrypoint for the agent the human hands the dispatch
plan to. It never plans and never implements. It must:

- **Role check** first: `ROLE: relay-lead` or a dispatch plan → continue;
  `ROLE: worker` → `<slug>-worker`; a human conversation → `<slug>-atlas`.
- **Enter through the dispatch plan only**: read it in full, then read every
  package it names before dispatching anything.
- **Respect hard ordering, own real parallelism**: it may lower parallelism or
  serialize a group, never raise it or reorder a hard dependency.
- **Carry the serialization criteria**: overlapping edits, several large builds in
  one build directory, CPU/memory/disk exhaustion, or tests observing another
  agent's half-written files. "Dispatch one, accept it, dispatch the next" is a
  good default, and parallelism is never a goal in itself.
- **Name the dispatch parameters literally**:
  `{"model": "gpt-5.6-luna", "reasoning_effort": "max"}`, the field being
  `reasoning_effort` rather than `thinking`, never left to inheritance. Hand over
  the package and nothing else.
- **Wait with the platform's blocking wait, never a sleep** (`wait_agent` on
  Codex), because a completion event does not preempt a synchronous shell tool
  already running.
- **Fix the wait timeout at one hour** (`timeout_ms: 3600000` — milliseconds, and
  the per-call maximum).
- **State that a wait timeout is not a failure**: the subagent is still running;
  call the wait again. Never grounds for declaring failure or re-dispatching.
- **State how to wait on several subagents**: the wait returns on the *first* to
  reach a final status, not a join, so outstanding ids are tracked and re-waited
  until the list is empty.
- **State that staying alive is the wait loop's job**, and that the long-running
  work mode (`/goal` on Codex) belongs to the human — the relay lead never invokes
  it for itself, never applies it to a subagent, and works without it.
- **Wait passively**: while a subagent is in flight, leave the shared tree, the
  subagent, and the schedule alone — no `git status`, no diff inspection, no build
  or test, no progress query, no declaring failure from a closed window, and no
  re-dispatch of a task that may still be running. Permitted meanwhile: reading
  undispatched packages, planning the schedule, and dispatching the next package
  under the plan's permitted parallelism.
- **Accept by re-running**, never on text: a report is a claim, and the relay lead
  is biased toward believing work it dispatched. Re-run the decisive commands,
  read the diff against the goal, check nothing outside the goal broke, and check
  the stated risks against what the diff shows. A shortcut the report explains and
  justifies is fine; an unexplained one is the finding.
- **Return gaps** naming only the gaps, with the required closing line. At most
  two returns; on a third the specification is the suspect, and that is the lead's
  to fix.
- **Never repair a specification** — no rewriting a goal, lowering an acceptance
  item, or bending the spec to match the implementation. Record the problem, stop
  that package, continue with everything it does not block.
- **Follow the completion protocol in order** (see Plan File Lifecycle):
  completion record → move → summary → commit and push, code and records together.
- **Run the plan's `Shared Verification`** after the last package, then report the
  batch.
- Record the reporting level and the delivery policy.

The relay adapter must not contain: the index path, the module list, the tier
model, the Before/After gate, the Decision Gate, or package-authoring rules.

## Decision Recording (Lead-Only)

Where a settled decision goes. A worker writes none of these; it reports the
needed record upward and the lead writes it.

- Cross-module decisions: add a row to the Architecture Decisions table in the
  index (title, chosen option, affected modules, rationale).
- Module-level decisions: add a note to the affected module's Known Risks or Do
  Not Do section, referencing the index entry if cross-module.
- Do not create separate decision log files.

## Worker Adapter Requirements

The worker adapter is the entrypoint for the implementation agent dispatched
against one task package. It must:

- **Scope itself** to prompts carrying a `ROLE: worker` package header, and point
  anything else at `<slug>-atlas` (human conversation) or `<slug>-relay` (dispatch
  plan).
- **Order the work**: read the package; use `Starting Points` when present;
  explore whatever the change requires; run the root-cause preflight; decide and
  implement the solution across the files it needs; run the checks needed to
  establish `Acceptance`; fix relevant failures until acceptance passes or a
  concrete blocker remains; check the result against `Goal` and `Acceptance`
  directly; report; stop.
- **State that files are not fenced by default**: `Starting Points` says where to
  begin, not what may be touched. The worker follows real dependencies and makes
  an architectural correction when the goal needs one rather than a local patch.
  The only exception is an explicit `Constraints` restriction.
- **State that the worker owns verification**: it chooses and runs the relevant
  build, test, lint, or type checks — including a whole-project build and the full
  suite — and reports their actual output. A green suite does not substitute for
  checking the change against `Goal` and `Acceptance` directly.
- **State what belongs to other tiers**, as ownership rather than prohibition:
  records and delivery (`Completion record`, `docs/changes/**`, the commit) are
  the relay lead's; the atlas and Architecture Decisions are the lead's; the
  Before/After gate already happened; a settled decision stays settled, and a
  worker that disagrees says so in `Needs A Decision`. If an explicit `Constraint`
  conflicts with the code or cannot be met, report it instead of silently changing
  the requirement.
- **Carry the shortcut rule** (`references/delegation.md` §7) as **one principle
  plus its usual shapes** — do not substitute making the check pass for solving
  the problem; any of those shapes can be right, so do it deliberately and say why
  — never as a catalogue of absolute bans.
- **Handle a returned `## Gaps` list**: fix exactly the named points and nothing
  else.
- **Fix the report format** (`references/delegation.md` §8): changed files, root
  cause, verification with **pasted output rather than a claim**, risks, and any
  needed decision. No exploration narrative or restatement of the task.
- Record the reporting level, and that delivery belongs to the relay lead.

The worker adapter must not contain: the index path, the module list, the tier
model, planning, the Before/After gate, the Decision Gate, dispatch mechanics, the
plan lifecycle, or a generic implementation-style prohibition catalogue. If a
worker needs any of that, the package was written wrong.

## Plan File Lifecycle

**The plan file and the task package are the same file.** There is no separate
spec to keep in sync.

Both discipline tiers (T1 and T2) write one. On completion, every package is
archived with a summary line; no completed package is deleted.

**Split ownership.** Everything under `docs/changes/` is a governance file, but
the halves have different writers: the lead owns `planning/` (packages and
dispatch plans), the relay lead owns `completed/` plus the `Completion record`
section inside each package. A worker writes neither — not even the package it was
handed.

**Date format.** Every `{{DATE}}` is ISO 8601 `YYYY-MM-DD` — zero-padded, local
date (for example `2026-06-09`, never `2026-6-9` or `06/09/2026`). The same date
string names the package file, the day's completed folder, and that day's summary
file, so they always match.

**Layout.**

```text
docs/changes/
  planning/
    {{DATE}}-{{SLUG}}.md                    # a task package
    {{DATE}}-{{SLUG}}-dispatch-plan.md      # the single file handed over
  completed/
    {{DATE}}/                  # one folder per calendar day, by completion date
      {{SLUG}}.md              # the finished package, moved here on acceptance
      summary.md               # that day's work summary, appended per package
```

The package filename keeps the date it was written; the completed folder is named
for the date it was accepted. These differ whenever a batch spans midnight, and
that is correct — the filename records authorship, the folder records completion.

**Lifecycle.**

1. After the Before/After is confirmed, the **lead** writes each package to
   `planning/{{DATE}}-{{SLUG}}.md` and the dispatch plan to
   `planning/{{DATE}}-{{SLUG}}-dispatch-plan.md`, **commits and pushes them** —
   the execution tier reads them out of the repository — then tells the user which
   single file to hand over. Any later `## Gaps` list is appended to the package.
2. The **relay lead**, on accepting a package, fills in its `Completion record`
   while the file is still in `planning/`.
3. Then moves it to `completed/{{DATE}}/{{SLUG}}.md` (create the date folder if
   missing). No copy is left behind in `planning/`, and no completed package is
   ever deleted.
4. Then appends one line to `completed/{{DATE}}/summary.md` (create it if
   missing), newest last — **after** the move, never before, so nothing it says
   about where files live is already stale:

   ```text
   - {{SLUG}} — <one-line what changed> · T<tier> · <verification result> · atlas: <boundary/ownership/contract change to report / none>
   ```

5. Then **commits and pushes**, with the code and the change-record files in the
   **same** commit.

The dispatch plan is a routing artifact for one batch; it is not archived and not
required to survive.

Packages and summaries may name modules and files regardless of reporting level;
the reporting level governs only user-facing chat reports.

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

Every initialization or rebuild generates **all three** adapters — lead, relay,
worker — for each confirmed platform. Never generate a partial set: without a
relay adapter the tier that orders, accepts, and records is missing, and
acceptance strands whenever the human does not return.

### Platform Adapters (when selected)

| Platform | Lead path | Relay path | Worker path |
|---|---|---|---|
| Claude Code | `.claude/skills/<project-slug>-atlas/SKILL.md` | `.claude/skills/<project-slug>-relay/SKILL.md` | `.claude/skills/<project-slug>-worker/SKILL.md` |
| Codex | `.agents/skills/<project-slug>-atlas/SKILL.md` | `.agents/skills/<project-slug>-relay/SKILL.md` | `.agents/skills/<project-slug>-worker/SKILL.md` |

Both platforms use the same bodies: `assets/templates/lead_adapter.md`,
`assets/templates/relay_adapter.md`, and `assets/templates/worker_adapter.md`.
Only the destination directory differs. Create the directories at the project
root if they do not exist.

**Frontmatter required** (render `description` in the Step 0 working language;
English shown here):

- Lead — `name: <project-slug>-atlas`, `description`: `Codebase Atlas for
  <PROJECT_NAME> — navigation map, change discipline, and task-package authoring,
  for the agent talking directly to a human. Load once at the start of work on
  this project; do not re-invoke later in the same conversation. An agent running
  a dispatch plan must not load this — it uses <project-slug>-relay. An agent
  executing a single task package must not load this — it uses
  <project-slug>-worker.`
- Relay — `name: <project-slug>-relay`, `description`: `Execution-manager rules
  for <PROJECT_NAME>. Load ONLY when your instructions arrived as a dispatch plan
  — a prompt or file whose header says ROLE: relay-lead. You order the task
  packages it names, dispatch one agent per package, accept their work, and
  record completion. Never load it when working directly with a human (that is
  <project-slug>-atlas) or when executing a single task package (that is
  <project-slug>-worker).`
- Worker — `name: <project-slug>-worker`, `description`: `Execution rules for an
  agent implementing an atlas task package on <PROJECT_NAME>. Load ONLY when your
  instructions arrived as a task package — a prompt whose header says ROLE:
  worker. Never load it when working directly with a human (that is
  <project-slug>-atlas) or when sequencing a whole batch from a dispatch plan
  (that is <project-slug>-relay).`

The tiers commonly run on different platforms — the lead where the human plans,
the relay and worker wherever the execution model runs. Generate all three for
every selected platform regardless; which platform hosts which tier is a runtime
choice, and a missing adapter fails silently by loading the wrong skill.

Each description must name **both** sibling skills.

Set `{{PROJECT_NAME}}`, `{{PROJECT_SLUG}}`, `{{DELIVERY_POLICY}}`, and
`{{REPORTING_LEVEL}}` in all three. Set `{{INDEX_FILE}}` in the lead adapter only,
to the relative path from its directory to the index (e.g.
`../../../docs/<project>_index.md`) — neither the relay nor the worker adapter
reads the index. There is no model token: the relay and worker adapters name
GPT-5.6-Luna, reasoning Max, literally.

### Generic Adapters (only when no platform adapter exists)

- **Paths:** `docs/<project>_lead_adapter.md`,
  `docs/<project>_relay_adapter.md`, and `docs/<project>_worker_adapter.md`
- **Templates:** the same three, with the frontmatter block dropped. They work as
  plain reference docs.
- Generate these only when Step 3's platform confirmation produced no
  platform-specific adapter — the user chose "None — skip adapter generation,"
  or platform detection was inconclusive and the user picked no platform. When
  at least one platform adapter set exists, skip them. Generate both forms only
  if the user explicitly asks for a plain-markdown entrypoint alongside a
  platform adapter.
- **Cleanup:** on any initialization or rebuild, if generic adapter files exist
  from a prior run — including the pre-split single `docs/<project>_adapter.md`
  and the two-role lead/worker pair from format 3 — and at least one platform
  adapter exists or is being generated this run, delete them. Do this as part of
  adapter generation, not as a follow-up task.

### Do Not Force-Load The Skill

Do not write a "run the atlas skill before every operation" mandate into
`CLAUDE.md`, `AGENTS.md`, or any always-on config. At most, add a single
plain-language pointer line noting that the navigation map lives at
`docs/<project>_index.md`, and only if that file does not already say so.

### All Three Adapters Must

- Be self-contained for their role, per the Lead, Relay, and Worker Adapter
  Requirements above. Do not point to separate workflow docs, and do not point at
  each other for content — only for role handoff.
- Open with the role check, naming both siblings.
- Include the reporting level, and the delivery policy or whose the delivery is.
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
