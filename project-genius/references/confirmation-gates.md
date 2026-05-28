# Confirmation Gates

Each Project Genius stage has a list of fields that MUST be user-confirmed
before the stage's output artifacts are produced. This file is the
checklist the agent runs through before writing any final document.

The agent classifies every field into one of three categories:

- **🔒 lock-required**: explicit user confirmation required; cannot be
  inferred alone. If the agent infers a value, it must read the inference
  back verbatim ("you said the primary user is a small-business owner —
  confirm?") and receive an explicit yes.
- **🟡 inference-allowed-with-readback**: agent may infer from materials,
  but must surface the inference for confirmation before treating it as
  locked. Silence does not equal acceptance.
- **⚪ default-allowed**: agent may use a sensible default without
  asking. Document the default in the output with rationale.

## The Iron Rule

> **No stage output document is written until every 🔒 field on that
> stage's checklist is confirmed.**

If a 🔒 field is missing, the agent stops, asks the relevant question,
and only resumes output generation once answered.

---

## Stage 1: Requirements & Planning Gate

Before producing `00-requirements.md`:

### Product Type
- 🔒 Primary product type (Web app / SaaS / Mobile / Marketing / Content /
  API / Extension / Desktop / mixed).
- 🟡 Secondary types if mixed.
- ⚪ Platform sub-classifications (e.g. "iOS first, Android later").

### Mental Anchor
- 🔒 One-sentence product essence (in the user's own words).
- 🔒 At least 3 reference products, each with "like X / unlike X"
  annotations.
- 🔒 At least 3 non-goals ("this is NOT...").
- 🟡 Answers to at least 2 elicitation questions (close-eyes, first 30
  seconds, three months, friend reaction).

### User and Problem
- 🔒 Primary user group (one specific persona).
- 🔒 The actual problem (not the feature wishlist).
- 🔒 At least one success signal.

### MVP Scope
- 🔒 v1 feature list (explicit, not "obvious from context").
- 🟡 v1.5 / v2 splits.
- 🟡 Non-MVP items the user mentioned.

### Constraints
- 🔒 Target platform.
- 🔒 Downstream coding agent identity (Claude Code / Codex / Cursor /
  unknown).
- 🟡 Time / budget / team skill.
- 🟡 Compliance requirements.
- ⚪ Hosting / deployment defaults.

### Architecture Constraints (only ask if relevant)
- 🔒 If offline/sync is mentioned, the chosen sync model approach.
- 🔒 If realtime is mentioned, the collaboration model.
- 🔒 If permissions/roles are mentioned, the role list.
- 🟡 Other architecture-changing items (large dataset, undo/redo,
  infinite canvas, high-frequency interaction).

### Module Plan (Step 1.7)
- 🔒 Active module list confirmed by user.
- 🟡 Inferred modules read back to user ("Based on what you've told me,
  I'll activate Frontend, Backend, and Data/API modules — does that sound
  right?"). Silence does not equal acceptance.
- ⚪ Core modules (delivery plan, handoff, guardrails) are always active;
  no need to mention them in the confirmation.

### Stage 1 Sign-off
- 🔒 User explicitly confirms "Stage 1 done, proceed to prototype". Do
  not auto-progress.

---

## Stage 2: Design & Prototyping Gate

Stage 2 has multiple sub-gates because the stage is iterative. Each
sub-gate must be satisfied before the corresponding artifact is locked
and the next sub-stage begins.

### Sub-Gate 2.A: Vibe Lock

Before locking vibe and writing tokens into `01-design-system.md`:

- 🔒 User picked one of 2-3 vibe candidates (or said "closer to A but X").
- 🔒 Token set read back to user (primary color hex, font family, radius,
  spacing scale).
- 🔒 Pilot artifact `prototype/_vibe-test.html` exists and user confirmed
  it matches expectation.
- 🟡 Dark mode requirement (yes / no / later).
- ⚪ Token naming convention.

### Sub-Gate 2.B: Layout Archetype Lock

Before generating first-pass screens:

- 🔒 Archetype chosen from type-appropriate candidates.
- 🔒 Navigation pattern locked (sidebar / topbar / tab bar / etc.).
- 🔒 Pilot artifact `prototype/_archetype-test.html` shows the chrome
  with placeholder content; user confirmed.

### Sub-Gate 2.C: Surface Map Lock

Before generating per-screen HTML:

- 🔒 Complete screen/section/endpoint list.
- 🔒 For each item: name, purpose, primary action, adjacency.
- 🟡 Modal / slide-over / drawer inventory.
- 🟡 Public vs authenticated separation if relevant.

### Sub-Gate 2.D: Per-Screen Lock (repeated per screen)

A screen is locked when:

- 🔒 User opened the screen's HTML file in their browser.
- 🔒 User gave explicit "this matches my image" or equivalent confirming
  language. Silent "ok" does NOT count.
- 🔒 Confirmation recorded in `prototype/_locks.md` with timestamp and
  quote.
- 🟡 Any out-of-scope items for that screen noted.

### Sub-Gate 2.E: Per-Interaction Micro-Locks

For each meaningful button / form / list, before writing to
`03-interactions.md`:

- 🔒 Button: click target, loading behavior, success feedback, error
  feedback.
- 🔒 Form field: validation timing, error location, error copy style.
- 🔒 List: empty / loading / error / partial / success states.
- 🔒 Pilot artifact for the most complex interaction (usually a Save
  flow): user confirmed.

### Sub-Gate 2.F: Data Model Lock (conditional)

If backend / data is in scope, before writing `04-data-model.md`:

- 🔒 Every entity with fields, types, sample records (not just schema).
- 🔒 Relationships between entities.
- 🔒 Permission model per entity per role.
- 🔒 Every API endpoint / server action: method, path, auth, request
  shape, response shape, error cases.
- 🔒 Pilot artifact: one entity's full lifecycle walked through with
  sample data and permission checks; user confirmed.

### Sub-Gate 2.G: Asset & Voice Lock

Before writing `05-assets-and-content.md`:

- 🔒 Voice choice (user picked from 3 sample sentences).
- 🔒 Asset source decisions for every required asset (user / AI /
  placeholder / stock).
- 🔒 Pilot artifact: one screen rendered with REAL assets and REAL copy;
  user confirmed.
- 🟡 Banned phrases / required phrases.
- 🟡 Image licensing status per asset.

### Sub-Gate 2.F-ext: Native Behaviors Lock (conditional — Mobile and Desktop only)

After per-screen locks, before writing `03b-native-behaviors.md`:

- 🔒 Gesture map for every screen with non-tap gestures (gesture → action →
  conflict resolution).
- 🔒 Haptic feedback decisions for every primary action, destructive action,
  and error (Mobile only).
- 🔒 Native vs custom component decision for every modal-type, bottom
  sheet, action sheet, picker, and context menu pattern.
- 🔒 Keyboard behavior per form: avoidance strategy, return key action,
  dismiss trigger.
- 🔒 Navigation transition type for every screen-to-screen move (push /
  modal full / sheet / fade).
- 🟡 OS integration per feature (share sheet, biometrics, file picker,
  camera, deep links) — only for features in v1 scope.
- 🔒 Desktop: native menu structure with keyboard shortcuts (Desktop only).
- 🔒 Desktop: tray/menu bar icon states and click behavior (Desktop only,
  if applicable).

### Sub-Gate 2.I: Performance Budget Lock (conditional)

Activate when any of these apply: the product is user-facing web or mobile;
user mentioned speed, performance, or latency; architecture constraints
include large dataset or high-frequency interaction.

Before writing the performance section of `06-tech-stack.md`:

- 🔒 Core Web Vitals targets (LCP / FID / CLS) or equivalent mobile
  startup time target. Even "no specific target" must be stated explicitly.
- 🔒 API response time SLA (p50 / p95 targets, or "no SLA for v1").
- 🟡 Caching strategy per data type (static assets / API responses /
  user-specific data).
- 🟡 Bundle size budget (if frontend is in scope).
- ⚪ DB query budget (derive from API SLA if not stated).

### Sub-Gate 2.J: Testing Strategy Lock (conditional)

Activate when the Testing module is active (see `module-router.md`).

Before writing `10-testing.md`:

- 🔒 Test layer priority ranking confirmed (E2E / integration / unit /
  visual regression / accessibility — ordered by value for this product).
- 🔒 CI gate: which checks must pass before a PR can merge.
- 🔒 Test data strategy: fixtures / factories / shared seed / none.
- 🔒 E2E framework chosen (if E2E is in the priority list).
- 🟡 Coverage threshold (if any).
- 🟡 External API handling in tests (real sandbox / cassettes / mocked).
- ⚪ Accessibility automation level (axe in CI / manual / none).

### Sub-Gate 2.K: Analytics Events Lock (conditional)

Activate when the Analytics module is active (see `module-router.md`).

Before writing `11-analytics.md`:

- 🔒 Analytics tool confirmed.
- 🔒 2-3 primary product metrics locked (the numbers the team will watch).
- 🔒 Funnel event inventory confirmed for every conversion funnel.
- 🔒 Core feature events confirmed for every v1 feature.
- 🔒 Event naming convention chosen (snake_case / Object Verbed / other)
  — and applied consistently across the entire event list.
- 🔒 Identity strategy: when does a user get a stable ID, what properties
  are set at identification.
- 🟡 Privacy/consent strategy (required for EU users by default).
- 🟡 Group analytics needed (org-level in addition to user-level).
- ⚪ Specific event properties beyond the core funnel.

### Sub-Gate 2.H: Tech Stack Lock

Before writing `06-tech-stack.md`:

- 🔒 Frontend framework + styling solution.
- 🔒 Backend framework if applicable.
- 🔒 Database.
- 🔒 Auth provider if relevant.
- 🟡 Storage / CDN / monitoring choices.
- ⚪ Specific provider within a chosen category (e.g. which Postgres
  host).
- 🔒 Each choice justified against Stage 1 architecture constraints.

### Stage 2 Sign-off

- 🔒 All screens in `prototype/_locks.md` marked locked.
- 🔒 Every sub-gate above satisfied.
- 🔒 User explicitly confirms "Stage 2 done, prepare handoff".

---

## Handoff Gate

Before writing `07-delivery-plan.md`, `08-handoff.md`,
`09-ai-guardrails.md`:

- 🔒 Stage 2 sign-off satisfied.
- 🔒 Downstream coding agent identity confirmed (already from Stage 1).
- 🔒 Pilot slice screen chosen.
- 🔒 Build phase order with dependencies.
- 🔒 Each phase has acceptance criteria pointing to prototype files.
- 🔒 `docs/genius/STATUS.md` reflects all completed sub-gates with no
  unresolved conflicts in the "Stale Decisions" section.
- 🟡 Stop points between phases.
- 🟡 Per-phase guardrails (must-ask-before, must-not-invent).

---

## Confidence Marking in Output Documents

When a 🟡 inference-allowed field is used, the output document MUST
mark it explicitly:

```markdown
## Sources & Confidence

- Materials used: [list]
- Confirmed by user: [list]
- Inferred from materials, user confirmed: [list]
- Inferred from materials, NOT yet user-confirmed: [list]
- Open questions: [list]
```

The agent MUST NOT leave "Inferred from materials, NOT yet
user-confirmed" non-empty if the document is going to handoff. Resolve
all such items before locking the document.

---

## Common Failure Modes

These are the most frequent gate violations from weak models:

| Failure | Fix |
|---------|-----|
| Treating user's "ok" as a lock | Ask explicitly: "should I lock this?" |
| Inferring 5 things and writing the doc | Stop. Read each inference back individually. |
| Skipping pilot artifact "because the docs are clear" | The artifact is the spec, the doc is metadata. Generate the artifact. |
| Producing all Stage 2 docs before any screen is locked | Stage 2 docs come AFTER lock. Refuse this order. |
| Single-round acceptance of a high-stakes lock | Force one more round: "want to see alternatives?" |
| Letting the user say "you decide" for visual choices | Force a reference pin or 3-candidate convergence. |

When the agent notices itself doing any of these, it stops and resets
to the protocol.
