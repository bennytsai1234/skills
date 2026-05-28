# {{ATLAS_TITLE}} Change Workflow

## Role

This is an internal agent module routed by the main workflow.
The user does not need to know this workflow exists.

Use it internally for all code-changing tasks: bugs, features, optimizations,
refactors, releases, dependency upgrades, schema or data migrations,
configuration changes, hotfixes, and cleanups.

## Internal Reasoning Layer

Do not output this layer to the user.

1. Preserve the user's original request.
1. Receive the task and already-read index summary from the main workflow.
1. Choose the most relevant module docs for the task.
1. Internally classify the task into one of the supported task types and
   apply the type-specific reasoning hints listed under
   **Internal Task Types** below.
1. Calibrate scope internally so Before / After is accurate:
   - What will change.
   - What may be affected downstream.
   - Which boundaries remain uncertain.
1. Check whether the Decision Gate triggers apply (see below). If any trigger
   matches, use the Decision Gate format instead of the plain Before / After.
1. If the change is non-trivial — touches more than three files or crosses
   more than one module — write a short change plan to
   `docs/changes/<YYYY-MM-DD>-<slug>.md` before editing. The plan lists scope,
   chosen module entry points, expected file touches, validation steps, and
   rollback notes. This plan is engineering scratch and is not the user-facing
   confirmation.
1. Inspect code, tests, docs, configs, runtime paths, or reference material only
   when needed.

## Internal Task Types

Pick exactly one type. Each type names the kind of work, the minimum
verification expected before reporting completion, and what counts as a
rollback path. Verification commands are repository-specific — pick the ones
that exist in this project from `package.json`, `Makefile`, `CONTRIBUTING.md`,
CI configuration, or equivalent.

- **Bug**: current behavior is wrong or unstable.
  Investigation: before proposing a root cause for non-trivial bugs, use the
  structured bug investigation workflow below. This is required for
  intermittent, stateful, async, UI, cache, persistence, lifecycle, or
  race-condition issues.
  Verify: reproduction is gone; relevant tests pass; nearest integration test
  exercises the fixed path.
  Rollback: revert the patch; the bug returns but no other behavior changes.

### Structured Bug Investigation Workflow

Use this workflow before proposing a root cause for any non-trivial bug. The
goal is to avoid early convergence on the nearest symptom layer.

1. Classify the symptom:
   - Determine whether it is deterministic or intermittent.
   - Determine whether it is UI-only, state-related, persistence-related,
     async/timing-related, cache-related, lifecycle-related, or external
     dependency-related.
   - Name the exact user action, system event, or data input that triggers the
     bug, and the final state that is wrong.
1. Trace the user-action chain:
   - Start from the user-visible entry point.
   - Follow callbacks, coordinators, services, repositories, state machines,
     renderers, and persistence until the expected final state is reached.
   - Record the main path in concrete terms, for example:
     Entry -> Handler -> Coordinator -> State owner -> Renderer/Persistence.
1. Identify the state owner and target state:
   - Name the object or module that owns the affected state.
   - Identify the exact fields, records, cache entries, DOM/widgets, files, or
     network-visible outputs that should change.
   - Identify the observable outcome that proves the state changed correctly.
1. List all writers and restorers of the affected state:
   - Search for every code path that writes, restores, invalidates, saves,
     derives, or falls back to the same state.
   - Include indirect writers through listeners, post-frame callbacks, timers,
     animations, async completions, lifecycle hooks, observers, caches, and
     persistence restore paths.
1. List async boundaries and invalidators:
   - Await points, futures, streams, post-frame callbacks, listeners/notifiers,
     timers, animations, request ids, generation counters, stale-request
     guards, cancellation checks, cache invalidation, retries, and fallback
     logic.
   - For intermittent bugs, explicitly identify which operations can interleave
     and which stale operation can overwrite, cancel, or restore the wrong
     state.
1. Compare candidate root causes:
   - Produce at least two plausible causes unless the evidence makes only one
     possible.
   - Explain what supports and weakens each candidate.
   - Prefer the cause that explains the triggering timing, intermittency, and
     observed final state with the fewest assumptions.
1. Design the reproduction test:
   - For deterministic bugs, exercise the direct failing path.
   - For intermittent bugs, explicitly interleave the competing async
     operations or lifecycle events.
   - For UI/state bugs, assert both internal state and visible/rendered outcome
     when possible.
1. Only then propose the fix:
   - State the minimal code change.
   - Explain why it addresses the root cause instead of masking a symptom.
   - Identify the rollback path and the relevant verification commands.

- **Feature**: new behavior is requested.
  Verify: new tests cover the happy path and at least one failure path; build
  succeeds; type check passes.
  Rollback: feature flag or revert; existing behavior is unaffected.

- **Optimization**: behavior stays the same while quality improves.
  Verify: existing tests still pass; the targeted metric (latency, memory,
  bundle size, query count) is measured before and after.
  Rollback: revert; quality regresses to the prior baseline.

- **Refactor**: structure changes while intended behavior stays the same.
  Verify: full test suite passes; public APIs unchanged unless explicitly
  scoped in.
  Rollback: revert; behavior unchanged either way.

