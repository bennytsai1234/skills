# Session Status and Checkpoint Protocol

Project Genius sessions can span multiple conversations. Without a checkpoint
file, the agent must infer session state by scanning scattered documents —
which is slow, error-prone, and risks redoing locked decisions.

`docs/genius/STATUS.md` is the single source of truth for session progress.
It is written and updated by the agent, not by the user.

---

## When to Write STATUS.md

Create `docs/genius/STATUS.md` at the very start of Step 2.0 (prototype
directory initialization), before any Stage 2 work begins. Update it:

- After every Stage 1 sub-step completes (Steps 1.1–1.7).
- After each Stage 2 sub-gate passes (Vibe, Layout, Surface Map, per-screen
  locks, Interaction micro-locks, Data model, Assets/Voice, Tech stack).
- After Handoff completes.
- Before ending any session (even mid-stage).

Never write STATUS.md at the very end of a session only — the session may be
interrupted. Update it progressively.

---

## STATUS.md Format

```markdown
# Project Genius — Session Status

_Last updated: YYYY-MM-DD_

## Session Info

- Project name: [name from one-sentence essence]
- Product type: [type]
- Downstream coding agent: [Claude Code / Codex / Cursor / unknown]

## Stage 1: Requirements & Planning

- [ ] 1.1 Product type detected
- [ ] 1.2 Mental anchor captured (essence, 3 references, non-goals)
- [ ] 1.3 Target user and problem locked
- [ ] 1.4 MVP scope locked
- [ ] 1.5 Constraints locked
- [ ] 1.6 Architecture-changing constraints locked
- [ ] 1.7 Module plan confirmed
- [ ] Stage 1 sign-off received
- Output: `00-requirements.md` — [ ] written

## Stage 2: Design & Prototyping

Sub-Gate 2.A — Vibe:
- [ ] Vibe candidates proposed
- [ ] User confirmed vibe
- [ ] `prototype/_vibe-test.html` exists
- [ ] `01-design-system.md` (partial: vibe section) — written

Sub-Gate 2.B — Layout Archetype:
- [ ] Archetype candidates proposed
- [ ] User confirmed archetype
- [ ] `prototype/_archetype-test.html` exists

Sub-Gate 2.C — Surface Map:
- [ ] Complete screen/section/endpoint list confirmed
- [ ] `02-surface-map.md` — written

Sub-Gate 2.D — Per-Screen Locks:
(copy and repeat per screen)
- [ ] [screen name].html — unlocked
  User quote: —

Sub-Gate 2.E — Interaction Micro-Locks:
- [ ] Per-button state maps captured
- [ ] Per-form validation captured
- [ ] Per-list states captured
- [ ] Interaction pilot artifact confirmed
- [ ] `03-interactions.md` — written

Sub-Gate 2.F — Native Behaviors (conditional):
- [ ] Gesture map captured
- [ ] Haptic feedback captured
- [ ] Native component decisions captured
- [ ] `03b-native-behaviors.md` — written

Sub-Gate 2.G — Data Model (conditional):
- [ ] All entities locked
- [ ] All API endpoints locked
- [ ] Permission model locked
- [ ] Data model pilot artifact confirmed
- [ ] `04-data-model.md` — written

Sub-Gate 2.H — Assets and Voice:
- [ ] Voice lock confirmed (candidate sentence chosen)
- [ ] Asset source decisions made for all required assets
- [ ] Asset pilot artifact confirmed
- [ ] `05-assets-and-content.md` — written

Sub-Gate 2.I — Performance Budget (conditional):
- [ ] Core Web Vitals targets confirmed
- [ ] API response time SLA confirmed
- [ ] Performance budget written into `06-tech-stack.md`

Sub-Gate 2.J — Testing Strategy (conditional):
- [ ] Test layer priorities confirmed
- [ ] CI gate design confirmed
- [ ] Test data strategy confirmed
- [ ] `10-testing.md` — written

Sub-Gate 2.K — Analytics Events (conditional):
- [ ] Tool selection confirmed
- [ ] Primary metrics locked
- [ ] Event inventory confirmed
- [ ] `11-analytics.md` — written

Sub-Gate 2.L — Tech Stack:
- [ ] Full stack confirmed
- [ ] `06-tech-stack.md` — written

Stage 2 sign-off:
- [ ] All screens locked
- [ ] All active sub-gates satisfied
- [ ] User confirmed "Stage 2 done"

## Handoff

- [ ] Pilot slice chosen: [screen/slice name]
- [ ] Phase build order confirmed
- [ ] `07-delivery-plan.md` — written
- [ ] `08-handoff.md` — written
- [ ] `09-ai-guardrails.md` — written
- [ ] STATUS.md — final update written

## Stale Decisions / Open Conflicts

(List any decisions that were locked but may be invalidated by later choices.
Clear this list when resolved.)

- [decision] — may conflict with [later decision] — STATUS: unresolved / resolved
```

---

## Resume Protocol

When resuming a Project Genius session:

1. Read `docs/genius/STATUS.md` first. This is the authoritative state.
2. Read documents marked as written to verify content matches STATUS.
3. Check `prototype/_locks.md` for per-screen lock status.
4. If STATUS.md does not exist, fall back to scanning existing documents
   and inferring state — then write STATUS.md immediately from what is found.
5. Surface any open conflicts listed in the "Stale Decisions" section before
   continuing.
6. Continue from the next incomplete sub-gate. Do not redo locked items unless
   the user explicitly asks.

### Conflict Detection on Resume

When STATUS.md and an actual document disagree (e.g. STATUS says
`01-design-system.md` is written but the file does not exist), surface the
discrepancy:

```
"STATUS.md says 01-design-system.md was written, but I can't find it.
Should I regenerate it from the locked vibe and archetype, or did something
change since the last session?"
```

Do not silently assume the STATUS is wrong or the document is wrong.
Always surface and ask.

---

## Scope Creep Guard (Standing Rule)

This rule runs throughout Stage 2 — it is not a sub-gate but a
standing check triggered whenever the user's feedback in a prototype
iteration introduces new capability.

When the user says something like "while we're here, can we also add X?" or
feedback implies a feature not in the v1 feature list from `00-requirements.md`:

1. Identify the new item.
2. Check it against the v1 feature list.
3. If not in v1, surface it explicitly:

```
"'X' isn't in the v1 scope (v1 = [A, B, C, ...]). Three options:
  a) Promote it to v1 now — I'll update 00-requirements.md and note the
     scope change.
  b) Queue it for v1.5 — I'll add it to the v1.5 list.
  c) Skip it for now.
Which would you like?"
```

4. Record the outcome in `00-requirements.md` under MVP Scope.
5. Do not silently add features to the prototype without user acknowledgment
   that scope has changed.

Scope creep that is not surfaced accumulates silently and creates a mismatch
between `00-requirements.md` and the actual prototype — which breaks the
handoff package.
