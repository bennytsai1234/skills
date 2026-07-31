# Codebase Atlas

Codebase Atlas is a small Markdown protocol for creating a durable navigation
layer for a repository. It scans a project once, writes a compact atlas under
`docs/`, and gives future agents role-split entrypoints that route ordinary work
before editing code.

## Design Manifesto

AI agents should not treat a repository as a disposable search space on every
task. They should inherit a durable map, use it to reason about ownership and
impact, and only then propose a change.

Codebase Atlas is built around six principles:

- **Map before edit**: future work starts from the atlas, not from a blind file
  search.
- **Initialize once, reuse often**: a strong initialization pass creates context
  that ordinary follow-up work can reuse.
- **Refresh, don't rebuild**: a map that drifted in two modules does not justify
  re-scanning twenty. The index records the commit it was built from, so a later
  run can compute exactly what went stale.
- **Human confirmation matters**: code-changing workflows must explain the
  plain Before / After state before editing — and that gate belongs to the agent
  a human is actually reading.
- **Split by role, not by activity**: a lead agent understands, decides,
  specifies, reviews, and writes the record; an implementation agent explores,
  builds, tests, and reports. Anything else turns the implementer into a project
  manager, or the manager into a distracted implementer.
- **The specification is the leverage**: the lead is not present while the work
  happens, so the task package is its only instrument. Acceptance criteria that a
  stranger can check are worth more than any amount of supervision.
- **Complete, bounded plans**: agents should avoid shortcut-oriented local
  patches and instead propose a coherent scope that actually solves the problem.
- **Markdown over infrastructure**: the atlas stays readable, reviewable,
  versionable, and portable across tools.

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
exists — a platform adapter is loaded automatically by its platform, so the
generic pair would otherwise sit unused.

## The Handoff

**The handoff is human-mediated.** The lead does not spawn the worker. It writes
a task package to a file, tells you where it is, and stops. You hand that file to
your implementation agent. You bring the result back. There is no dispatch, no
concurrency, no scheduling — the unit of delegation is a file a person copies.

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
`Forbidden` are normally copied straight out of the owning module doc's **Do Not
Do** and **Known Risks** — which is why those sections are written the way they
are. It is the same file as the plan; there is no second document to keep in
sync.

Three rules make the loop hold:

- **Acceptance is the whole contract.** The lead is absent while the work
  happens and cannot correct course, so every acceptance item must be checkable
  by someone who was not in the conversation — an exact command with an expected
  result, or an observable behaviour. "Works correctly" is not one.
- **Evidence, not claims.** The worker pastes command output. A claim that a
  check passed is exactly what the review exists to test, so it cannot also be
  the thing reviewed.
- **Single writer.** Only the lead writes atlas docs, plans, completed folders,
  and summaries. A worker that finds the map wrong reports it upward.

Because only one agent is ever active on the tree, whoever holds it owns it: the
worker runs its own build, suite, and migrations while implementing, and there is
nothing to negotiate.

Role is resolved from the instructions, not from the environment: an explicit
`ROLE: worker` header wins, no header means lead, and a governance write gate
blocks the damaging case either way.

**Returning work** names gaps and nothing else, and says so explicitly —
"everything else is accepted, change nothing outside these points." Without that
line a capable agent asked to fix two things will improve five, and the review
starts over. Two returns maximum; a third means the package was wrong, so it is
withdrawn and reissued rather than patched.

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
the commit it was built from, and the atlas format version. That line is what
makes a cheap update possible.

- **Refresh** — for an atlas that has drifted. Diff the recorded commit against
  `HEAD`, map the changed files onto modules through each module doc's scope, and
  classify every module as *stale*, *unmapped*, *removed*, or *untouched*. Only
  stale and new modules are re-scanned, and their docs are updated in place so
  hand-added notes survive. Untouched docs are left byte-identical, the
  Architecture Decisions table is not touched, and adapters are regenerated only
  when the recorded format version is behind the current one. The plan is
  confirmed with the user before any subagent runs — a refresh rewrites docs
  people rely on.
- **Rebuild** — for an atlas whose *structure* is wrong: no usable provenance,
  most modules stale, or a restructure that invalidated the module split itself.
  A refresh over most of the atlas costs more than a rebuild and produces a worse
  result, because each subagent still reasons from a split the restructure
  already broke.

*Unmapped* files are the interesting class: a changed file that belongs to no
module's scope means a new module appeared or a boundary moved. That judgement is
made centrally and confirmed with the user, never inferred by a scanning subagent
that can only see its own module.

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
`description`s make them discoverable when a task needs them, so unrelated
conversations pay no context cost — and each description names the sibling
skill, so a mis-triggered load self-corrects on the first line.

Code-changing work uses a plain Before / After gate as the user-facing
checkpoint. Supporting analysis may guide the agent, but it must not replace the
Before / After explanation.

## Cost

The lead is alive across the whole loop and its context only grows, so that is
where the money goes. Three rules cover it.

**While the package is out, the lead does nothing** — no `git status`, no diff
inspection, no progress narration, no speculative reading. The work is happening
in another process that will report when it is done, and "not finished yet" is
the whole of what any check could return. Each idle turn re-sends a growing
context to buy that non-answer. This is the single largest avoidable cost.

**Specify once, completely.** The lead's one shot at the outcome is the package.
Time spent making acceptance criteria checkable is the cheapest spend in the
loop; every round trip after that costs your attention as well as tokens — and
your attention is the scarce resource here, not tokens.

**Review once, in a batch.** One pass over the whole returned change, one list of
gaps. Reviewing partially and returning twice doubles the number of times you
have to carry something across.

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