- **Release**: bump version, regenerate changelog, prepare tag.
  Verify: version manifest matches changelog entry; build artifacts produce
  cleanly; tag follows the project's existing convention.
  Rollback: drop the tag and revert manifest bump; release is unpublished.

- **Dependency**: upgrade, downgrade, replace, or remove a package.
  Verify: install or lock-file regeneration succeeds; build succeeds; targeted
  tests covering callers of the changed package pass; check changelog or
  release notes for breaking changes.
  Rollback: pin to the previous version and re-resolve.

- **Migration**: database schema, data, or storage migration.
  Verify: forward migration succeeds on a fresh copy of the data; reverse
  migration script exists or the irreversibility is recorded; one read and one
  write path are exercised after migration.
  Rollback: reverse migration script or restore from snapshot. Always escalate
  to Decision Gate.

- **Config**: environment variables, feature flags, infrastructure
  configuration, or runtime parameters.
  Verify: configuration loads in the affected environment; the dependent code
  path responds to the new value; secrets are not committed.
  Rollback: revert to the prior config value; restart or reload affected
  process.

- **Hotfix**: emergency fix for a live incident.
  Verify: minimum reproduction is gone; the rest of the test suite still
  passes on the patched branch; a follow-up task is noted for proper fix or
  post-mortem.
  Rollback: revert hotfix; incident returns. Prefer the smallest possible
  change surface.

- **Cleanup**: dead code removal, file consolidation, comment pruning, or
  unused asset deletion.
  Verify: build succeeds; full test suite passes; no references remain to
  removed symbols; user-facing behavior is unchanged.
  Rollback: revert; nothing is lost because there are no behavior changes.

If the task does not cleanly match one type, pick the closest and note the
deviation in internal reasoning. Do not invent new types.

## External Reporting Layer

1. If Decision Gate triggers matched, present the Decision Gate format first.
   Wait for the user to choose before continuing.
1. Confirm with the user using the Before / After format below.
1. Wait for explicit user confirmation before editing any files.
1. Write the change plan and commit it before touching source files:
   - Fill `assets/templates/change_plan.md` with the confirmed Before, After,
     task type, expected file scope, validation steps, and rollback path.
   - Save to `docs/changes/{{DATE}}-{{SLUG}}.md` (create `docs/changes/` if
     it does not exist).
   - Run `git add docs/changes/{{DATE}}-{{SLUG}}.md` and
     `git commit -m "plan: {{SLUG}}"`.
   - Do not edit any source files until this commit succeeds.
1. After the plan is committed, implement the change.
1. Run the minimum verification listed for the chosen task type. Include the
   verification result in the user-facing report. If verification fails, do
   not claim completion; either fix and re-verify, or report the failure
   honestly and ask the user how to proceed.
1. Validate the affected behavior and boundaries.
1. Finish with one plain-language sentence describing what changed and how it
   was verified.

## Reporting Rules

- Before / After is the only human confirmation interface.
- Reporting level for this project: {{REPORTING_LEVEL}}
  - Plain: do not expose module names, file paths, function names, or code
    snippets in user-facing reports.
  - Technical: include module names, file paths, and relevant code context in
    user-facing reports to help the developer locate changes.
- Keep internal reasoning separate from the user-facing summary.
- Verification status is part of the user-facing report regardless of
  reporting level: state plainly whether checks passed, were skipped, or
  failed.

## Before / After Format

**Before**: In one to three plain sentences, explain the current situation and
what is wrong, missing, or risky.

**After**: In one to three plain sentences, explain what will be true after the
change is complete.

Wait for explicit user confirmation before any file-editing operation.

## Decision Gate

The Decision Gate is an escalation from Before / After for changes with broader
impact. Use it when any of these triggers match:

- The change would alter module boundaries (create, remove, or merge modules).
- The change affects an external API contract or public interface.
- There are two or more viable approaches with different trade-offs.
- The change involves an irreversible operation (large-scale deletion, database
  migration, framework replacement, package downgrade with data loss).
- The internal task type is Migration or contains an irreversible step.

When triggered, present this format instead of the plain Before / After:

```markdown
## Decision: <one-sentence title>

### Context
Why this decision is needed.

### Options
A. <option A> — <advantages / costs>
B. <option B> — <advantages / costs>

### Impact
Which areas are affected and how.

### Recommendation
Which option is recommended and why.
```

After the user chooses, continue with a Before / After that implements the
chosen option. Record the decision:

- Cross-module decisions: add a row to the Architecture Decisions table in the
  index.
- Module-level decisions: add a note to the affected module's Known Risks or
  Do Not Do section.

## Atlas Update Conditions

Update affected atlas docs only when the change truly changes module
boundaries, ownership, or external APIs. Ordinary bug fixes and small features
do not require atlas updates.

When an update is needed, apply it incrementally:

1. Update only the affected module doc or docs.
2. If the module list or summaries in the index changed, update the index.
3. Do not rescan unrelated modules or regenerate workflow docs.
4. Note what changed and why in the report.

## Delivery Policy

{{DELIVERY_POLICY}}
