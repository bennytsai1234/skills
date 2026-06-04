# {{ATLAS_TITLE}} Change Workflow

## Role

This is an internal agent module routed by the adapter's entry step.
The user does not need to know this workflow exists.

Use it internally for all code-changing tasks: bugs, features, optimizations,
refactors, releases, dependency upgrades, schema or data migrations,
configuration changes, hotfixes, and cleanups.

The disciplines this workflow uses (debugging, TDD, verification) live as
self-contained technique docs under `{{TECHNIQUES_DIR}}/` and are read on demand
— never inlined here. Read only the technique the current task calls for.

## Discipline Tiers

Open every task by judging how much discipline it warrants. Spend effort where
being wrong is expensive; do not apply heavy process to trivial work.

- **T0 — trivial:** no behaviour-logic change, reversible, single file (typo,
  comment, constant, obviously-safe one-liner). No debugging/TDD. One-line
  Before/After. Skip the plan file. Verify with the single most relevant
  check.
- **T1 — normal:** contained, reversible, diagnosis is clear. Light path: fix an
  obvious confirmed root cause; add one focused test when a cheap seam exists.
  Short plan as uncommitted scratch. Type-appropriate test subset.
- **T2 — hard / risky:** intermittent/async/stateful bug, multi-module, external
  API, irreversible, performance regression, or a diagnosis you are not sure of.
  Full discipline; usually triggers the Decision Gate; full verification.

**Hard floor:** any change that is irreversible, crosses more than one module,
alters an external API contract, or is a migration is **at least T2** regardless
of size — conditions that usually also trip the Decision Gate (multi-module work
that leaves boundaries intact may not).

**Control:** judge the tier automatically. If the user says "be quick" / "be
thorough" (or similar), honour that override — but never drop below the hard
floor.

## Internal Reasoning Layer

Do not output this layer to the user.

1. Preserve the user's original request.
1. Receive the task and the already-read index summary from the entry step.
1. Choose the most relevant module docs for the task.
1. **Judge the discipline tier** (T0/T1/T2) using the rules above.
1. Internally classify the task into one of the task types below and pull in the
   matching technique doc, scaled to the tier:
   - **Bug** → read and follow `{{TECHNIQUES_DIR}}/debugging.md` (T1 = light
     path, T2 = full feedback loop and ranked hypotheses).
   - **Behaviour-changing (feature / bugfix)** with a cheap test seam → read and
     follow `{{TECHNIQUES_DIR}}/tdd.md` (T0 skips).
   - **Refactor** → apply the refactoring note below.
1. Calibrate scope so Before/After is accurate: what will change, what may be
   affected downstream, which boundaries remain uncertain.
1. Check whether any Decision Gate trigger applies (see below). If so, use the
   Decision Gate before the plain Before/After.

## Internal Task Types

Pick exactly one type. Each names the work, the minimum verification expected
before claiming completion, and the rollback path. Verification commands are
repository-specific — pick the ones that exist in this project (`package.json`,
`Makefile`, `CONTRIBUTING.md`, CI config, or equivalent).

- **Bug**: current behaviour is wrong or unstable. Investigate via
  `{{TECHNIQUES_DIR}}/debugging.md` before proposing a root cause; this is
  mandatory at T2. Verify: the reproduction is gone; relevant tests pass.
  Rollback: revert the patch.
- **Feature**: new behaviour. Verify: new tests cover the happy path and one
  failure path; build and type check pass. Rollback: feature flag or revert.
- **Optimization**: same behaviour, better quality. Verify: existing tests pass;
  the targeted metric is measured before and after. Rollback: revert to the
  prior baseline.
- **Refactor**: structure changes, behaviour stays. Verify: full suite passes;
  public APIs unchanged unless explicitly scoped in. Rollback: revert.
- **Release**: version bump, changelog, tag. Verify: manifest matches changelog;
  artifacts build cleanly; tag follows the project convention. Rollback: drop
  the tag and revert the bump.
- **Dependency**: upgrade/downgrade/replace/remove a package. Verify: install or
  lockfile regeneration succeeds; build passes; tests covering callers pass;
  check release notes for breaking changes. Rollback: pin to the previous
  version.
- **Migration**: schema, data, or storage migration. Verify: forward migration
  succeeds on a fresh copy; a reverse script exists or irreversibility is
  recorded; one read and one write path are exercised after. Rollback: reverse
  script or restore from snapshot. **Always escalate to the Decision Gate.**
- **Config**: env vars, feature flags, infra config, runtime parameters. Verify:
  config loads in the affected environment; the dependent path responds; no
  secrets committed. Rollback: revert the value; reload the process.
