# Project Document Contract

Use one canonical home for each kind of durable information.

## `AGENTS.md` — how agents work in this repository

Keep it project-specific and compact.

Include only rules a coding agent cannot reliably infer from the repository, for example:

- required project language or reporting behavior when different from global defaults;
- important project-specific constraints/contracts;
- authoritative build/test/document pointers;
- project-specific delivery expectations;
- where the atlas index and key docs live.

Do not copy the global Agent philosophy, architecture narrative, environment tutorial, or every development command into it.

## `README.md` — what the project is

Include:

- purpose and major user-facing capability;
- minimal quick start when useful;
- links to DEVELOPMENT, DESIGN (if present), architecture (if present), and atlas index;
- any information a human should see first.

Do not turn README into the full architecture or engineering map.

## `DEVELOPMENT.md` — how to build/run/test locally

Include only current, actionable developer information:

- prerequisites/toolchain;
- setup;
- build/run/test commands;
- local DB/Redis/queue/services when applicable;
- ports and configuration entrypoints;
- local topology and debugging notes;
- how company/test/prod resources differ when that matters to development.

Keep secrets out of the repository. Move host-specific reusable operations to Skills when they are not part of ordinary project development.

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

## `docs/architecture.md` — optional high-level system structure

Create only when a separate cross-module view adds value.

Keep to:

1. System overview.
2. Critical runtime flows.
3. Data and state ownership.
4. External systems.
5. Deployment topology.

Do not copy module maps, file inventories, or work-history decisions into it.

## Codebase Atlas

Atlas files answer where code ownership lives and where a change should start. They are maintained by `codebase-atlas` and are not duplicated into the foundation docs.

## `docs/changes/`

Formal Atlas Planner/Relay task packages, dispatch plans, completion records, and summaries live here. They are work history, not architecture or foundation guidance.

## Other docs

Other long-lived project-specific documents belong under `docs/` when practical. Do not move files whose root location is required or conventional for tooling/ecosystem behavior (for example LICENSE or tool-discovered configuration) merely to satisfy a visual layout.
