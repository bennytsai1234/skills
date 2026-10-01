# Cleanup: Repository Shape and Runtime Artifacts

The goal is a repository whose top level can be read in one glance and hosts that run only what is in use. Every file and every running artifact needs a current consumer; git history keeps what is removed from the repository.

## Repository shape

The top level holds only:

- `AGENTS.md`, an existing `README.md` (short, kept correct), ignore files and `.env.example`;
- files the toolchain requires at the root (`*.csproj`/`*.sln`, `package.json`, `pyproject.toml`, the application entry module, and similar);
- source, test, deploy, script and experiment directories.

Everything else moves into a directory or is deleted.

### Deploy targets

- One directory per deploy target: `deploy/<target>/` (for example `deploy/h200/`, `deploy/h100/`, `deploy/qwen3-asr-streaming/`). It holds that target's `Dockerfile`, `compose.yml`, run script, sidecar config and env example.
- Inside a target directory use the standard names (`Dockerfile`, `compose.yml`, `run.sh`). Do not encode variants in file suffixes such as `Dockerfile.H200.vllm-asr`; a real separate image is its own target directory.
- Two files that differ only in a few values become one file with build args or environment variables. Do not add a templating layer beyond that.
- The run script's defaults are the source of truth for the current image tag and model version; documents do not repeat them.

### Variants without a consumer

A Dockerfile, compose file, script or config is kept only if something current uses it: a run script, another build file, CI, a test, or the current deployment. A file referenced only by documents or work history, or by nothing, is deleted. Before deleting, search the repository for its name, and update or remove the references.

### Documents

The repository has no `docs/` directory. Harvest what is still useful from it, then delete it; git history keeps every removed file:

- working rules, gotchas and still-open residual risks go into `AGENTS.md`;
- verified decisions found in completion records or write-ups are pulled up into the `AGENTS.md` key decisions with their evidence (see `experiments.md`);
- tuning results, comparisons and proofs of concept become run records under the experiment root;
- target-specific deploy steps go into that target's run script comments or its `AGENTS.md` deploy section;
- behavior specs become tests (contract tests are the spec); keep a spec file only when an external tool or party requires it, and then next to its consumer;
- architecture tours, file maps, repository indexes and completed work records (`docs/changes/completed/`) are deleted, because the code and git log show them.

Atlas packages in `docs/changes/planning/` are a work queue while a dispatch is running; leave them until that dispatch finishes.

### Scripts

`scripts/` holds operational entry points that are still run. A one-off probe or benchmark belongs to the experiment run that used it (referenced from its `notes.md`, kept in code if it can be rerun) or is deleted.

### Untracked clutter

List untracked and ignored top-level entries with their size: stale tool caches (for tools no longer used), handoff bundles, old logs, downloaded models and wheels. Classify each as keep-ignored (still used; make sure `.gitignore` covers it), move out of the repository, or delete. Untracked files cannot be restored from git, so state that explicitly and delete only after the human confirms each item.

## Runtime artifacts on hosts

Running services accumulate containers, image tags, volumes and model weights. For each host the project deploys to:

1. Inventory the project's containers (running and stopped), images and tags, volumes, and model weight directories, with size, creation date and whether a running container uses them. Get host access facts from the host-specific skill or instructions; on shared hosts, list only this project's artifacts and never touch other users'.
2. Keep, per service: what is running now and one rollback version (the previous known-good). Everything else goes on a deletion list.
3. Show the deletion list with sizes and wait for the human's confirmation. Never delete an image, volume or weight directory that a running or rollback container uses.
4. New tags follow the version scheme in `experiments.md` (`<service>:<family>-v<N>`), so tag order is readable and matches `VERSIONS.md`. Tags already deployed keep their names.
5. Report what was removed and the space freed, and confirm the running services still pass their health and readiness checks.

## The `AGENTS.md` maintenance section

A cleanup only lasts if everyday work keeps the shape. Every repository this skill organizes gets a short maintenance section in `AGENTS.md`, filled in with that repository's actual top-level list, targets and hosts, and written in its working language. Keep it to these rules; it is loaded in every session, so it stays short:

```markdown
## Keeping the repository tidy

- Top level holds only <this repository's list>. New files go into an existing directory.
- Each deploy target lives in `deploy/<target>/` with `Dockerfile`, `compose.yml` and a run script. A new variant is a build argument or a new target directory, never a suffixed copy.
- Replacing something removes the old one in the same change: old build files, scripts, configs, and the references to them.
- No `docs/` documents: rules go here, results go into the run's `notes.md`, deploy steps go into the target's run script, behavior specs go into tests, work history goes into commit messages.
- Scratch files, downloads and handoff bundles stay outside the repository or in ignored paths, and are removed when the task ends.
- Deploying a new version keeps it plus one rollback per service; this project's older tags, stopped containers and unused weights on the host are listed and, after confirmation, removed as part of the same deployment.
- Before reporting a task done, check `git status` and the top level for new stray files.
```

Leave out lines that do not apply (for example the host rule in a repository that deploys nowhere) rather than keeping them as placeholders.

## Order of work

Repository shape first, runtime artifacts second: the run scripts define what is current, and that is what decides which host artifacts are kept. Present the full move/rename/delete map for both before changing anything, and apply only the groups the human approves.