- **Hotfix**: emergency fix for a live incident. Verify: the minimum
  reproduction is gone; the suite still passes on the patched branch; a
  follow-up task is noted. Rollback: revert; prefer the smallest change surface.
- **Cleanup**: dead code, consolidation, unused asset removal. Verify: build and
  full suite pass; no references remain to removed symbols; behaviour unchanged.
  Rollback: revert.

If the task does not cleanly match one type, pick the closest and note the
deviation internally. Do not invent new types.

### Refactoring note

When refactoring, aim for **deepening**: more behaviour behind a smaller, more
testable interface. Apply the **deletion test** to anything you suspect is a
shallow pass-through — imagine deleting it: if complexity vanishes it earned
nothing; if complexity reappears across its callers it was earning its keep.
Change structure, never behaviour, and keep the full suite green throughout.

## External Reporting Layer

1. If a Decision Gate trigger matched, present the Decision Gate format first
   and wait for the user to choose.
1. Confirm with the user using the Before / After format below.
1. Wait for explicit user confirmation before editing any files.
1. Record the plan, scaled to the tier — this is engineering scratch, not the
   user-facing confirmation. Plan files live in two folders: not-yet-implemented
   plans go in `docs/changes/planning/`, completed ones in
   `docs/changes/completed/`. `{{DATE}}` and `{{SLUG}}` are filled here per
   change; they are not initialization placeholders:
   - **T0:** skip the plan file.
   - **T1:** write `docs/changes/planning/{{DATE}}-{{SLUG}}.md` (create the
     folder if needed) with these fields — task type, the confirmed Before, the
     confirmed After, expected file scope, validation steps, and rollback path.
     Leave it as uncommitted scratch. Do not edit source files until it exists.
   - **T2:** write the same plan file (also under `docs/changes/planning/`). If
     the delivery policy allows commits (`commit only` / `commit and push`), run
     `git add docs/changes/planning/{{DATE}}-{{SLUG}}.md` and
     `git commit -m "plan: {{SLUG}}"` before editing source; under `no commit`,
     leave it uncommitted. Do not edit source files until the plan file exists.
1. Implement the change.
1. Verify by reading and following `{{TECHNIQUES_DIR}}/verification.md`, scaled
   to the tier. Include the verification result in the user-facing report. If
   verification fails, do not claim completion: fix and re-verify, or report the
   failure honestly and ask how to proceed.
1. Once verification passes and the change is truly complete, move the plan file
   from `docs/changes/planning/` to `docs/changes/completed/{{DATE}}-{{SLUG}}.md`
   (keep the same name; create the folder if needed). If this session produced
   only a plan without implementing it (e.g. the user deferred it, or it is a
   design-interview artifact), leave the plan in `docs/changes/planning/`.
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
- Verification status is part of the user-facing report regardless of reporting
  level: state plainly whether checks passed, were skipped, or failed.

## Before / After Format

**Before**: In one to three plain sentences, explain the current situation and
the diagnosed problem — what is wrong, missing, or risky, and your read of the
root cause. The user judges your diagnosis here; if it is shallow or wrong, this
is where they catch it.

**After**: In one to three plain sentences, explain what will be true after the
change, and how it will be verified.

Wait for explicit user confirmation before any file-editing operation.

## Decision Gate

The Decision Gate is an escalation from Before / After for changes with broader
impact. Use it when any trigger matches:

- The change would alter module boundaries (create, remove, or merge modules).
- The change affects an external API contract or public interface.
- There are two or more viable approaches with different trade-offs.
- The change involves an irreversible operation (large-scale deletion, database
  migration, framework replacement, package downgrade with data loss).
- The internal task type is Migration or contains an irreversible step.

When the decision involves several interdependent unresolved decisions or
unclear requirements — not a clean A/B — first resolve it by following
`{{TECHNIQUES_DIR}}/design-grilling.md`: interview one question at a time, each
with a recommended answer, exploring the atlas and code to answer where
possible. Then present the options below.

When triggered, present this instead of the plain Before / After:

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

After the user chooses, continue with a Before / After implementing the chosen
option. Record the decision:

- Cross-module decisions: add a row to the Architecture Decisions table in the
  index.
- Module-level decisions: add a note to the affected module's Known Risks or Do
  Not Do section.

## Atlas Update Conditions

Update affected atlas docs only when the change truly changes module boundaries,
ownership, or external APIs. Ordinary bug fixes and small features do not
require atlas updates.

When an update is needed, apply it incrementally:

1. Update only the affected module doc or docs.
2. If the module list or summaries in the index changed, update the index.
3. Do not rescan unrelated modules or regenerate workflow docs.
4. Note what changed and why in the report.

## Delivery Policy

{{DELIVERY_POLICY}}
