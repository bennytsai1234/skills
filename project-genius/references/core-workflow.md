# Core Workflow

Project Genius runs in two stages plus a handoff. Each step has a goal, a
question list, lock-required fields, and an output. Lock-required fields
gate the stage's output document — do not produce the output until every
lock-required field has an explicit user-confirmed answer.

See companion files:
- `confirmation-gates.md` for the complete lock-required field list per
  stage.
- `convergence-protocol.md` for how to run the proposal → feedback → lock
  loop.
- `type-question-trees.md` for product-type-specific questions.
- `product-type-router.md` for type routing rules.

---

## Stage 1: Requirements & Planning

Goal: anchor product identity and capture enough of the user's mental
image that Stage 2 can build a first-pass prototype.

### Step 1.0: Session Opening

Deliver the self-introduction defined in `SKILL.md` § Session Opening
before any other action. End with the first concrete question (product
type).

### Step 1.1: Product Type Detection

Ask: "What kind of product is this?" Present the candidate types listed in
`SKILL.md` § Product Type Router. Recognize mixed products. Do not force a
single label when the product genuinely combines types (e.g. SaaS dashboard
with a public marketing site).

Lock-required: at least one primary type.

### Step 1.2: Mental Anchor Capture

This step captures the user's mental image, not their feature list.

Ask in this order:

1. **One-sentence product essence.** Force the user to compress.
2. **3 reference products** (mandatory). For each: "what about this
   reference is like your product?" and "what about it is NOT?"
   - If the user cannot name references, propose 3 candidates based on
     product type and let them choose.
   - Reference pinning replaces adjective descriptions. See
     `convergence-protocol.md`.
3. **Non-goals.** "What is this product NOT?" Three concrete items.
4. **Elicitation questions** (pick 2-3):
   - "Close your eyes. What's the first screen the user sees?"
   - "Describe the user's first 30 seconds in the product."
   - "Three months after launch, what's the most-used feature?"
   - "If you screenshot the finished product and showed a friend, what
     would they say?"

Lock-required: one-sentence essence, 3 references with annotations,
non-goals.

### Step 1.3: Target User and Problem

- Primary user group (one specific persona, not "everyone").
- The actual problem (not the feature).
- Success signal in 6 months.

Lock-required: primary user, problem, one success signal.

### Step 1.4: MVP Scope

- v1: the smallest shippable scope.
- v1.5: near-term followups.
- v2: future, out of current scope.
- Explicit non-MVP items the user mentioned.

Lock-required: v1 feature list.

### Step 1.5: Constraints

- Time / budget / team skill.
- Platform (web only / mobile only / cross-platform).
- Compliance (GDPR / HIPAA / SOC2 / PCI / none).
- Deployment target (Vercel / self-host / mobile store / extension store).
- **Downstream coding agent identity** (Claude Code / Codex / Cursor /
  unknown). This affects how the handoff is structured.

Lock-required: platform, downstream agent identity.

### Step 1.6: Architecture-Changing Constraints

Only ask about items that change Stage 2 prototype shape:

- Offline + sync requirement.
- Realtime collaboration.
- Large dataset / pagination strategy.
- Undo/redo across complex operations.
- Roles, permissions, audit logs.
- Infinite canvas, precise coordinates, timelines, drag-and-drop ordering.
- High-frequency interaction (60fps).
- **Performance perception**: "Does this product need to feel fast? What's
  an acceptable wait time for the primary screen to load?" Even a rough
  answer (e.g., "first screen in under 2 seconds") is enough to lock a
  performance budget that flows into `06-tech-stack.md`. "No specific target"
  is a valid and lockable answer.

See `architecture-reasoning.md` for the reasoning patterns.

Lock-required: each constraint that the user confirms applies.

### Step 1.7: Module Plan

After locking Steps 1.1–1.6, decide which Stage 2 modules to activate.

1. Infer the module set from product type, MVP scope, and architecture
   constraints already confirmed.
2. Read the inferred list back: "Based on what you've told me, I'll
   activate [list]. Is that right?"
3. Adjust based on the user's response.
4. Record the confirmed module list. It becomes part of `00-requirements.md`
   and gates which Stage 2 output documents are produced.

