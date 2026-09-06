# Codebase Atlas

Codebase Atlas builds a durable engineering navigation layer for a repository.

It creates only:

```text
docs/<project>_index.md
docs/<project>/<module_slug>.md
```

The index routes work between modules. Each module doc explains ownership, boundaries, dependencies, key flows, and useful change entry points. Live search still answers exact symbol/file questions.

Project foundation files (`AGENTS.md`, `README.md`, `DEVELOPMENT.md`, optional `DESIGN.md`, optional `docs/architecture.md`) are intentionally outside this skill. `project-foundation` owns that concern.

Ordinary development uses `atlas-fast`. Formal human-discussed planning uses `atlas-planner` -> `atlas-relay` -> `atlas-worker`. Codebase Atlas runs only when a human explicitly asks to build, refresh, rebuild, or repair the map.

## Modes

- **Initialize**: no atlas exists yet.
- **Refresh**: re-scan only repository areas changed since the recorded provenance commit.
- **Rebuild**: replace the map when provenance/boundaries are no longer reliable.
- **Reference-assisted**: optionally use a human-supplied reference within an explicitly selected scope.

See `references/atlas-contract.md` for the map contract and `references/quality-checklist.md` for validation.
