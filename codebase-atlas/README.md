# Codebase Atlas

Codebase Atlas is a small Markdown protocol for creating a durable navigation
layer for a repository. It scans a project once and writes an atlas under
`docs/` — an index and per-module docs. That is all this skill does.

The day-to-day work on top of the map is handled by four skills installed once
on this machine and shared by every project: **`atlas-planner`**, **`atlas-relay`**,
**`atlas-worker`**, and **`atlas-fast`**. Nothing is generated per project for
them — they find a project's atlas on their own. This split exists so that
building the map and running the workflow are two independent concerns: a map
rebuild never touches workflow logic, and a workflow change never requires
re-running a scan.

## Rules

- **Map before edit**: work starts from the atlas, not from a blind file search.
- **Initialize once, refresh after**: the index records the commit it was built
  from, so a later run re-scans only the modules that drifted.
- **This skill only builds the map.** It has no opinion on how work happens
  afterward — that doctrine lives in `atlas-planner`'s `references/delegation.md`.
- **Markdown over infrastructure**: readable, reviewable, versionable, portable.

## What It Creates

```text
docs/
  <project>_index.md          # map tiers 1-2: overview + module routing
  <project>/
    <module_slug>.md          # map tier 3: loaded only when a task needs it
```

`docs/changes/` (planning packages, dispatch plans, completion records) is
written later by `atlas-planner` and `atlas-relay` during ordinary work — this
skill does not create it.

## The Four Skills That Read The Map

These are documented in full in their own skill directories
(`atlas-planner`, `atlas-relay`, `atlas-worker`, `atlas-fast`); this is the short
version so you know what to expect once an atlas exists.

- **`atlas-planner`** — for the agent talking directly to a human, on the
  strongest available model. Entry router (read the index, confirm the project
  in one sentence, route know→investigate / change→change), change discipline
  (tiers, Decision Gate, Before/After gate), diagnosis, decomposition, package
  and dispatch-plan authoring, spec fixes on escalation, and atlas writes for
  work it planned itself. It does not implement, and it does not dispatch.
- **`atlas-relay`** — for the agent a human hands a dispatch plan to. It orders
  the batch within the plan's dependencies, decides real parallelism, sends
  non-frontend packages to GPT subagents, runs frontend packages through Claude
  Sonnet 5 with `claude -p`, waits without interfering, accepts by re-running the
  decisive checks itself, relays mid-course adjustments to the same package
  route, records completion, commits, and refreshes the map at batch end.
- **`atlas-worker`** — for either implementation route the relay manages. It
  explores the code freely, designs and makes the change across whatever files
  are needed, writes and runs tests including full builds and suites, fixes
  failures until they pass, and reports with pasted evidence. It never runs the
  Before/After gate, never writes plans or atlas docs, and never commits.
- **`atlas-fast`** — for an immediate change with none of the above, when a human
  explicitly asks to skip the process. No plan, no package, no acceptance step;
  git's commit history is the only record it leaves.

The full three-tier doctrine these three share — the loop, the dispatch plan and
task package shapes, concurrency and waiting, acceptance, and the completion
protocol — lives in `atlas-planner/references/delegation.md`. This skill's
contract (`references/atlas-contract.md`) only covers what it generates: the
index and module docs.

## Modes

- **Standalone**: the target repository is the only source of truth.
- **Reference-assisted**: a reference repository, spec, design, screenshot set,
  or prior implementation guides selected boundaries and patterns. It is not a
  feature backlog unless the user explicitly chooses full alignment.

Reference use is confirmed with three user-facing choices:

- **No reference**: build the atlas from this project only.
- **Partial reference**: use only the selected parts of the reference, such as
  data flow, UI structure, error handling, diagnostics, or test patterns.
- **Full alignment**: make the project fully match the reference's
  functionality, only when explicitly requested.

Initialization confirmations should avoid internal setting names. The agent
should ask plain-language questions and show each inherited project rule with
the concrete handling that will be written into the atlas.

## How It Works

1. Silently detect the working language and whether an old atlas or legacy
   per-project entrypoint skills exist.
2. Explain what the skill creates, then handle old atlas artifacts if needed.
3. Pre-scan existing repository rules and confirm the initial decisions in
   plain language, including each inherited rule and how it will be handled.
4. Inspect repository structure shallowly to propose a module split, then
   dispatch one subagent per candidate module, in parallel, to deep-scan that
   module and write its module doc directly.
5. Reconcile the module list from the subagents' findings and write the index
   centrally.
6. Dispatch one verification subagent per generated file, in parallel, to
   re-check and fix that file directly, then run a final centralized
   cross-file check plus the quality checklist.
7. Apply the delivery policy (no commit / commit only / commit and push),
   never force-pushing.

## Refresh vs Rebuild

Every generated index records a build provenance line: the date it was built,
the commit it was built from, and the atlas format version.

- **Refresh** — for an atlas that has drifted. Diff the recorded commit against
  `HEAD`, map the changed files onto modules through each module doc's scope, and
  classify every module as *stale*, *unmapped*, *removed*, or *untouched*. Only
  stale and new modules are re-scanned, and their docs are updated in place so
  hand-added notes survive. Untouched docs are left byte-identical, and the
  Architecture Decisions table is not touched. The plan is confirmed with the
  user before any subagent runs.
- **Rebuild** — for an atlas whose *structure* is wrong: no usable provenance,
  most modules stale, or a restructure that invalidated the module split itself.
  A rebuild also removes any legacy per-project entrypoint skills a pre-format-5
  atlas generated — they are superseded by the global four skills above.

An *unmapped* file — one that belongs to no module's scope — means a new module
appeared or a boundary moved. That judgement is made centrally and confirmed with
the user, never inferred by a scanning subagent.

## Daily Use After Initialization

Do not rerun Codebase Atlas for ordinary work. Daily work enters through
`atlas-planner`, which reads the index and handles the task itself — or through
`atlas-fast` when the human explicitly wants to skip the process. No skill is
force-loaded on every conversation; each one's `description` makes it
discoverable when a task needs it, and each names its siblings so a
mis-triggered load self-corrects on the first line.

## Skill Files

- `SKILL.md`: trigger rules and the initialization/refresh workflow.
- `references/atlas-contract.md`: the map's output contract and generation
  rules — index and module docs only.
- `references/modes.md`: standalone and reference-assisted guidance.
- `references/quality-checklist.md`: final review checklist.
- `assets/templates/`: Markdown templates for the generated index and module
  docs.

## License

MIT
