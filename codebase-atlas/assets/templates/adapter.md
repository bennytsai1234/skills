# {{PROJECT_NAME}} Codebase Atlas

Self-contained entrypoint and router for daily work on this project. It carries
its own discipline — there are no separate workflow docs to read.

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
assumptions and unknowns. Never edit — if a fix is needed, hand off to Change
after the user agrees. Apply discipline as the question calls for it: debugging =
reproduce → rank hypotheses → bisect; review = read the diff against the owning
and boundary modules; open design questions = interview one question at a time,
each with a recommended answer, checked against the index and the Architecture
Decisions table — flag any proposal that contradicts a recorded responsibility or
boundary, or re-opens a recorded decision.

## Change (any edit)

Judge a discipline tier, then scale effort:

- **T0 trivial** (no logic change, reversible, single file): one-line
  Before/After; skip the plan file; run the single most relevant check.
- **T1 normal** (contained, reversible, clear diagnosis): add one focused test
  when a cheap seam exists; write a scratch plan
  `docs/changes/planning/{{DATE}}-{{SLUG}}.md` before editing source
  (`{{DATE}}` = today's local date, ISO `YYYY-MM-DD`).
- **T2 hard/risky** (async/stateful bug, multi-module, external API,
  irreversible, perf regression, uncertain diagnosis): full discipline; same plan
  file; usually a Decision Gate.

**Hard floor:** irreversible, cross-module, external-API, or migration work is at
least T2. Honour a plain "be quick / be thorough" override, but never below the
floor.

**Before / After gate** (the only confirmation interface):
- **Before**: current state and why the change is needed — for a bug, the
  diagnosed root cause — in plain language.
- **After**: what becomes true, and how it will be verified.

At T1/T2, wait for explicit confirmation before editing any file. At T0
(trivial, reversible, single file), state the one-line Before/After and proceed
without waiting, then report after — it is reversible if the Before was wrong.

**Decision Gate** — when a change alters module boundaries, an external API, is
irreversible or a migration, or has two or more viable approaches: first check whether the proposal
contradicts or re-opens anything recorded in the index or Architecture Decisions
table — if so, name it and confirm the prior decision is being reopened. Then
present Context / Options (A/B with trade-offs) / Recommendation and wait for a
choice before the Before/After. Record cross-module decisions in the index's
Architecture Decisions table; module-level ones in that module's Known Risks.

After edits, verify scaled to the tier; the verification result is always in the
report — never claim completion on a failed check. Once complete, move the plan
to `docs/changes/completed/{{DATE}}/{{SLUG}}.md` and append a one-line entry for
it to that day's `docs/changes/completed/{{DATE}}/summary.md` (the daily work
summary). Update atlas docs only when module boundaries, ownership, or external
APIs change — incrementally, no rescan.

## Reporting & delivery

- Reporting level: {{REPORTING_LEVEL}} — Plain: no module names, paths, or code in
  user-facing reports. Technical: include them.
- Delivery policy: {{DELIVERY_POLICY}}
- Do not rerun Codebase Atlas initialization unless the user explicitly asks for a
  full rebuild.