Do not ask module-by-module questions if the answer is already clear from
prior steps. Only ask about genuinely ambiguous cases (e.g. "You mentioned
admin features — should I activate the Auth/Permissions module?").

See `module-router.md` for activation criteria per module.

Lock-required: confirmed module list.

### Stage 1 Confirmation Gate

Before producing `00-requirements.md`, every lock-required field above
MUST be user-confirmed. See `confirmation-gates.md` § Stage 1 for the
complete checklist.

### Stage 1 Output

`00-requirements.md` covering: type, essence, 3 references, non-goals,
elicitation answers, user/problem/success, MVP split, constraints,
architecture constraints, downstream agent identity, confirmed module list,
Sources & Confidence block.

---

## Stage 2: Design & Prototyping (Iterative)

Goal: build a visual prototype that matches the user's mental image, by
iterating between agent proposals and user feedback until every screen is
locked.

Documents in Stage 2 come AFTER prototype lock, not before. The locked
prototype IS the primary artifact.

### The Iteration Loop

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   ┌──────────────────┐                                      │
│   │  Build / Update  │                                      │
│   │   prototype      │◀──────────────────┐                  │
│   └────────┬─────────┘                   │                  │
│            │                             │                  │
│            ▼                             │                  │
│   ┌──────────────────┐                   │                  │
│   │  User reviews    │                   │                  │
│   │  in browser      │                   │                  │
│   └────────┬─────────┘                   │                  │
│            │                             │                  │
│            ▼                             │                  │
│   ┌──────────────────┐    not yet        │                  │
│   │  All screens     │───────────────────┘                  │
│   │  locked?         │                                      │
│   └────────┬─────────┘                                      │
│            │ yes                                            │
│            ▼                                                │
│   ┌──────────────────┐                                      │
│   │  Extract docs    │                                      │
│   │  from prototype  │                                      │
│   └──────────────────┘                                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Step 2.0: Initialize prototype directory and STATUS.md

Create `prototype/` next to the docs. Inside it:
- `index.html` — entry point linking to all screens.
- `_locks.md` — per-screen lock status. Format:
  ```
  - [ ] dashboard.html  unlocked
  - [x] login.html      locked at 2026-05-13 — "matches mental image"
  ```
- `assets/` — CSS, images, JS.

If the downstream stack is known (e.g. React + Tailwind), the prototype
may use it. Otherwise plain HTML/CSS is the safe default — any downstream
agent can read it.

Create `docs/genius/STATUS.md` using the format defined in
`session-status.md`. Mark Stage 1 items as complete (since Stage 2 is
opening). Leave all Stage 2 sub-gates unchecked. Update STATUS.md after
every sub-gate completes for the rest of the session.

See `session-status.md` for the full checkpoint format and resume protocol.

### Step 2.1: Vibe Lock

Propose 3 vibe candidates based on the Stage 1 reference pins. Each
candidate gets:
- A label (e.g. "cold engineering density like Linear", "warm hand-drawn
  like Excalidraw", "minimalist editorial like Stripe").
- 3-5 concrete tokens (primary color, font family, radius, spacing
  scale).
- A pilot artifact: a single button + a single card rendered with the
  vibe, in `prototype/_vibe-test.html`.

User picks one or says "closer to A but X is wrong". Iterate.

Lock-required: vibe choice + token set (read back to user).

### Step 2.2: Layout Archetype Lock

Propose 3 layout archetypes appropriate for the product type:

- Web app / SaaS: sidebar + canvas / topbar + grid / hub-and-spoke.
- Mobile: tab bar + stacks / drawer + stacks / single stack.
- Marketing: single scroll / sectioned scroll with sticky nav.
- Content: list+detail / docs sidebar + reader / magazine grid.
- API: doc-style / Postman-style / Stripe-style reference.
- Extension: popup-only / sidebar-only / popup + content overlay.
- Desktop: window-only / tray + window / menu bar + window.

Pilot artifact: ASCII wireframe of the chosen archetype, plus a static
HTML version with one fake screen showing the chrome.

Lock-required: archetype choice.

### Step 2.3: Surface Map + First-Pass Prototype

Together with the user, list every screen / view / endpoint / section
the product needs. For each:
- Name.
- Purpose.
- Primary action.
- Adjacent screens (where you came from, where you go).

Then agent generates the first-pass prototype:
- One HTML file per screen.
- Locked vibe applied.
- Locked archetype as chrome.
- Placeholder data.
- Stub interactions (buttons present but clicks just toast "stub").

For non-UI product types:
- API service: generate `prototype/api-reference.html` with one fully
  spec'd endpoint as a template, plus a stub list of remaining endpoints.
- Browser extension: generate `popup.html`, `sidebar.html`, and a sample
  host-page injection demo.

Lock-required: complete screen/endpoint list.

### Step 2.4: Per-Screen Iteration to Lock

For each screen, run the convergence loop:

1. User opens the screen in browser.
2. User marks what's wrong (anything: spacing, color, copy, layout,
   missing element, wrong button).
3. Agent asks targeted questions about the marked items only.
4. Agent updates the file.
5. Repeat until user says "this screen matches my image".
6. Mark `[x]` in `prototype/_locks.md` with timestamp and user's
   confirmation quote.

A screen is not locked until the user explicitly confirms. Implicit
acceptance ("looks fine") is not a lock unless followed by an explicit
"lock this".

### Scope Creep Guard (Standing Rule for All of Stage 2)

This rule is not a step — it runs continuously throughout Stage 2 iteration.

Whenever user feedback in a prototype round introduces a capability not in
the v1 feature list from `00-requirements.md`:

1. Flag the new item explicitly. Do not silently add it to the prototype.
2. Present three options:
   - Promote to v1 (update `00-requirements.md`; note the scope change).
   - Queue for v1.5 (add to the v1.5 list in `00-requirements.md`).
   - Skip.
3. Wait for the user's choice before proceeding.
4. Record the outcome in `00-requirements.md`.

Scope creep added silently causes a mismatch between the requirements doc
and the prototype, which breaks the handoff package. Surface it every time.

### Step 2.5: Per-Interaction Micro-Locks

During or after screen lock, capture interaction details that pixels
cannot show. For each meaningful button, form field, list:

**Button checklist:**
- Click target (inline edit / modal / slide-over / new page / nothing).
- Loading behavior (spinner / skeleton / optimistic / disabled).
- Success feedback (toast / inline message / redirect / silent).
- Error feedback (toast / inline / banner).
- Optimistic update yes/no.
- Confirmation dialog needed.

**Form field checklist:**
- Validation timing (on change / on blur / on submit).
- Error message location (inline / summary / both).
- Required marking style.
- Async validation needs.

**List/table checklist:**
- Empty state.
- Loading state.
- Error state.
- Partial state.
- Pagination / infinite scroll / load more.
- Sort and filter behavior.
- Bulk actions if applicable.
- Row click behavior.

Pilot artifact for the most complex interaction (usually a Save flow):
fully implemented in HTML/JS showing click → loading → success → error
states. User confirms before locking the interaction.

Lock-required: every meaningful button's full state map; every form's
validation behavior.

### Step 2.5b: Native Behavior Micro-Locks (Conditional — Mobile and Desktop only)

Run during or after per-screen iteration (Step 2.4), for each screen that
has non-tap gestures, OS-level interactions, or platform-specific components.

Capture per screen:
- Navigation transition type (push / modal full / sheet / fade / replace).
- Every non-tap gesture → action → conflict resolution.
- Haptic feedback for every primary action, destructive action, and error.
- Native vs custom component decision for every modal-type pattern.
- Keyboard avoidance and return key behavior for every form.

For Mobile: also capture push notification types, OS integrations (camera,
share, biometrics, deep links) for features in v1 scope.

For Desktop: also capture native menu structure with keyboard shortcuts, tray
icon states, window management, and auto-updater UX.

Pilot artifact: a walkthrough page or annotated prototype note that lists each
confirmed gesture/behavior per screen. The user confirms the behavior matches
their expectation before locking.

Lock-required: gesture map and transition type for every screen with
non-tap interactions; haptic feedback decisions; native component choices.

See `modules-native-behaviors.md` for the full question tree.

### Step 2.6: Data Model and Domain (Conditional)

Skip if no backend / no persistent data.

For each entity:
- Name.
- Purpose.
- Fields with types.
- Sample records (actual rows, not just schema).
- Relationships.
- Permissions (who can read/write per role).
- Lifecycle states.

For each API endpoint or server action:
- Method + path / action name.
- Auth requirement.
- Request shape (with example).
- Response shape (with example).
- Error cases (with example error responses).
- Frontend consumer.

Pilot artifact: one entity's full lifecycle (create → read → update →
delete) walked through with sample data and permission checks.

