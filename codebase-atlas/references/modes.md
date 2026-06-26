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
- Small repositories naturally have fewer modules. Do not split modules just to
  create more files.
- Large monorepos may have more modules, but prefer product or domain
  boundaries over technical-layer boundaries.

## Reference-Assisted Mode

Use reference-assisted mode when the user provides a reference repository,
folder, docs, screenshots, product, API spec, or prior implementation.

The reference-template decision has three modes:

**A. No Reference**

Use the target repository as the only source of truth. Do not inspect or apply
external reference material.

**B. Partial Reference**

Use the reference only for the scope the user selected. Out-of-scope reference
features, flows, UI, architecture, or behavior are not relevant and must not be
treated as missing target functionality.

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

Do not use the reference to:

- Add unrelated features outside the selected mode.
- Force the target into the reference architecture unless explicitly requested.
- Treat out-of-scope reference features as bugs.
- Turn the reference into an open-ended backlog.

## Optional: Design System Mapping (format-only)

When a project has a real design system — a token source such as a CSS `:root`
block, a tokens file, or a theme config, plus component and visual rules — you may
optionally map it using `assets/templates/design.md`. That template is a generic,
opt-in scaffold in the google-labs-code/design.md two-layer format (YAML token
front-matter + prose rationale, canonical section order). This is **format-only**:
never install or run `@google/design.md` (its CLI / lint / export), so it stays
compatible with no-build, supply-chain-restricted environments.

Normativity follows the project's declared source of truth: if the project declares
its code/CSS/tokens canonical, the front-matter is a mirror regenerated when the
source changes; only if the project declares the design.md file canonical is it
normative. Record the design system like any other concern — as a normal module doc
and/or an index link — and keep project-specific layering (such as a per-page
override system) as preserved sections in the document, not as skill behavior. This
template is optional and never part of the required output shape.
