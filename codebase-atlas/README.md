# Codebase Atlas

Codebase Atlas is a small Markdown protocol for creating a durable navigation
layer for a repository. It scans a project once, writes a compact atlas under
`docs/`, and gives future agents an entry router that routes ordinary work
before editing code.

## Design Manifesto

AI agents should not treat a repository as a disposable search space on every
task. They should inherit a durable map, use it to reason about ownership and
impact, and only then propose a change.

Codebase Atlas is built around five principles:

- **Map before edit**: future work starts from the atlas, not from a blind file
  search.
- **Initialize once, reuse often**: a strong initialization pass creates context
  that ordinary follow-up work can reuse.
- **Human confirmation matters**: code-changing workflows must explain the
  plain Before / After state before editing.
- **Complete, bounded plans**: agents should avoid shortcut-oriented local
  patches and instead propose a coherent scope that actually solves the problem.
- **Markdown over infrastructure**: the atlas stays readable, reviewable,
  versionable, and portable across tools.

## What It Creates

```text
docs/
  <project>_index.md
  <project>/
    <module_slug>.md
  <project>_adapter.md
  <project>_techniques/        # optional, only if you opt in
    debugging.md
    tdd.md
    verification.md
    code-review.md
    design-grilling.md
```

The adapter is the single, self-contained entrypoint. It embeds the entry
router — read the index, confirm the project in one sentence, route
know→investigate / change→change — **and** carries the change/investigate
discipline (tiers, Before/After gate, Decision Gate, plan lifecycle,
verification) inline. There are no separate workflow docs, so a routine task
loads only the entrypoint skill plus the index and one or two module docs. The
full technique docs are copied in only when you opt in; otherwise the adapter's
one-line discipline pointers cover them.

## How It Works

1. Silently detect the working language and whether old atlas docs or generated
   entrypoints exist.
2. Explain what the skill creates, then handle old atlas artifacts if needed.
3. Pre-scan existing repository rules and confirm the initial decisions in
   plain language, including each inherited rule and how it will be handled.
4. Inspect repository structure, entrypoints, source roots, tests, configs, and
   existing docs.
5. Split the project into stable modules.
6. Write the index (navigation map + inherited operating constraints), the module
   docs, and the self-contained adapter. Copy the technique docs only on opt-in.
7. Run the quality checklist.

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
self-contained adapter, which reads the index and handles the task itself:

- Read-only work — explanations, investigations, reviews, reproductions,
  profiling, CI failures, risk assessments — follows its investigate path.
- Every code edit follows its change path, with discipline scaled to the task
  (trivial → fast; hard or risky → full).

The adapter is not force-loaded on every conversation. Its skill `description`
makes it discoverable when a task needs repo navigation, so unrelated
conversations pay no context cost.

Code-changing work uses a plain Before / After gate as the user-facing
checkpoint. Supporting analysis may guide the agent, but it must not replace the
Before / After explanation.

## Skill Files

- `SKILL.md`: trigger rules and the initialization workflow.
- `references/atlas-contract.md`: output contract and generation rules.
- `references/modes.md`: standalone and reference-assisted guidance.
- `references/quality-checklist.md`: final review checklist.
- `assets/templates/`: Markdown templates for generated atlas files (index,
  module, and the self-contained adapters).
- `assets/techniques/`: distilled, self-contained discipline docs (debugging,
  TDD, verification, code review, design grilling), copied into a generated atlas
  only when the user opts in.

## License

MIT
