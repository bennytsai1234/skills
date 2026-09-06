# Atlas Contract

The atlas is a navigation map, not a workflow file or project-policy database.

Its job is to answer:

- what owns this area;
- where should future work start;
- what crosses the module boundary;
- which runtime/data flows matter inside the module;
- what repository-specific risks or invariants must not be missed.

Live search answers exact locations, call sites, and symbol inventories.

## Source of truth

Every atlas claim must be grounded in committed source/config/tests/manifests or persistent project documentation. Invocation-local facts such as the current model, shell session, temporary tool state, or chat decisions do not belong in the atlas.

If a persistent fact cannot be established, omit it or mark a real `TODO`.

## Scan boundaries

Ignore generated, vendored, dependency, cache, build, and VCS paths when inferring module ownership unless the human explicitly asks otherwise, including:

- `.git/`, `.hg/`, `.svn/`
- `node_modules/`, `vendor/`, `third_party/`
- `.venv/`, `venv/`, `env/`, `.tox/`
- `dist/`, `build/`, `out/`, `target/`, `.next/`, `.nuxt/`
- `coverage/`, `.cache/`, `.turbo/`, `.parcel-cache/`
- compiled/minified/binary artifacts that do not define source ownership

Generated code may be mentioned as downstream impact when relevant.

## Map layers

```text
index                -> route between modules
module doc           -> understand one module
live search / code   -> find exact implementation
```

Do not duplicate search-answerable detail into the map.

## Output shape

Standalone:

```text
docs/
  <project>_index.md
  <project>/
    <module_slug>.md
```

Reference-assisted:

```text
docs/
  <project>_<reference>_index.md
  <project>_<reference>/
    <module_slug>.md
```

Use lowercase snake_case slugs. All generated links/paths are relative and use forward slashes on every host OS.

## Format version

Current atlas format: `6`.

Format 6 removes workflow metadata, delivery/reporting settings, operating constraints, and architecture-decision storage from the index. Project rules live in project docs; work history lives in `docs/changes/`; the atlas stays a map.

Bump the format only when the generated map shape changes.

## Index requirements

Use `assets/templates/index.md`.

The index contains only:

- project/map purpose in one short paragraph;
- provenance: build/refresh date, source commit, atlas format;
- links to every module doc;
- routing-oriented module summaries.

It must not contain:

- delivery policy;
- reporting level;
- working-language policy;
- project operating rules copied from `AGENTS.md`;
- architecture decision logs;
- Planner/Relay/Worker process instructions;
- file/symbol inventories.

## Module requirements

Use `assets/templates/module.md`.

Each module doc contains:

- Responsibility;
- Scope — representative roots, APIs, entrypoints, commands, tests; not exhaustive inventory;
- Dependencies & Impact;
- Key Flows;
- Change Routes — where common work should start and what must move together;
- Risks & Boundaries — repository-specific fragile assumptions, contracts, invariants, or ownership limits.

A module boundary should approximate a stable change/ownership boundary. Prefer product/domain ownership over arbitrary technical-layer slicing when the repository supports that interpretation.

## Provenance

Index provenance format:

```text
Atlas built: <YYYY-MM-DD> · from commit <short-sha|not-a-git-repo> · format 6
```

Refresh rewrites provenance only after generated files pass validation.

## Refresh semantics

When the recorded commit is reachable, use changed source paths between that commit and `HEAD`. Exclude Scan Boundaries paths.

Classify modules:

- **stale** — owns changed source;
- **unmapped** — changed source belongs to no module;
- **removed** — the documented owned scope is gone;
- **untouched** — no relevant drift.

Re-scan stale modules only. Resolve unmapped source centrally. Leave untouched docs byte-identical. Remove docs only for confirmed removed modules. Update the index only when routing changed.

If provenance is missing/unusable or boundaries changed broadly, prefer rebuild after explaining the reason.

## Reference-assisted mode

A supplied reference can influence only the scope the human selected. The target repository remains the primary subject unless the human explicitly asks for full alignment. Reference details belong in module docs only when they help route or constrain work in that module.

## Non-goals

The atlas does not create or maintain:

- project foundation files;
- formal task packages or completion records;
- a general architecture document;
- deployment/runbooks;
- host credentials;
- session-specific workflow settings.
