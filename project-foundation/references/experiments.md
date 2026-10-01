# Experiment Convention

Experiments are where a project's hard-won knowledge comes from. Keep them orderly enough that the chain "question → setup → result → verdict → next run" can be read back later without guessing. There is no separate lessons document: the run records are the source, and `AGENTS.md` holds only the conclusions that change how people work, linked to the runs behind them.

## Layout

One tracked experiment root per repository, named in `AGENTS.md` (default `experiments/`):

```text
experiments/
  VERSIONS.md            # version registry, tracked
  <run-id>/
    notes.md             # run record, tracked
    config.*             # exact command, parameters and inputs used, tracked (small)
    outputs/             # results, ignored by git when large
```

- Scripts live in the repository's code and are versioned by commit. A run records the script path, arguments and commit; do not keep ad-hoc script copies inside run directories.
- Datasets and models live in one data root with versioned names. A run references them by name and version; copy data into a run only when it is small and specific to that run.
- Ignore only the bulky parts (for example `experiments/*/outputs/`). Never put tracked records under an ignored directory: git cannot re-include a file whose parent directory is excluded.

## Naming

- Run id: `YYYYMMDD-<topic>-<short-commit>`, lowercase kebab-case, for example `20260922-speaker-evidence-ab-6596512`. One date format only. Add `-2`, `-3` for repeats of the same topic and commit on the same day.
- Topic: what is being tested, not the outcome (`moss-long-audio-chunking`, not `fix-works`).
- Do not use generic names such as `verify`, `test`, `benchmark` or `tmp` without a topic.

## Versions

- Every versioned artifact family (fine-tuned model, dataset, prompt recipe) uses `<family>-v<N>` with an integer `N` that only increases, for example `moss-ft-v16`, `moss-train-data-v16`.
- No letter suffixes (`v13b`), adjectives (`Ultra`, `full`, `final`) or decimal mixes inside a version. A variant worth keeping gets the next integer; its description goes in the registry.
- `VERSIONS.md` has one row per version: version, date, base version, what changed, data version, evaluating run id(s), status (`current`, `candidate`, `retired`).
- Identifiers already deployed or used as cache keys (for example a model tag that isolates a cache) keep their existing names. Record the legacy name next to the registry entry instead of renaming it; the scheme applies to new versions.

## `notes.md`

Write it when the run finishes, before reporting results. Keep it to about one screen, in the repository's working language:

```markdown
# <run-id>

- Previous: <run-id this continues, if any>
- Question: what this run answers, or the hypothesis
- Setup: commit <sha>, script <path> <args>, data <name-vN>, model <family-vN>, host
- Result: key numbers with units and conditions; full outputs in outputs/
- Verdict: conclusion, and how it was judged (human listening / script / against ground truth)
- Unverified: explanations or ideas this run did not test, if any
- Next: what was done because of it (commit, next run id, key decision pulled up or changed)
```

## Key decisions: pull them up

A finding that changes how future work is done must not stay buried in one run's `notes.md`. Pull it up into the key decisions section of `AGENTS.md`. The test: would someone planning the next experiment or change choose differently without knowing it? Example: "training data converted to Simplified Chinese works best; training on Traditional Chinese makes the model collapse" decides every later data preparation, so it goes up.

Every key decision carries an evidence label, and the two labels follow different rules:

- `[verified]`: observed directly in recorded runs whose setup isolates the factor (same everything except what is compared), with the result checked against ground truth or by a human where scripts can mislead. List the run id(s). Changing it needs new run evidence that continues the chain; then update the decision and its references together.
- `[unverified]`: anything not shown by such a run: model reasoning, plausible explanations of why something happened, untested alternatives, follow-up plans ("retraining with different prompts should help"). Name its source (for example "model inference, not run"). It may be overridden or dropped at any time without evidence, must not be cited as a reason to refuse a change, and must not be written as fact. List it only when current practice depends on it or it is the next thing to test, so nobody mistakes it for an established rule.

Split mixed statements. In "Simplified works best because of tokenization, so retrain with different prompts", only the observed comparison is `[verified]`; the cause and the plan are `[unverified]` until a run tests them.

Never promote to `[verified]` on a script's number alone when the check could be wrong (alignment, slicing, metric choice); open the actual outputs or compare against ground truth first. When the evidence is ambiguous, keep `[unverified]`.

Pitfalls that did not come from an experiment (environment, tooling, delivery) are ordinary one-line rules in `AGENTS.md`; they need no label or run.

## The `AGENTS.md` experiments section

When a repository runs experiments, its `AGENTS.md` carries:

- a short convention block: the experiment root, the run id format, the version scheme and registry location, that `notes.md` is written before results are reported, and project-specific exceptions (legacy names, a second data root);
- the key decisions list, one or two lines each, for example:

```markdown
- [verified] Convert training data to Simplified Chinese; Traditional-Chinese training collapses. Runs: 20260915-train-script-simp-vs-trad-a1b2c3d.
- [unverified] Different prompts may avoid the Traditional-Chinese collapse. Source: model inference, not run. May be dropped any time.
```

## Organizing an existing repository

1. Inventory runs, scripts, data and version names wherever they are (log directories, scratch folders, training repos).
2. Propose a rename and move map (old path → new path) and show it to the human before moving anything. Search the repository for references to each old path and update them with the move. Do not rename deployed identifiers.
3. Backfill `notes.md` for existing runs from commit messages, docs, handoff notes and agent memory. Mark every reconstructed field as inference, with its source. List runs whose question or verdict cannot be reconstructed and ask the human; do not invent them.
4. Build `VERSIONS.md` from the versions found, recording legacy names.
5. Pull key decisions up into `AGENTS.md` and label each one. Audit the rules already there: a rule stated as fact but backed only by reasoning is relabeled `[unverified]` with its source; a verified one gets its run ids. Ask the human about decisions whose evidence cannot be found.
6. Leave large outputs in place when moving them is risky; record where they are in the run's `notes.md`.
