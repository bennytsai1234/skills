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
- **Split by role**: the lead understands, decides, specifies, reviews, and
  writes the record; the implementation agent explores, builds, tests, and
  reports.
- **The lead never edits code**: no size exemption, no escape hatch.
- **Acceptance criteria a stranger can check**: the lead is absent while the work
  happens, so the package carries the whole contract.
- **Complete, bounded plans**: no shortcut-oriented local patches.
- **Markdown over infrastructure**: readable, reviewable, versionable, portable.

## What It Creates

```text
docs/
  <project>_index.md          # map tiers 1-2: overview + module routing
  <project>/
    <module_slug>.md          # map tier 3: loaded only when a task needs it

docs/changes/
  planning/{{DATE}}-{{SLUG}}.md   # the task package — plan and handoff in one file

.claude/skills/               # or .agents/skills/ for Codex
  <project-slug>-atlas/       # lead entrypoint  — human-facing agent
  <project-slug>-worker/      # worker entrypoint — the implementation agent
```

Two entrypoints, split by role:

- **Lead adapter** — for the agent talking to a human. Entry router (read the
  index, confirm the project in one sentence, route know→investigate /
  change→change), change discipline (tiers, Decision Gate, Before/After gate),
  task-package authoring, review of what comes back, and every governance write.
  It does not implement, and it does not spawn anything.
- **Worker adapter** — for the implementation agent a human hands a package to.
  It explores the code freely, designs and makes the change across whatever files
  are needed, writes and runs tests, fixes failures until they pass, and reports
  with pasted evidence. It never runs the Before/After gate, never writes plans
  or atlas docs, and never commits.

Generic `docs/*_adapter.md` copies are generated only when no platform adapter
exists.

## The Handoff

**The handoff is human-mediated.** The lead does not spawn the worker. It writes
a task package to a file, tells you where it is, and stops. You hand that file to
your implementation agent. You bring the result back. There is no dispatch, no
concurrency, no scheduling.

**The lead never edits code.** No size exemption: a typo leaves as a task package
like everything else. It reads, runs read-only checks, and re-runs a verification
that decides acceptance; a failure there is a gap to return, not something to
fix.

```text
You       → state the need
Lead      1. understand the project and the need
          2. decide the solution boundary
          3. write the acceptance-testable task package
Worker    4. explore the relevant code
          5. design and make the change, across files as needed
          6. add tests, run them, fix failures until green
          7. report with evidence and risks
Lead      8. review: requirement conformance, architecture, diff, tests
          9. accept — or return precise gaps, nothing else
Worker   10. fix exactly the named gaps
Lead     11. final acceptance, then deliver
```

The **task package** (`atlas/v2`) carries goal, why, the solution boundary,
starting points, scope, what must be preserved, what is forbidden, acceptance
criteria, required tests, and the evidence to bring back. `Must Preserve` and
`Forbidden` are copied straight out of the owning module doc's **Do Not Do** and
**Known Risks**. It is the same file as the plan.

Three rules hold the loop together:

- **Acceptance is the whole contract.** Every acceptance item must be checkable
  by someone who was not in the conversation — an exact command with an expected
  result, or an observable behaviour. "Works correctly" is not one.
- **Evidence, not claims.** The worker pastes command output, never a summary of
  it.
- **Single writer.** Only the lead writes atlas docs, plans, completed folders,
  and summaries. A worker that finds the map wrong reports it upward.

Only one agent is active on the tree at a time, and whoever holds it owns it: the
worker runs its own build, suite, and migrations while implementing.

Role is resolved from the instructions, not from the environment: an explicit
`ROLE: worker` header wins, no header means lead, and a governance write gate
backstops both.

**Returning work** names gaps and nothing else, ending with the required line
"everything else is accepted, change nothing outside these points." Two returns
maximum; on a third the package is withdrawn and reissued rather than patched.

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
   and the lead/worker adapter pair centrally (generating the generic `docs/`
   pair only when no platform adapter exists, and deleting stale ones —
   including the pre-split single adapter — otherwise).
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
- Every code edit follows its change path, with specification scaled to the task
  (trivial → a minimal package; hard or risky → a Decision Gate first and
  explicit evidence requirements), ending in a task package you hand over.

Neither adapter is force-loaded on every conversation. Their skill
`description`s make them discoverable when a task needs them, and each names the
sibling skill so a mis-triggered load self-corrects on the first line.

Code-changing work uses a plain Before / After gate as the user-facing
checkpoint. Supporting analysis may guide the agent, but must not replace it.

## Cost

**While the package is out, the lead does nothing** — no `git status`, no diff
inspection, no progress narration, no speculative reading. It waits for you to
bring back the report.

**Specify once, completely.** Spend the effort on making acceptance criteria
checkable, before the handoff.

**Review once, in a batch.** One pass over the whole returned change, one list of
gaps.

## Skill Files

- `SKILL.md`: trigger rules and the initialization workflow.
- `references/atlas-contract.md`: output contract and generation rules.
- `references/delegation.md`: the two-agent doctrine — the loop, roles, role
  resolution, the `atlas/v2` task package, forbidden implementation patterns, the
  report format, review and return, and cost control.
- `references/modes.md`: standalone and reference-assisted guidance.
- `references/quality-checklist.md`: final review checklist.
- `assets/templates/`: Markdown templates for generated atlas files (index,
  module, and the lead/worker adapters).

## License

MIT
