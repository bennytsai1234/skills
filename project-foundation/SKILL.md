---
name: project-foundation
description: "Organize and clean up a repository: a lean top level with deploy targets in deploy/<target>/, AGENTS.md as the single agent guide, an orderly experiment area (run names, version registry, per-run notes), and unused image tags, containers and weights pruned on hosts. Use when asked to set up or clean up a project, its docs, experiments, deploy files or running service versions (整理專案、清理專案)."
---

# Project Foundation

Organize a repository so the next agent or human can work in it without guessing. Code and git history are the primary source of truth; documents hold only what they cannot show. Hard-won knowledge comes from experiments, so the experiments themselves are kept in order and the conclusions point back to them.

Read `references/document-contract.md` before creating or reorganizing documents, `references/cleanup.md` before moving or deleting files or host artifacts, and `references/experiments.md` whenever the repository runs experiments (model, data, tuning, benchmarks, A/B comparisons).

## Target shape

A top level that can be read in one glance: documents, toolchain-required files, and directories. Nothing else.

```text
AGENTS.md              # single guide for all coding agents, Claude Code included
<toolchain files>      # what the toolchain requires at the root (*.csproj, pyproject.toml, entry module, ...)
<source/test dirs>
deploy/<target>/       # one directory per deploy target: Dockerfile, compose.yml, run script
scripts/               # operational entry points still in use
experiments/           # only when the repository runs experiments
  VERSIONS.md          # version registry
  <run-id>/notes.md    # one record per run
DESIGN.md              # only when the repository has a real UI/design system
```

Every file and every host artifact needs a current consumer. Variant files encoded in suffixes (`Dockerfile.H200.vllm-asr`), unreferenced build files, the `docs/` directory, and old image tags are cleaned up following `references/cleanup.md`.

## Organize once, maintain every day

A one-time cleanup decays unless everyday work keeps it. The rules that keep the shape live in the repository's `AGENTS.md`, which every session loads: the maintenance section from `references/cleanup.md` (top level, deploy targets, removing what is replaced, no topic docs, scratch files, host versions) and, for repositories that run experiments, the experiments section from `references/experiments.md`. This skill writes and updates those sections; it is not what keeps the repository tidy between runs.

Do not create `README.md`, `CLAUDE.md`, `DEVELOPMENT.md`, a `docs/` directory, a lessons folder, or other documents. Module structure, data flow and file layout are read from the code, behavior contracts live in tests, and work history lives in git; written copies go stale. An existing `README.md` is the human's entry point: keep it short and correct what is stale, but do not create one or move agent rules into it.

## Key decisions are pulled up and labeled

A finding that changes how future work is done (data format, training recipe, engine choice) is pulled up from the run notes into the key decisions list in `AGENTS.md`, with an evidence label:

- `[verified]`: shown by recorded runs that isolate the factor, checked against ground truth or by a human where scripts can mislead; lists its run ids. Changing it needs new run evidence.
- `[unverified]`: model reasoning, explanations, untested plans; names its source. It can be overridden or dropped at any time without evidence and is never a reason to refuse a change.

Split mixed statements so only the observed part is `[verified]`. When unsure, label `[unverified]`. Details are in `references/experiments.md`.

## Existing repository workflow

1. Read applicable global/project instructions.
2. Inventory the top level (tracked, untracked and ignored, with sizes), deploy and build files with their consumers, `docs/` content, and where knowledge is buried: gotcha lines, handoff and experiment notes, workaround comments in code, and fix commits whose messages explain a cause.
3. Classify each item using `references/document-contract.md`: rule for `AGENTS.md`, run record under the experiment root, belongs in code/tests, or drop.
4. If the repository runs experiments, organize them following `references/experiments.md`: inventory runs, scripts, data and version names; show the rename/move map to the human before moving anything; backfill `notes.md` marking reconstructed fields as inference; build `VERSIONS.md`; ask about runs whose question or verdict cannot be reconstructed.
5. Write or update the `AGENTS.md` experiments section. Pull key decisions up into it with `[verified]`/`[unverified]` labels, and relabel existing rules that state reasoning as fact. Merge duplicates into one canonical location.
6. Fold the still-useful parts of an existing `CLAUDE.md`, `DEVELOPMENT.md`, `docs/architecture.md` and similar guidance docs into `AGENTS.md`, then remove those files. Drop content that only restates what the code shows.
7. Update stale wording when repository evidence proves the current state changed.
8. Do not delete ecosystem-required files (LICENSE, tool configuration), files an external tool or party requires, an existing `README.md`, or Atlas packages under `docs/changes/planning/` while their dispatch is still running.
9. Agent memory outside the repository (for example Claude Code auto-memory) may hold experiment verdicts and project rules. Propose them as candidates and copy only after the human confirms; never copy credentials, hostnames or account details the repository does not already contain.
10. Clean up the repository shape following `references/cleanup.md`: deploy variants into `deploy/<target>/`, unconsumed files deleted, `docs/` harvested and removed, untracked clutter classified. Present the full move/rename/delete map first and apply only the groups the human approves.
11. If the project deploys to hosts, prune runtime artifacts following `references/cleanup.md`: keep what is running plus one rollback per service, delete the rest only after confirmation, then check the services are still healthy.
12. Write or update the `AGENTS.md` maintenance section from `references/cleanup.md`, filled in with this repository's actual top level, deploy targets and hosts.
13. Decide whether `DESIGN.md` is justified; skip it when it would be empty or speculative.
14. Validate links and paths, run the tests or build that cover moved files, and eliminate contradictory duplicate instructions.

## New repository workflow

1. Create `AGENTS.md` with the known conventions and commands and the maintenance section from `references/cleanup.md`; use explicit TODOs for genuinely undecided values rather than inventing them.
2. If the repository will run experiments, add the experiments section to `AGENTS.md` and create the experiment root when the first run happens; an empty registry or placeholder run adds nothing.
3. Create `DESIGN.md` only when a UI/design system or confirmed prototype already exists.

## Design decision

`DESIGN.md` means product visual/design system guidance for coding agents: visual direction, tokens, typography, layout, components, interaction conventions, and do/don't guidance that actually exists in the product.

Do not use it for one feature proposal or a backend implementation plan. If the repository has no meaningful UI, omit it.

## Delivery

Follow current human instructions and repository `AGENTS.md` for commit/push behavior. Report which documents were created, merged or removed, what was renamed, moved or deleted (old → new), host artifacts removed and space freed, which run notes were backfilled and from what sources, and which questions are still open for the human.