See `modules-backend-data.md` for deeper rules.

Lock-required: every entity, every endpoint, permission model.

### Step 2.7: Asset and Content Pinning

For every image, icon, video, copy block:
- Source (user / AI-generated / placeholder / stock / brand asset).
- License status.
- Specs (size, aspect ratio, format).
- Fallback rule.
- Alt text / accessibility note.

For copy / voice:
- Propose 3 voice samples (same message, three tones). User picks.
- Banned phrases / required phrases.

Pilot artifact: one full screen rendered with REAL assets and REAL copy
(not Lorem Ipsum, not placeholder images). User confirms the feel.

See `modules-media-assets.md` for deeper rules.

Lock-required: voice choice, asset source decisions for every required
asset.

### Step 2.7b: Testing Strategy (Conditional)

Run when the Testing module is active (see `module-router.md`).

Capture:
- Test layer priority ranking (E2E / integration / unit / visual regression /
  accessibility — ordered by value for this specific product).
- CI gate: which checks must pass before a PR merges.
- E2E framework if E2E is prioritized.
- Test data strategy (fixtures / factories / shared seed / none).
- Coverage threshold (if the team wants one).

Pilot artifact: not required. Written confirmation of the CI gate design is
sufficient.

See `module-testing.md` for the full question tree.

