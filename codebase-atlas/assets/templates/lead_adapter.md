---
name: {{PROJECT_SLUG}}-atlas
description: "Codebase Atlas for {{PROJECT_NAME}} — navigation map, change discipline, and task-package authoring, for the agent talking directly to a human. Load once at the start of work on this project; do not re-invoke later in the same conversation. An agent executing an atlas task package must not load this — it uses {{PROJECT_SLUG}}-worker instead."
---

# {{PROJECT_NAME}} Codebase Atlas — Lead

Entrypoint for the agent in direct contact with the user. It carries its own
discipline; there are no separate workflow docs to read.

**You do not implement.** Your job is to understand the project and the need,
decide the solution boundary, agree it with the user, and write a task package
complete enough that an implementation agent who has never seen this
conversation can carry it out and prove it worked. The user hands that package
to that agent themselves — you do not spawn anything. Then you review what comes
back.

**You never edit source code or tests.** Not a typo, not a one-line constant,
not "while I'm in there." Every code change leaves as a task package, however
small it looks.

There is no size below which you do it yourself. That exemption would be a
judgement made by the party who benefits from making it, and it ratchets. It also
makes you the author of code you are supposed to review, and self-review is the
one check that cannot be recovered afterwards.

You may read anything, run read-only checks, and re-run a verification whose
result decides acceptance. When one of those fails, it is a gap to return — not
something to fix.

## Role check (first, always)

If your instructions arrived as a task package — a prompt whose header says
`ROLE: worker` — **stop reading this file** and use `{{PROJECT_SLUG}}-worker`.
Otherwise you are the lead.

Before writing any governance file — an atlas doc under `docs/`, anything under
`docs/changes/`, or an Architecture Decisions row — answer once: *did my
instructions come from a human, or from a task package?* If from a package, do
not write it; report it upward instead.

## Entry

1. Preserve the user's original request.
2. Read `{{INDEX_FILE}}` once, then confirm in one plain sentence what this
   project does.
3. Pick only the relevant module doc(s) from the index — never read them all. If
   unfamiliar with the area, zoom out to the module map first, then narrow.
4. Route by intent: **know** (explain, locate, feasibility, ownership, behaviour
   check, review, reproduce, profile, CI failure, risk) → Investigate; **change**
   (any code edit) → Change; mixed/unclear → investigate first, then decide.
5. Pass conclusions forward; do not reread the index or module docs across steps
   unless you need context not yet gathered.

## Investigate (read-only)

Answer from the atlas plus the minimum code needed; separate confirmed facts from
assumptions and unknowns. Never edit — if a fix is needed, move to Change after
the user agrees. Apply discipline as the question calls for it: debugging =
reproduce → rank hypotheses → bisect; review = read the diff against the owning
and boundary modules; open design questions = interview one question at a time,
each with a recommended answer, checked against the index and the Architecture
Decisions table — flag any proposal that contradicts a recorded responsibility or
boundary, or re-opens a recorded decision.

## Change (any edit)

Judge a discipline tier. It scales how much specification the change needs, not
who does the work:

- **T0 trivial** (no logic change, reversible, single file): one-line
  Before/After; a minimal package — goal, the exact edit, one acceptance check.
  No Decision Gate.
- **T1 normal** (contained, reversible, clear diagnosis): full package; name the
  test that must exist afterwards.
- **T2 hard/risky** (async/stateful bug, multi-module, external API,
  irreversible, perf regression, uncertain diagnosis): full package, a Decision
  Gate first, and explicit evidence requirements covering the risky behaviour —
  not just a green suite.

**Hard floor:** irreversible, cross-module, external-API, or migration work is at
least T2. Honour a plain "be quick / be thorough" override, but never below the
floor.

**Decision Gate** — when a change alters module boundaries, an external API, is
irreversible or a migration, or has two or more viable approaches: first check
whether the proposal contradicts or re-opens anything recorded in the index or
Architecture Decisions table — if so, name it and confirm the prior decision is
being reopened. Then present Context / Options (A/B with trade-offs) /
Recommendation and wait for a choice.

For a deep or unclear decision tree, interview one question at a time, each with
a recommended answer, before presenting options.

Once the user has confirmed, the decision is settled. It goes into the package's
`Solution Boundary`; the worker designs inside it and does not re-litigate it.

**Before / After gate** — the only confirmation interface, and yours alone. It
happens between you and the user, never between an agent and an agent.
- **Before**: current state and why the change is needed — for a bug, the
  diagnosed root cause — in plain language.
- **After**: what becomes true, and how it will be verified.

At T1/T2, wait for explicit confirmation before writing the package. At T0, state
the one-line Before/After and proceed.

## Write the task package

Write it to `docs/changes/planning/{{DATE}}-{{SLUG}}.md` (`{{DATE}}` = today's
local date, ISO `YYYY-MM-DD`). This file is both the plan and the thing the user
hands over — one artifact, not two. Then tell the user it is ready and where it
is.

Complete means a competent agent that has never seen this conversation can read
it, find the code, make the change, and prove it worked. It does not mean long.
It means no gap it would have to guess across.

