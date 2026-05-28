# Codebase Atlas

Codebase Atlas is a small Markdown protocol for creating a durable navigation
layer for a repository. It scans a project once, writes a compact atlas under
`docs/`, and gives future agents a main workflow that routes ordinary work
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
  <project>_understand_workflow.md
  <project>_change_workflow.md
  <project>_validate_workflow.md
  <project>_main_workflow.md
  <project>_adapter.md
```

The default adapter is always generated. It stays thin and points back to the
canonical main workflow under `docs/`.

## How It Works

1. Silently detect the working language and whether old atlas docs or generated
   entrypoints exist.
2. Explain what the skill creates, then handle old atlas artifacts if needed.
3. Pre-scan existing repository rules and confirm the initial decisions in
   plain language, including each inherited rule and how it will be handled.
4. Inspect repository structure, entrypoints, source roots, tests, configs, and
   existing docs.
5. Split the project into stable modules.
6. Write a module index with inherited operating constraints, module notes,
   four workflow docs, and the default adapter.
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

Do not rerun Codebase Atlas for ordinary work. Use the generated workflow docs:

- `docs/<project>_main_workflow.md` for daily routing across all task types.
- `docs/<project>_understand_workflow.md` for explanations and investigations.
- `docs/<project>_change_workflow.md` for bugs, features, optimizations, and
  refactors.
- `docs/<project>_validate_workflow.md` for checks, reviews, reproductions, and
  risk assessments.

Code-changing workflows use a plain Before / After gate as the user-facing
checkpoint. Supporting analysis may guide the agent, but it must not replace
the Before / After explanation.

## Skill Files

- `SKILL.md`: trigger rules and main workflow.
- `references/atlas-contract.md`: output contract and generation rules.
- `references/modes.md`: standalone and reference-assisted guidance.
- `references/quality-checklist.md`: final review checklist.
- `assets/templates/`: Markdown templates used for generated atlas files.

## License

MIT
