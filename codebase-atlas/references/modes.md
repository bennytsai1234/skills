# Atlas Modes

## Standalone

Use the target repository as the source of truth.

Inspect existing project docs/rules, manifests, entrypoints, source roots, integrations, storage/jobs, and tests. Split modules by stable change ownership rather than a target count.

Small repositories naturally have fewer modules. Large repositories may have more, but avoid fragmenting one cohesive domain across many purely technical layers.

## Reference-assisted

Use only when the human supplied a reference repository, spec, design, screenshot set, or prior implementation.

Three scopes are possible:

- **No reference** — target repository only.
- **Partial reference** — use only the explicitly selected aspects.
- **Full alignment** — reference functionality is in scope only when the human explicitly asks for parity/alignment/compatibility/migration equivalence.

Understand target repository boundaries first. Then inspect the reference only where it helps the selected target modules. Do not turn out-of-scope reference features into defects or backlog items.
