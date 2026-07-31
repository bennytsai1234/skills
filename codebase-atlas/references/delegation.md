# Delegation

The doctrine the generated lead and worker adapters must carry. Read this when
generating adapters, and when deciding what belongs in each one.

**The handoff is human-mediated. The lead never spawns the worker.** The lead
understands the project and the need, decides the solution boundary, agrees it
with the human, and writes a complete, acceptance-testable **task package** to a
file. The human carries that file to a strong implementation agent. That agent
explores the code on its own, designs and makes the change across whatever files
it needs, writes and runs tests until they pass, and reports back with evidence.
The human brings the result back, and the lead reviews it.

Nothing in this document describes automated dispatch. There is no spawn, no
concurrency, no scheduling. The unit of delegation is a file a person copies.

That premise decides everything else. The worker is not a cheap executor being
kept on a short leash — it is a capable agent given a well-specified problem, and
the lead's leverage is entirely in how well the package is written. A vague
package cannot be rescued downstream, because the lead is not there.

## 1. The Loop

```text
Human      → states the need
Lead       1. understand the project and the need
           2. decide the solution boundary
           3. write the acceptance-testable task package
Worker     4. explore the relevant code
           5. design and make the change, across files as needed
           6. add tests, run them, fix failures until green
           7. report with evidence and risks
Lead       8. review: requirement conformance, architecture, diff, tests
           9. accept — or return precise gaps, nothing else
Worker    10. fix exactly the named gaps
Lead      11. final acceptance, then deliver to the human
```

Steps 3→4 and 7→8 cross a human. The lead writes a file and stops; the human
runs the worker; the human brings back the report and the diff. The lead's next
turn begins from what it is given, not from a poll.

## 2. Roles

**Lead** — the only agent in contact with the human. It owns:

- Understanding vague requests and aligning on intent.
- Reading the atlas and deciding what the change touches.
- Architecture and product decisions, and the Decision Gate.
- The Before / After gate.
- Writing the task package: scope, boundaries, acceptance criteria, evidence
  required.
- Reviewing the returned work and deciding accept-or-return.
- Every write to a governance file: atlas docs, plan files, completed folders,
  daily summaries, architecture decisions.
- Final acceptance and delivery.

The lead does not write production code as part of this loop. If the human asks
it to make a small edit directly, that is the human's call to make, not a
shortcut the lead takes on its own.

**Worker** — a strong implementation agent, run by the human against one task
package. It owns:

- Exploring the codebase to find what the change actually requires. The package
  names starting points; it does not cap what may be read.
- Designing the implementation within the boundary the package sets.
- Editing across as many files as the change genuinely needs.
- Adding or extending tests, running them, and fixing failures until they pass.
- Running builds, suites, linters, and type checks — it owns the working tree for
  the duration of its task.
- Reporting with evidence: what was changed, what was run, what came back.

A worker never talks to the human as the project's voice, never writes a plan or
a summary, never updates the atlas, never re-opens a decision the package
already settled, and never silently steps outside the package's scope.

## 3. Role Resolution

Neither platform exposes a reliable signal for "am I the implementation agent."
Resolve the role from the instructions:

1. **Explicit header wins.** A prompt whose header declares `ROLE: worker` is a
   worker. `ROLE: lead` is a lead.
2. **No header → lead.** Direct conversation with a human is the default, so the
   Before / After gate is never silently skipped.
3. **Governance write gate (the safety net).** Before writing *any* governance
   file — an atlas doc, `docs/changes/planning/**`, `docs/changes/completed/**`,
   or an Architecture Decisions row — answer one question: *did my instructions
   come from a human turn, or from a task package?* If from a package, do not
   write. Report the needed change and let the lead write it.

Rule 3 is what makes rule 2 safe. A worker handed a package without a header
still reasons like a lead, but is blocked at the only place a misjudged role does
lasting damage — the shared documents.

