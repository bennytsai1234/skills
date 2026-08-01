# Codebase Atlas

Codebase Atlas is a small Markdown protocol for creating a durable navigation
layer for a repository. It scans a project once, writes an atlas under `docs/`,
and gives future agents role-split entrypoints that route ordinary work before
editing code.

## Rules

- **Map before edit**: work starts from the atlas, not from a blind file search.
- **Initialize once, refresh after**: the index records the commit it was built
  from, so a later run re-scans only the modules that drifted.
- **Before / After before any change**: stated by the agent the human is reading,
  never agent-to-agent.
- **Split by role**: the lead understands, decides, specifies, and reviews; the
  relay lead orders, dispatches, accepts, and records; the implementation agent
  explores, builds, tests, and reports.
- **The lead never edits code**: no size exemption, no escape hatch.
- **Acceptance criteria a stranger can check**: the lead is absent while the work
  happens — and may never return — so the package carries the whole contract and
  the relay lead is the gate that always runs.
- **Complete, bounded plans**: no shortcut-oriented local patches.
- **Markdown over infrastructure**: readable, reviewable, versionable, portable.

## What It Creates

```text
docs/
  <project>_index.md          # map tiers 1-2: overview + module routing
  <project>/
    <module_slug>.md          # map tier 3: loaded only when a task needs it

docs/changes/
  planning/{{DATE}}-{{SLUG}}.md                 # a task package — plan and handoff in one file
  planning/{{DATE}}-{{SLUG}}-dispatch-plan.md   # the single file you hand over

.claude/skills/               # or .agents/skills/ for Codex
  <project-slug>-atlas/       # lead entrypoint   — human-facing planning
  <project-slug>-relay/       # relay entrypoint  — execution management
  <project-slug>-worker/      # worker entrypoint — one package, end to end
```

Three entrypoints, split by role:

- **Lead adapter** — for the agent talking to a human, on the strongest available
  model. Entry router (read the index, confirm the project in one sentence, route
  know→investigate / change→change), change discipline (tiers, Decision Gate,
  Before/After gate), diagnosis, decomposition, package and dispatch-plan
  authoring, second-pass review, and atlas writes. It does not implement, and it
  does not dispatch.
- **Relay adapter** — for the agent you hand the dispatch plan to, on
  GPT-5.6-Luna with reasoning Max. It orders the batch within the plan's
  dependencies, decides real parallelism, dispatches one agent per package, waits
  without interfering, accepts by re-running the decisive checks itself, records
  completion, and commits.
- **Worker adapter** — for the implementation agent the relay lead dispatches. It
  explores the code freely, designs and makes the change across whatever files are
  needed, writes and runs tests including full builds and suites, fixes failures
  until they pass, and reports with pasted evidence. It never runs the
  Before/After gate, never writes plans or atlas docs, and never commits.

Generic `docs/*_adapter.md` copies are generated only when no platform adapter
exists.

## The Handoff

**The human crosses the workflow once.** The lead writes the packages and one
dispatch plan, commits and pushes them, and stops. You hand that single plan to
the relay lead. Everything after that is agent-to-agent — because you are not
expected to come back, and the workflow has to be complete without you.

**The lead never edits code.** No size exemption: small fixes like a typo go
straight to an execution model rather than becoming task packages. It reads, runs
read-only checks, and re-runs a verification that decides acceptance; a failure
there is a gap to return, not something to fix.

```text
You       → state the need
Lead      1. understand the project and the need
          2. clarify the goal and acceptance evidence
          3. write the task packages
          4. write the dispatch plan, commit and push, hand it over
You       → give the dispatch plan to the relay lead
Relay     5. read the plan and every package it names
          6. order the work; decide real parallelism
          7. dispatch one agent per package
Worker    8. explore, implement across files as needed
          9. run the checks that prove acceptance
         10. report with evidence and risks
Relay    11. accept by re-running the decisive checks — or return precise gaps
         12. record completion, archive, summarize, commit and push
         13. run the batch verification, report
Lead     14. (if you return) second-pass review, and atlas updates
```

Step 14 may never happen. That is expected, not a failure.

The **task package** (`atlas/v3`) carries the desired result and objective
acceptance checks. It may include optional starting points and `Constraints`, but
only when they record requirements the worker cannot infer from the repository or
ordinary engineering judgement — for example API compatibility, schema ownership,
dependency policy, component ownership, or deterministic verdict authority. It
does not prescribe the implementation. It is the same file as the plan.

Its `Background` section is what makes it portable: the package is read by a model
that never saw the conversation it came from, possibly on another platform, so the
diagnosis has to travel with it — the wrong code quoted, real input against real
wrong output, any inventory already done. There is no length limit on it.

Four rules hold the loop together:

- **Acceptance is the whole contract.** Every acceptance item must be checkable
  by someone who was not in the conversation — an exact command with an expected
  result, or an observable behaviour. "Works correctly" is not one.
