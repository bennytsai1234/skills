---
name: codebase-atlas
description: "Build, refresh, or rebuild a durable engineering map for an existing code repository. Use only when the human explicitly asks to create/update/rebuild the Codebase Atlas or engineering map. Generate only the atlas index and per-module map docs under docs/; do not create project foundation files, ordinary change plans, or source changes."
---

# Codebase Atlas

Create and maintain a repository navigation map. The atlas explains module ownership, boundaries, key flows, dependencies, and where future work should start. Exact symbol/file locations remain the job of live search.

Read `references/atlas-contract.md` before writing output. Use `references/modes.md` only when the human supplied a reference repository/spec/design. Validate with `references/quality-checklist.md` before reporting completion.

## Scope

This skill creates or updates only:

```text
docs/<project>_index.md
docs/<project>/<module_slug>.md
```

Do not create or rewrite:

- `AGENTS.md`
- `README.md`
- `DEVELOPMENT.md`
- `DESIGN.md`
- `docs/architecture.md`
- `docs/changes/**`

Those belong to project foundation or normal development workflows.

## Before scanning

1. Read applicable project rules and existing docs only to understand repository reality.
2. Detect the working language: explicit project rule first, otherwise the human's request language.
3. Detect whether an atlas already exists and read its provenance line.
4. If the human explicitly said `refresh`, update incrementally.
5. If the human explicitly said `rebuild`, replace the atlas from current repository reality.
6. If an atlas exists and the request only says "update" or "fix the map", prefer refresh when provenance is usable; ask only when the correct mode cannot be inferred.
7. If no atlas exists, initialize it.

Do not force a reference-template choice unless the human actually supplied or named a reference.

## Initialization

1. Read `references/atlas-contract.md`.
2. Inspect repository manifests, entrypoints, top-level source roots, tests, README, `DEVELOPMENT.md`, `DESIGN.md`, and `docs/architecture.md` when present.
3. Infer candidate module boundaries from stable change ownership, not file count or technical layers alone.
4. Deep-scan each candidate module. Parallelize independent module scans when the environment supports useful subagents; otherwise scan directly.
5. Reconcile boundaries centrally when scans show a module should split or merge.
6. Write each module doc from `assets/templates/module.md`.
7. Write the index from `assets/templates/index.md`, including build provenance.
8. Run the quality checklist and fix generated-file problems before reporting completion.

Only ask the human about a module boundary when repository evidence leaves a real ownership choice unresolved.

## Refresh

Use the provenance commit recorded in the existing index.

1. Compute repository drift from the recorded commit to current `HEAD`.
2. Exclude generated/vendor/cache/build paths from the drift set.
3. Map changed source files to module scopes.
4. Re-scan only stale modules.
5. Resolve unmapped changed files centrally: extend an existing module, add a new module, or identify a boundary change.
6. Remove a module doc only when its owned scope no longer exists.
7. Leave untouched module docs byte-identical.
8. Update the index only when module links/summaries changed, then update provenance last.
9. Run the quality checklist across the final map.

If provenance is unusable or module boundaries changed so broadly that incremental mapping is unreliable, explain why and switch to rebuild only with human agreement.

## Rebuild

Re-scan the repository from current reality and replace the atlas index/module docs. Preserve unrelated `docs/` content and `docs/changes/**`.

Remove confirmed legacy Atlas-generated workflow/adaptor artifacts only when they are clearly superseded by the global Atlas skills. Never delete unrelated `.agents/`, `.claude/`, or project docs.

## Delivery

Follow the human's current instruction and project `AGENTS.md` for commit/push behavior. This skill does not store delivery policy inside the atlas.

## Principles

- Map ownership and routes; do not make a file inventory.
- Ground claims in committed repository files or persistent project docs.
- Record real uncertainty as `TODO`; never invent missing architecture.
- Keep all generated paths relative and forward-slash shaped.
- Do not normalize unrelated line endings.
- Do not make ordinary work depend on re-running this skill. Daily work reads the map; map maintenance is explicit.