**Single writer.** For any governance file, exactly one agent writes it: the
lead. Two agents appending to the same daily summary is how the summary becomes
wrong.

## 4. Task Package (`atlas/v2`)

The lead writes this to `docs/changes/planning/{{DATE}}-{{SLUG}}.md`. It is both
the plan file and the thing the human hands over — one artifact, not two.

Complete means: a competent agent that has never seen this conversation can read
this file, find the code, make the change, and prove it worked. It does not mean
long. It means no gap the worker would have to guess across.

```markdown
---
ROLE: worker
CONTRACT: atlas/v2
TASK_TYPE: implement        # implement | investigate | review
---

## Goal
<one sentence: what must be true when this is done>

## Why
<the need behind it, and for a bug the diagnosed root cause. Enough that the
worker can tell a correct fix from one that merely satisfies the letter of the
goal. Not chat history.>

## Solution Boundary
<what was decided and what was ruled out — the approach chosen, the approaches
rejected and why. The worker designs inside this; it does not re-litigate it.>

## Starting Points
- docs/<project>/<module>.md
- <the symbol, route, or entrypoint the change most likely begins at>
<orientation, not a reading limit. Explore whatever the change requires.>

## Scope
- Expected to change: <areas>
- Out of bounds: <areas that must not change>
<if the real fix turns out to lie outside this, stop and report — do not widen>

## Must Preserve
- <architecture boundary, public API, or contract that must not change>

## Forbidden
- <task-specific bans, on top of the baseline catalogue in §5>

## Acceptance
- <check 1: an exact command with its expected result, or an observable behaviour>
- <check 2>
- Old behaviour that must not change: <...>

## Tests
- <what must be covered, and where those tests live>
- <or: no new test — and why the existing coverage is sufficient>

## Evidence Required
- The command output for each Acceptance check, pasted, not summarized.
- The full test-suite result.

## Stop And Report If
- The root cause turns out to be outside Scope.
- The fix requires changing something under Must Preserve.
- Two or more viable approaches differ materially in trade-offs.
- The package rests on a premise the code contradicts.
```

`Must Preserve` and `Forbidden` are usually free to write: copy them from the
owning module doc's **Do Not Do** and **Known Risks** sections. That is what
those sections are for.

**Acceptance is the whole contract.** The lead is not present while the work
happens and cannot correct course. Every acceptance item must be checkable by
someone who was not in the conversation — an exact command with an expected
result, or an observable behaviour described precisely enough to disagree with.
"Works correctly" is not an acceptance criterion.

**Commands must run in the shell that will run them.** Write them for the shell
the worker will actually get, not the POSIX one it is tempting to assume. One
command per line, never an `&&` chain — Windows PowerShell 5.1 has no `&&`, and a
syntax error comes back as a check that never ran. On a Windows host also avoid
inline environment prefixes (`NODE_ENV=test cmd`), `2>/dev/null`, and POSIX
utilities assumed on `PATH`. Prefer the project's own runner (`npm test`,
`pytest tests/auth -q`, `dotnet build`); it behaves the same everywhere. Paths
stay relative with forward slashes, on every host.

## 5. Forbidden Implementation Patterns

The worker carries this baseline. "Do not patch" is too abstract to enforce;
these are checkable, and the lead checks them against the diff at review.

- Do not add a special case, hardcoded value, or skipped assertion to make a
  check pass.
- Do not catch and swallow an exception to make a symptom disappear.
- Do not copy existing logic to a second location — find the existing
  abstraction first.
- Do not add a production branch that exists only for tests
  (`if TEST`, `NODE_ENV === 'test'`, …).
- Do not repair an upstream problem at a downstream layer.
- Do not introduce new global state, or a wrapper that adds no capability.
- Do not weaken, delete, or rewrite an existing test to make it pass.
- Do not change a public API, schema, or wire contract unless the package
  explicitly allows it.
