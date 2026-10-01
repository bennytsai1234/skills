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
2. Keep, per service: what is running now, plus anything a current build or on-demand start still uses (an overlay's base image, a stopped container a supervisor starts when needed). No rollback copies by default: these are small internal services where a failure gets fixed forward. Keep a rollback only when the project's `AGENTS.md` asks for one. Everything else goes on a deletion list.
3. Show the deletion list with sizes and wait for the human's confirmation. Never delete an image, volume or weight directory that a running container, a current build or an on-demand start uses.
4. One fixed tag per service, named after the service and target (for example `aistt-agent:h200`); every deploy overwrites it. Delete date, commit-hash, `pre-*`, `refresh-*` and numbered tags. Model and data versions live in the run script's environment and `VERSIONS.md`, not in image tags.
5. Also list host-side leftovers: backup files (`*.bak*`, `*.orig`, `*-backup*`), transfer tarballs and staging directories named by commit hash or date, test audio dropped in the deploy root, and the user's trash folder.
6. Report what was removed and the space freed, and confirm the running services still pass their health and readiness checks.

## The `AGENTS.md` maintenance section

A cleanup only lasts if everyday work keeps the shape. Every repository this skill organizes gets a short maintenance section in `AGENTS.md`, filled in with that repository's actual top-level list, targets and hosts, and written in its working language. Keep it to these rules; it is loaded in every session, so it stays short:

```markdown
## Keeping the repository tidy

- Top level holds only <this repository's list>. New files go into an existing directory.
- Each deploy target lives in `deploy/<target>/` with `Dockerfile`, `compose.yml` and a run script. A new variant is a build argument or a new target directory, never a suffixed copy.
- Replacing something removes the old one in the same change: old build files, scripts, configs, and the references to them.
- No `docs/` documents: rules go here, results go into the run's `notes.md`, deploy steps go into the target's run script, behavior specs go into tests, work history goes into commit messages.
- Scratch files, downloads and handoff bundles stay outside the repository or in ignored paths, and are removed when the task ends.
- Deploying a new version overwrites the service's fixed tag and keeps nothing else (no rollback copies); this project's leftover tags, stopped containers and unused weights on the host are listed and, after confirmation, removed as part of the same deployment.
- Text files are LF (`.gitattributes` and `.editorconfig` enforce it). Code that writes files on Windows passes `newline="\n"`. Before copying anything to a Linux host, `git ls-files --eol | grep w/crlf` must print nothing.
- Before reporting a task done, check `git status` and the top level for new stray files.
```

Leave out lines that do not apply (for example the host rule in a repository that deploys nowhere) rather than keeping them as placeholders.

Every repository also gets `.gitattributes` (`* text=auto eol=lf`, with `*.bat`/`*.cmd` as `eol=crlf`) and `.editorconfig` (`end_of_line = lf`). When adding them, convert working-tree files that are still CRLF and run `git add --renormalize .`; with non-ASCII paths, list files with `git -c core.quotepath=off ls-files --eol`.

## The `AGENTS.md` delivery workflow (addressed to GPT／Codex)

Observed in practice, GPT／Codex agents deliver by accumulation: a new image tag per deploy (`pre-*`, `refresh-<date>`), `*.bak-<date>` copies of scripts and data on hosts, transfer tarballs and staging directories named by commit hash, per-file SHA-256 manifests and byte-level disk projections, completion-record documents and docs-only commits, one copied script per model version, test audio in the deploy root, and long restated reports. Prohibitions alone do not fix this; a clean default workflow does, because following it leaves nothing behind.

Every repository this skill organizes gets the section below in `AGENTS.md`, under a heading that names GPT／Codex explicitly so those agents see it is addressed to them, written in the repository's working language and filled in with the repository's real tags, paths, hosts and smoke sample. All agents follow it.

```markdown
## Delivery workflow (for GPT／Codex; all agents follow it)

Each step has a fixed name and a fixed place, so a deploy overwrites what was there and leaves nothing behind.

1. Source is a commit. Commit first, then package with `git archive HEAD`, not from the working tree; the content is exactly what was committed and line endings are LF.
2. Fixed staging. Each target has one staging directory on the host (`<deploy root>/staging/<target>/`). Empty it, unpack, build, empty it again.
3. Fixed tag. Each service has one tag named after it (`<service>:<target>`); the build overwrites it. Dockerfiles carry `LABEL project=<project>`, so after the deploy `docker image prune -f --filter label=project=<project>` removes the layers the overwrite left dangling, without touching other users' images.
4. Stream images. Move images with `docker save <tag> | gzip | ssh <host> 'gunzip | docker load'`: no tarball lands anywhere. Only an offline target that cannot be reached gets a delivery directory, at one fixed path, overwritten by the next package.
5. Versions live in configuration. Model and recipe versions are environment variables of the run script plus a row in `VERSIONS.md`. Switching weights: put the new directory next to the old one, change the variable, recreate the container, delete the old directory.
6. Acceptance is three checks: the container is healthy, the service's own readiness endpoint answers, and the fixed smoke sample (`<smoke sample path>`) transcribes once on each changed engine. Integrity is the tools' job: `docker load` verifies every layer digest and `gzip -t` checks an archive, so no SHA manifest or disk projection is added.
7. History lives in git. Code history is git; data the service maintains (term lists, caches) lives in the persistent data volume that deploys do not overwrite. So no backup copies are made; a temporary copy needed mid-operation is deleted in the same step.
8. One script per job. A new model version is a new parameter value of the existing script, not a copied `build_vN.py`.
9. Records: the commit message says what changed and how it was verified; a lasting rule goes into this file; an experiment result goes into its run's `notes.md`. Probes and test audio live in that run, not in the deploy root.
10. Report in three short parts: what changed, what was verified, what is still pending. No restating the scope, no step-by-step narration.
```

Drop steps that cannot apply (for example image steps in a repository that builds no images) rather than keeping placeholders.

## Order of work

Repository shape first, runtime artifacts second: the run scripts define what is current, and that is what decides which host artifacts are kept. Present the full move/rename/delete map for both before changing anything, and apply only the groups the human approves.