### Step 2.7c: Analytics Events (Conditional)

Run when the Analytics module is active (see `module-router.md`).

Capture:
- Tool selection.
- 2-3 primary product metrics (the numbers the team watches weekly).
- Funnel event inventory for every conversion funnel.
- Core feature events for every v1 feature.
- Event naming convention (must be consistent).
- Identity strategy (when user is identified, what properties are set).
- Privacy/consent strategy (required for EU users by default).

Pilot artifact: not required. The event inventory table is the primary
artifact.

See `module-analytics.md` for the full question tree.

### Step 2.8: Tech Stack (Late)

Only after product shape is locked. Decide:
- Frontend framework + styling solution.
- Backend framework (if applicable).
- Database.
- Storage.
- Auth provider.
- Hosting / deployment.
- CDN / media pipeline.
- Testing approach.
- Monitoring basics.

Justify choices against the locked architecture constraints from Step
1.6.

Lock-required: each stack layer.

### Stage 2 Confirmation Gate

Before producing Stage 2 output documents, ALL of these MUST be true:
- Every screen in `prototype/_locks.md` is marked locked.
- Vibe, layout archetype, navigation pattern are confirmed.
- Every meaningful button's interaction state map is captured.
- Data model and API contract are confirmed (if applicable).
- Voice and asset decisions are confirmed.
- Tech stack is confirmed.

See `confirmation-gates.md` § Stage 2.

### Stage 2 Outputs

- `prototype/` — the locked HTML/CSS files. Primary source of truth.
- `01-design-system.md` — tokens extracted from the prototype.
- `02-surface-map.md` — screen list, navigation, transitions.
- `03-interactions.md` — per-button / per-field / per-state.
- `03b-native-behaviors.md` — gesture map, haptics, native components,
  OS integrations. [Mobile and Desktop only]
- `04-data-model.md` — entities, API, permissions (if applicable).
- `05-assets-and-content.md` — asset inventory, voice, copy rules.
- `06-tech-stack.md` — stack decisions with rationale and performance budget.
- `10-testing.md` — test layer priorities, CI gate design, test data
  strategy. [Testing module]
- `11-analytics.md` — tool, primary metrics, event inventory, identity,
  naming convention, privacy. [Analytics module]

---

## Handoff

Goal: package the prototype + docs for the downstream coding agent in a
way that prevents drift and forces pilot-slice validation.

### Step 3.1: Build Order

Decide phases and dependencies. For each phase:
- User stories covered.
- Screens or endpoints in scope.
- Dependencies on previous phases.
- Acceptance criteria (with pointers to prototype files).
- Verification steps.
- Stop point.

### Step 3.2: Pilot Slice

Choose one representative locked screen (or one vertical slice for
full-stack) as the first thing the coding agent implements. The pilot:
- Uses the locked stack.
- Re-implements one locked screen exactly as the prototype shows it.
- Wires the chosen state management / data fetching pattern.
- Includes one error and one success state.

User reviews the pilot in the chosen stack before any other phase
starts.

### Step 3.3: Stop Points and Guardrails

The coding agent MUST stop and ask before:
- Changing data model.
- Changing auth model.
- Changing the locked design system.
- Diverging from the prototype's layout or interaction spec.
- Adding paid dependencies.
- Building all screens before pilot approval.

The coding agent MUST NOT:
- Invent real assets.
- Invent API endpoints not in the data model.
- Silently change tech stack.
- Convert mock data into production data without permission.

See `handoff-guardrails.md`.

### Step 3.4: Acceptance Checklist

Per-phase checklist used to verify each phase's output matches the
locked prototype.

### Handoff Outputs

- `07-delivery-plan.md` — phases, dependencies, pilot slice.
- `08-handoff.md` — single source of truth ordering, first coding-agent
  prompt, acceptance checklist.
- `09-ai-guardrails.md` — must-follow, must-ask-before, must-not-invent.

---

## Resuming

When restarting a session from existing files:

1. Scan `docs/genius/` for completed documents.
2. Scan `prototype/_locks.md` for locked screens.
3. Identify the latest complete stage.
4. Flag conflicts and stale decisions.
5. Continue from the next useful step. Do not redo locked items unless
   the user asks.

---

## Mode Variants

- **Mock-only / prototype-only**: stop at end of Stage 2. Skip Step 2.6
  (data model) unless required for the UI. Skip Step 2.8 (stack)
  beyond frontend.
- **API-only**: Stage 2 focuses on Step 2.6 and a doc-style prototype.
  Skip vibe / layout / per-screen iteration.
- **Resume from existing repo + docs**: detect via Codebase Atlas if
  present; otherwise scan manually.
