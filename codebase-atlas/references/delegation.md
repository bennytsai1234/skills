# Delegation

The doctrine the generated lead and worker adapters must carry. Read this when
generating adapters, and when deciding what belongs in each one.

The handoff is human-mediated. The lead never spawns the worker. There is no
dispatch, no concurrency, no scheduling.

## 1. The Loop

```text
Human      → states the need
Lead       1. understand the project and the need
           2. clarify the goal and acceptance evidence
           3. write the concise task package
Worker     4. explore the relevant code
           5. decide and make the change, across files as needed
           6. run the checks needed to prove acceptance
           7. report with evidence and risks
Lead       8. review: acceptance, diff, evidence, risks
           9. accept — or return precise gaps, nothing else
Worker    10. fix exactly the named gaps
Lead      11. final acceptance, then deliver to the human
```

Steps 3→4 and 7→8 cross a human. The lead writes a file and stops. The human runs
the worker and brings back the report and the diff.

## 2. Roles

**Lead** — the only agent in contact with the human. It owns:

- Understanding vague requests and aligning on intent.
- Reading the atlas and deciding what the change touches.
- Product decisions that cannot be inferred from the repository, and the Decision
  Gate.
- The Before / After gate.
- Writing the task package: goal, acceptance criteria, explicit constraints when
  needed, and evidence required.
- Reviewing the returned work and deciding accept-or-return.
- Every write to a governance file: atlas docs, plan files, completed folders,
  daily summaries, architecture decisions.
- Final acceptance and delivery.

**The lead never edits source code or tests.** No size exemption: a typo leaves
as a task package like everything else. There is no documented case in which the
lead may edit directly.

The lead may read code, run read-only checks, and re-run a verification whose
result decides acceptance. When one of those fails, it is a gap to return, not
something to fix.

**Worker** — a strong implementation agent, run by the human against one task
package. It owns:

- Exploring the codebase to find what the change requires. The package names
  starting points; it does not cap what may be read.
- Deciding the implementation from the goal, acceptance criteria, code, and
  explicit constraints.
- Editing across as many files as the change needs.
- Adding or extending tests when they are needed to establish acceptance.
- Running the checks needed to establish acceptance and fixing relevant failures;
  the worker owns the working tree for the duration of its task.
- Reporting with evidence: what was changed, what was run, what came back.

A worker never talks to the human as the project's voice, never writes a plan or
a summary, never updates the atlas, never commits or pushes, and never silently
violates an explicit constraint.

## 3. Role Resolution

Resolve the role from the instructions, not from the environment:

1. **Explicit header wins.** A prompt whose header declares `ROLE: worker` is a
   worker. `ROLE: lead` is a lead.
2. **No header → lead.**
3. **Governance write gate.** Before writing *any* governance file — an atlas
   doc, `docs/changes/planning/**`, `docs/changes/completed/**`, or an
   Architecture Decisions row — answer one question: *did my instructions come
   from a human turn, or from a task package?* If from a package, do not write.
   Report the needed change and let the lead write it.

**Single writer.** For any governance file, exactly one agent writes it: the
lead.

## 4. Task Package (`atlas/v2`)

The lead writes this to `docs/changes/planning/{{DATE}}-{{SLUG}}.md`. It is both
the plan file and the thing the human hands over — one artifact, not two.

Complete means: a competent agent that has never seen this conversation can read
this file, understand the desired result, find the code, choose an implementation,
and prove the result with evidence.

```markdown
---
ROLE: worker
CONTRACT: atlas/v2
TASK_TYPE: implement        # implement | investigate | review
---

## Goal
<one sentence: what must be true when this is done>

## Acceptance
- <exact command with its expected result, or an observable behaviour>
- <another objectively checkable result>
- <relevant tests or checks pass>

## Constraints (only when needed)
- <a requirement that cannot be inferred from the code or ordinary engineering
  judgement, such as API compatibility, schema ownership, dependency policy,
  component ownership, or deterministic verdict authority>
<omit this section when no explicit constraint exists>

## Starting Points (optional)
- docs/<project>/<module>.md
- <the symbol, route, or entrypoint that may help orient exploration>
<omit this section when no useful pointer is available>

## Evidence
- The actual output for each Acceptance check, pasted rather than summarized.
- The tests and other checks run, plus any remaining risks.
```

Do not add generic rules such as "preserve existing functionality", "use a
reasonable architecture", or "maintain code quality". Add a constraint only when
it records a real requirement that the worker cannot infer from the repository or
ordinary engineering judgement.

**Acceptance rules.** Every acceptance item must be checkable by someone who was
not in the conversation — an exact command with an expected result, or an
observable behaviour described precisely enough to disagree with. "Works
correctly" is not an acceptance criterion.

**Command rules.** Write commands for the shell the worker will get. One command
per line, never an `&&` chain — Windows PowerShell 5.1 has no `&&`. On a Windows
host also avoid inline environment prefixes (`NODE_ENV=test cmd`), `2>/dev/null`,
and POSIX utilities assumed on `PATH`. Prefer the project's own runner
(`npm test`, `pytest tests/auth -q`, `dotnet build`). Paths stay relative with
forward slashes, on every host.

**Never** paste chat history, the index, or a full spec into a package. Do not
prescribe the implementation when the worker can determine it from the goal and
the code.

## 5. Worker Report Format

```markdown
## Changed
- <file>: <what changed and why — one line each>

## Verification
- <command>
  <the actual output, pasted — not "passed">
- <tests/checks run for Acceptance and their actual output>

## Risks
- <what could still be wrong, what was not covered, what is worth watching>
- <or: none>

## Needs A Decision
- <or: none>
```

Evidence is pasted output, never a claim about output. No exploration narrative
or restatement of the task is needed.

## 6. Review And Return

The lead reviews the package it wrote, the report, and the diff, in this order:

1. **Requirement conformance.** Does the change do what `Goal` asked, and does
   every `Acceptance` item hold? Verify against the pasted evidence, and re-run
   anything whose result decides acceptance.
2. **Diff.** Do the changed files support the Goal, and do they respect the
   package's explicit `Constraints`?
3. **Verification.** Do the reported checks establish the Acceptance items, and
   are the remaining risks stated honestly?

Everything found at this step is a gap, including a check that fails on re-run.
The lead does not fix it.

**Returning.** A return names gaps and nothing else. Do not re-explain the task,
do not restate the goal, do not re-send the package.

```markdown
## Gaps
1. <file:line> — <what is wrong, and what "fixed" looks like>
2. <...>

Everything else is accepted. Change nothing outside these points.
```

The final line is required.

Return at most twice. On a third round, withdraw the package, fix the
specification, and reissue.

## 7. Cost And Context Discipline

- **While the package is out, do nothing.** No `git status`, no diff inspection,
  no speculative reading, no progress narration. Wait for the human to bring back
  the report.
- **Specify once, completely.** Spend the effort on making `Acceptance`
  checkable, before the handoff.
- **Do not re-read what you already concluded.** Carry conclusions forward across
  steps rather than re-reading the index at review time.
- **Batch the review.** Review once against the whole returned change, and issue
  one list of gaps.
