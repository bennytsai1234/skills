# Project Document Contract

Use one canonical home for each kind of durable information. If the code or git history already shows it, do not write it down.

## `AGENTS.md` — how agents work in this repository

Keep it project-specific and compact.

Include only rules a coding agent cannot reliably infer from the repository, for example:

- required project language or reporting behavior when different from global defaults;
- important project-specific constraints and scope;
- build/test/verification commands, which ones are authoritative, and their non-obvious prerequisites;
- release and delivery process;
- local environment facts that affect how agents work (services, ports, secrets handling), when they matter.

A rule that came from experiments states the instruction in one or two lines and names the run id(s) or commit behind it; the question, setup, evidence and verdict live only in the run's `notes.md`. When the repository runs experiments, include the experiments section described in `experiments.md`.

Do not copy the global agent instructions, architecture narrative, file inventories or deployment status into it.

## Experiment root — run records and version registry

Layout, naming, versioning and the `notes.md` format are in `experiments.md`. Run records are the source of experiment knowledge; do not write a separate lessons or findings document that restates them.

## `DESIGN.md` — visual/product design system

Create only for products with a real UI/design system.

Useful sections may include:

- overview / visual identity;
- colors/tokens;
- typography;
- layout/spacing;
- shapes/elevation;
- recurring components;
- interaction/motion/responsive conventions when they are actually defined;
- do/don't guidance that helps coding agents make consistent UI decisions.

Prefer concrete rules and rationale over adjectives such as "modern" or "premium" alone.

## Not created

- `README.md`: not created. An existing one is the human's entry point: keep it short, correct stale facts, and do not move agent rules into it.
- `CLAUDE.md`: Claude Code loads `AGENTS.md` on its own (verified 2026-10-01 on 2.1.286 with no `CLAUDE.md` present). Fold an existing `CLAUDE.md` into `AGENTS.md` and remove it; a rule that applies to Claude Code alone goes in its own `AGENTS.md` section.
- `DEVELOPMENT.md`: setup and commands go in `AGENTS.md`.
- `docs/` in any form: architecture docs, code maps, topic write-ups, specs, changelogs and completed work records. Harvest and remove them as described in `cleanup.md`.

## Where other content goes

- Something a test, assertion or config check can enforce, including behavior specs: put it there, not in a document.
- Current deployment or health status: not documented, because it changes; verify it live.
- Experiment questions, setups, results and verdicts: the run's `notes.md`.
- Work history and completion records: git commit messages.
- A file an external tool or party requires: next to its consumer, not under `docs/`. Do not move files whose root location is required by tooling (for example LICENSE) merely to satisfy a layout.

## Atlas work queue

While an Atlas dispatch is running, its packages and dispatch plan under `docs/changes/planning/` are a work queue that Relay and Worker read. Leave them in place until the dispatch finishes; they are not guidance and are not kept afterwards.