- **Evidence, not claims.** The worker pastes command output, never a summary of
  it, and the relay lead re-runs the decisive checks rather than believing the
  report.
- **Governance files are split by tier.** The lead owns atlas docs and
  `docs/changes/planning/`; the relay lead owns completion records,
  `docs/changes/completed/`, and implementation commits. Workers write neither.
  Both tiers push — the lead before handover, since the relay lead reads the
  packages out of the repository.
- **Waiting is passive, and blocking.** The relay lead waits with the platform's
  blocking wait (on Codex, `wait_agent`, one hour per call), never a `sleep`,
  which a completion event cannot preempt. While a subagent is in flight it runs
  no git command, no build, no test, and no progress query — and never
  re-dispatches a task that may still be running, since two agents editing the
  same files overwrite each other invisibly. A wait that times out means the
  window closed, not that the task failed.

One agent implements on the tree at a time, and whoever holds it owns it: the
worker runs the checks needed to establish acceptance while implementing. Where
two packages would contend, the relay lead serializes them rather than fencing
either — task packages carry starting points, not allowed paths.

Role is resolved from the instructions, not from the environment: `ROLE: worker` →
worker, `ROLE: relay-lead` → relay lead, no header → lead, with a governance write
gate backstopping all three.

**Returning work** names gaps and nothing else, ending with the required line
"everything else is accepted, change nothing outside these points." Two returns
maximum; on a third the specification is the suspect, and that is the lead's to
withdraw, fix, and reissue.

**Trivial fixes do not belong here.** A typo, a constant, a one-line config change
goes straight to an execution model — no lead, no dispatch plan, no package. There
is no trivial tier, by design: the moment one exists, deciding what counts as
trivial costs more than the fix.

## How It Works

1. Silently detect the working language and whether old atlas docs or generated
   entrypoints exist.
2. Explain what the skill creates, then handle old atlas artifacts if needed.
3. Pre-scan existing repository rules and confirm the initial decisions in
   plain language, including each inherited rule and how it will be handled.
4. Inspect repository structure shallowly to propose a module split, then
   dispatch one subagent per candidate module, in parallel, to deep-scan that
   module and write its module doc directly.
5. Reconcile the module list from the subagents' findings and write the index
   and all three adapters centrally (generating the generic `docs/` set only when
   no platform adapter exists, and deleting stale ones — including the pre-split
   single adapter and the format-3 lead/worker pair — otherwise).
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
  hand-added notes survive. Untouched docs are left byte-identical, the
  Architecture Decisions table is not touched, and adapters are regenerated only
  when the recorded format version is behind the current one. The plan is
  confirmed with the user before any subagent runs.
- **Rebuild** — for an atlas whose *structure* is wrong: no usable provenance,
  most modules stale, or a restructure that invalidated the module split itself.

An *unmapped* file — one that belongs to no module's scope — means a new module
appeared or a boundary moved. That judgement is made centrally and confirmed with
the user, never inferred by a scanning subagent.

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

## Daily Use After Initialization

Do not rerun Codebase Atlas for ordinary work. Daily work enters through the
lead adapter, which reads the index and handles the task itself:

- Read-only work — explanations, investigations, reviews, reproductions,
  profiling, CI failures, risk assessments — follows its investigate path.
- Every code change follows its change path, with specification scaled to the
  task (normal → a full package; hard or risky → a Decision Gate first and
  explicit evidence requirements), ending in task packages and one dispatch plan
  you hand over.

No adapter is force-loaded on every conversation. Their skill `description`s make
them discoverable when a task needs them, and each names both sibling skills so a
mis-triggered load self-corrects on the first line.

Code-changing work uses a plain Before / After gate as the user-facing
checkpoint. Supporting analysis may guide the agent, but must not replace it.

## Cost

**While work is out, do nothing** — no `git status`, no diff inspection, no
progress narration, no speculative reading. That holds for the lead across the
whole batch, and for the relay lead while a subagent is in flight.

**Specify once, completely.** Spend the effort on making acceptance criteria
checkable, before the handoff.

**Review once, in a batch.** One pass over the whole returned change, one list of
gaps.

## Skill Files

- `SKILL.md`: trigger rules and the initialization workflow.
- `references/atlas-contract.md`: output contract and generation rules.
- `references/delegation.md`: the three-tier doctrine — the loop, roles, role
  resolution, the dispatch plan, the `atlas/v3` task package, concurrency and
  waiting, shortcut patterns, the report format, acceptance, the completion
  protocol, and cost control.
- `references/modes.md`: standalone and reference-assisted guidance.
- `references/quality-checklist.md`: final review checklist.
- `assets/templates/`: Markdown templates for generated atlas files (index,
  module, and the lead / relay / worker adapters).

## License

MIT
