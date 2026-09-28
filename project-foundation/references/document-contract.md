# Project Document Contract

Use one canonical home for each kind of durable information. If the code or git history already shows it, do not write it down.

## `AGENTS.md` — how agents work in this repository

Keep it project-specific and compact.

Include only rules a coding agent cannot reliably infer from the repository, for example:

- required project language or reporting behavior when different from global defaults;
- important project-specific constraints and scope;
- build/test/verification commands and which ones are authoritative;
- release and delivery process;
- local environment facts that affect how agents work (services, ports, secrets handling), when they matter.

Do not copy the global agent instructions, architecture narrative or file inventories into it.

## `README.md` — what the project is

Include:

- purpose and major user-facing capability;
- minimal quick start for a human (prerequisites, setup, run) when useful;
- link to `DESIGN.md` when present;
- any information a human should see first.

Do not turn README into an architecture document.

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

- `DEVELOPMENT.md`: setup and commands go in `README.md` (for humans) or `AGENTS.md` (for agents).
- `docs/architecture.md` and code maps: module structure and data flow are read from the code.

## `docs/changes/`

Formal Atlas Planner/Relay task packages, dispatch plans and completion records live here when that workflow is used. They are work history, not project guidance; leave them in place.

## Other docs

Specs, changelogs and other long-lived documents that are not agent guidance can stay under `docs/`. Do not move files whose root location is required by tooling (for example LICENSE) merely to satisfy a layout.