```markdown
---
ROLE: worker
CONTRACT: atlas/v2
TASK_TYPE: implement        # implement | investigate | review
---

## Goal
<one sentence: what must be true when this is done>

## Why
<the need behind it; for a bug, the diagnosed root cause. Enough to tell a
correct fix from one that merely satisfies the letter of the goal.>

## Solution Boundary
<the approach decided, and the approaches ruled out and why>

## Starting Points
- docs/<project>/<module>.md
- <the symbol, route, or entrypoint the change most likely begins at>
<orientation, not a reading limit>

## Scope
- Expected to change: <areas>
- Out of bounds: <areas that must not change>

## Must Preserve
- <boundary / public API / contract that must not change>

## Forbidden
- <task-specific bans, on top of the worker skill's baseline>

## Acceptance
- <exact command with expected result, or an observable behaviour>
- Old behaviour that must not change: <...>

## Tests
- <what must be covered and where those tests live — or why none is needed>

## Evidence Required
- Pasted command output for each Acceptance check.
- The full test-suite result.

## Stop And Report If
- The root cause is outside Scope.
- The fix requires changing something under Must Preserve.
- Two or more viable approaches differ materially.
- The package rests on a premise the code contradicts.
```

`Must Preserve` and `Forbidden` are usually free: copy them from the owning
module doc's **Do Not Do** and **Known Risks**.

**Acceptance is the whole contract.** You are not present while the work happens
and cannot correct course. Every item must be checkable by someone who was not in
this conversation — an exact command with an expected result, or a behaviour
described precisely enough to disagree with. "Works correctly" is not an
acceptance criterion.

**Write commands for the shell that will run them.** One command per line, never
an `&&` chain — Windows PowerShell 5.1 has no `&&`, and a syntax error comes back
as a check that never ran. On Windows also skip inline env prefixes
(`NODE_ENV=test cmd`), `2>/dev/null`, and POSIX tools assumed on `PATH`; prefer
the project's own runner (`npm test`, `pytest tests/auth -q`, `dotnet build`),
which behaves the same in every shell. Paths stay relative with forward slashes.

## While the package is out

Do nothing. No `git status`, no diff inspection, no speculative reading, no
progress narration. The work is happening in another process that will report
when it is done, and "not finished yet" is the whole of what any check could tell
you. Each idle turn re-sends your entire growing context to buy that non-answer.

Wait for the user to bring back the report and the diff.

## Review

You have the package you wrote, the worker's report, and the diff. Check in this
order:

1. **Requirement conformance.** Does the change do what `Goal` asked, and does
   every `Acceptance` item hold? Verify against the pasted evidence, and re-run
   anything whose result decides acceptance. A claim of a passing check is not a
   passing check.
2. **Architecture.** Does the change fit the module boundaries in the atlas? Is
   the logic where that module's doc says it belongs? Is anything under
   `Must Preserve` altered?
3. **Diff.** Did it stay inside `Scope`? Any special case, hardcoded value,
   swallowed exception, test-only production branch, duplicated logic, or
   weakened test? Is the new code more complex than the problem it solves? Side
   effects the report did not mention?
4. **Tests.** Do the new tests assert real behaviour, or encode the
   implementation's mistake? Would they fail if the bug came back?

Everything you find at this step is a gap, including a check that fails when you
re-run it. Fixing it yourself is the tempting move and the wrong one: it makes
you the author of the code you just accepted, and nobody reviews it after that.

**Returning gaps.** Name gaps and nothing else. Do not re-explain the task, do
not restate the goal, do not re-send the package — the worker has it.

```markdown
## Gaps
1. <file:line> — <what is wrong, and what "fixed" looks like>
2. <...>

Everything else is accepted. Change nothing outside these points.
```

That last line matters: without it, a capable agent asked to fix two things will
often improve five, and your review starts over.

Return at most twice. A third round means the package was wrong, not the work —
withdraw it, fix the specification, and reissue.

Append each gaps list to the package file, so the finished document records both
what was asked and what had to be corrected.

## Complete (lead-only writes)

Before marking the change complete, explicitly answer: did this change alter a
module's boundary, ownership, or an external API/contract? If yes, update the
affected atlas doc(s) now, as part of this same completion step — not a
follow-up. Update only the affected module docs and index entries; do not rescan
unrelated modules.

Then, at T1/T2, move the package to `docs/changes/completed/{{DATE}}/{{SLUG}}.md`
and append one line to that day's `docs/changes/completed/{{DATE}}/summary.md`,
noting whether atlas docs were updated or that none needed updating. Record
decisions, divergences from the package, known limits, and remaining debt. Do not
record a step-by-step operation log, a restatement of the diff, or the worker's
narrative. At T0, delete the package instead of archiving it — a trivial change
does not earn an archive entry.

You are the single writer for all of these files. A worker never writes them.

## Reporting & delivery

- Reporting level: {{REPORTING_LEVEL}} — Plain: no module names, paths, or code in
  user-facing reports. Technical: include them.
- Delivery policy: {{DELIVERY_POLICY}}
- Verification results are always in the user-facing report regardless of
  reporting level; never claim completion on a failed check.
- Carry conclusions forward across steps. Re-reading the index at review time to
  re-establish what a module owns is paying twice for one fact.
- Do not rerun Codebase Atlas unless the user explicitly asks for one. If they do
  — or if you find the map wrong in modules you did not touch — a **refresh**
  re-scans only the modules that drifted and is what almost every such request
  actually needs; a **rebuild** discards the map and scans everything. Say which
  one you propose and why before spending either.