- Do not add a dependency unless the package explicitly allows it.
- Do not edit outside `Scope`.

**Root-cause preflight.** Before editing, the worker answers three questions
internally and puts the answer in one line of its report:

1. What actually causes this, and at which layer?
2. Is there an existing abstraction that already handles it?
3. Will this fix put the same logic in a second place?

If the honest answer to (1) points outside `Scope`, stop and report — that is the
case *Stop And Report If* exists for.

**Green is not done.** A passing suite proves nothing was broken; it does not
prove the goal was met. Check the change against `Goal` and `Acceptance`
directly, not through the test result.

## 6. Worker Report Format

Short, structured, and evidenced. The lead reads this instead of re-deriving the
work — but the lead also reads the diff, so the report does not need to restate
it.

```markdown
## Changed
- <file>: <what changed and why — one line each>

## Approach
<two or three lines: the design chosen inside the package's boundary, and any
place the code required something different from what the package assumed>

## Root Cause
<one or two lines: what caused it, and why this layer is the right place to fix it>

## Verification
- <command>
  <the actual output, pasted — not "passed">
- Full suite: <command> → <result>

## Risks
- <what could still be wrong, what was not covered, what is worth watching>
- <or: none>

## Needs A Decision
- <or: none>
```

No exploration narrative. No self-assessment paragraphs. Evidence is pasted
output, not a claim about output — a claim is exactly what review exists to
check, so it cannot also be the thing reviewed.

## 7. Review And Return

The lead reviews what came back. It has the package it wrote, the report, and the
diff — everything needed, without re-deriving the work.

Check, in this order:

1. **Requirement conformance.** Does the change do what `Goal` asked, and does
   every `Acceptance` item actually hold? Verify against the pasted evidence, and
   re-run anything whose result decides acceptance.
2. **Architecture.** Does the change fit the module boundaries in the atlas? Did
   it put logic where that module's doc says logic belongs? Is anything under
   `Must Preserve` altered?
3. **Diff.** Did it stay inside `Scope`? Does it contain any pattern from §5? Is
   the new code more complex than the problem it solves? Are there side effects
   the report did not mention?
4. **Tests.** Do the new tests assert real behaviour, or do they encode the
   implementation's mistake? Would they fail if the bug came back?

**Returning.** A return names gaps and nothing else. Do not re-explain the task,
do not restate the goal, do not re-send the package — the worker has it. Write
the smallest amendment that closes the gap:

```markdown
## Gaps
1. <file:line> — <what is wrong, and what "fixed" looks like>
2. <...>

Everything else is accepted. Change nothing outside these points.
```

The last line matters. Without it, a capable agent asked to fix two things will
often improve five, and the review starts over.

Return at most twice. A third round means the package was wrong, not the work —
withdraw it, fix the specification, and reissue.

## 8. Cost And Context Discipline

The lead is alive across the whole loop, and its context only grows. That is
where the money goes.

**While the package is out, do nothing.** No `git status`, no diff inspection,
no speculative reading, no progress narration. The work is happening in another
process that will report when it is done, and "not finished yet" is the entire
content of anything a check could return. Each idle turn re-sends the lead's
whole growing context to buy that non-answer.

**Specify once, completely.** The lead's one shot at influencing the outcome is
the package. Time spent making `Acceptance` checkable is the cheapest spend in
this loop; every round trip after that costs a human's attention as well as
tokens.

**Never paste chat history, the index, or a full spec into a package.** `Why` and
`Solution Boundary` are a handful of lines each. `Starting Points` orient the
worker; they do not brief it.

**Do not re-read what you already concluded.** Carry conclusions forward across
steps. Re-reading the index at review time to re-establish what a module owns is
paying twice for one fact.

**Batch the review.** Review once, against the whole returned change, and issue
one list of gaps. Reviewing partially and returning twice doubles the human's
involvement, which is the scarcest resource in this loop.
