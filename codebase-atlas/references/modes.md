# Modes

## Standalone Mode

Use standalone mode when the target repository is its own source of truth.

Inspect in this order:

1. Existing project docs and rules.
2. Manifests and package metadata.
3. Entrypoints, public APIs, app shells, binaries, routes, or service starts.
4. Source roots, domain folders, shared layers, integrations, storage, jobs,
   tooling, and tests.
5. Existing architecture or decision docs.

Split the project into stable modules. Judge the split by quality:

- Each module should be an independent change boundary, where future engineers
  can work without heavy cross-module coordination.
- Too many modules means the boundaries are too fragmented and most changes
  still cross several modules.
- Too few modules means the boundary is not meaningful and most work starts in
  the same place.
- Small repositories naturally have fewer modules. Module count follows change
  boundaries, not a target file count.
- Large monorepos may have more modules, but prefer product or domain
  boundaries over technical-layer boundaries.

## Reference-Assisted Mode

Use reference-assisted mode when the user provides a reference repository,
folder, docs, screenshots, product, API spec, or prior implementation.

The reference-template decision has three modes:

**A. No Reference**

Use the target repository as the only source of truth.

**B. Partial Reference**

Use the reference only for the scope the user selected. Out-of-scope reference
features, flows, UI, architecture, or behavior are simply not part of the target.

Examples of partial reference scope:

- Data-flow design only.
- UI structure only.
- Error-handling approach only.
- Diagnostics or testing pattern only.

**C. Full Alignment**

The target project must fully align with the reference's functionality. Enable
this only when the user explicitly asks for full alignment, parity,
compatibility, migration equivalence, or reference-driven expansion.

Rules for Partial Reference and Full Alignment:

- Understand the target repository first.
- Build the module split from target reality, not from the reference.
- Inspect the reference only after likely target modules are known.
- For each target module, record reference counterparts only when useful.
- Keep the target project as the primary subject unless Full Alignment
  explicitly makes reference functionality part of the target goal.

The target project stays the primary subject:

- The reference adds only what the selected mode calls for.
- Architecture follows the target's reality unless full alignment was requested.
- Out-of-scope reference features are out of scope, not defects.
- The reference stays bounded to the selected mode.
