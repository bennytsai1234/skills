# Output Templates

These templates correspond to the artifacts produced by the new
2-stage flow. They are not all generated in every session — produce only
what the active type and locked decisions require.

The numbering reflects the canonical order. Optional documents are
marked.

## Shared `Sources & Confidence` Block

Every Stage 1 and Stage 2 document includes this block near the top when
the content involves inference or user-supplied materials.

```markdown
## Sources & Confidence

- Materials used:
- Confirmed by user:
- Inferred from materials, user confirmed:
- Inferred from materials, NOT yet user-confirmed:
- Open questions:
```

The "NOT yet user-confirmed" bucket MUST be empty at handoff time.

---

## 00-requirements.md (Stage 1 output)

```markdown
# Requirements

## Sources & Confidence

## Product Type

## One-Sentence Essence

## Reference Pins

### Reference 1: [name]
- What to learn:
- What NOT to copy:

### Reference 2: [name]
- What to learn:
- What NOT to copy:

### Reference 3: [name]
- What to learn:
- What NOT to copy:

## Non-Goals

## Mental Image Notes
(Answers to elicitation questions: first screen, first 30 seconds, three
months in, friend reaction.)

## Target User

## Problem

## Success Signal

## MVP Scope

### v1 (in scope)

### v1.5 (near-term)

### v2 / out of scope

## Constraints
- Platform:
- Downstream coding agent:
- Time / budget / team:
- Compliance:

## Architecture-Changing Constraints
(Only items the user confirmed apply.)
```

---

## 01-design-system.md (Stage 2 output, after vibe + archetype lock)

```markdown
# Design System

## Sources & Confidence

## Vibe Lock
- Chosen: [label]
- Pilot artifact: `prototype/_vibe-test.html`
- User confirmation quote:

## Layout Archetype Lock
- Chosen: [archetype]
- Pilot artifact: `prototype/_archetype-test.html`

## Tokens

### Colors
- primary:
- accent:
- foreground:
- background:
- muted:
- danger / warning / success:

### Typography
- font-family-sans:
- font-family-mono (if needed):
- size scale:
- weight scale:
- line-height:

### Spacing
- scale:
- container widths:

### Radius and Borders
- radius scale:
- border-color:
- shadow scale:

### Motion
- timing functions:
- duration scale:

## Component Decisions
- buttons:
- inputs:
- cards:
- modals / sheets:
- navigation chrome:

## Accessibility Baseline

## Dark Mode
(if applicable)
```

---

## 02-surface-map.md (Stage 2 output, after surface map lock)

```markdown
# Surface Map

## Sources & Confidence

## Screen / Section / Endpoint List
(Format depends on product type. For Web/App: screens. For Marketing:
sections. For Content: templates. For API: endpoints. For Extension:
surfaces.)

| Name | Purpose | Primary Action | Adjacent | Locked? |
|------|---------|----------------|----------|---------|

## Navigation Pattern

## Transitions and Cross-Screen Behavior

## Modal / Sheet / Drawer Inventory

## Public vs Authenticated Split
(if applicable)
```

---

## 03-interactions.md (Stage 2 output)

```markdown
# Interactions

## Sources & Confidence

## Per-Button Spec

### [Screen] > [Button name]
- Click target:
- Loading behavior:
- Success feedback:
- Error feedback:
- Optimistic update:
- Confirmation dialog:

(repeat per meaningful button)

## Per-Form Spec

### [Screen] > [Form name]
- Validation timing:
- Error location:
- Required marking style:
- Async validation:
- Submit behavior:

## Per-List Spec

### [Screen] > [List/table name]
- Empty:
- Loading:
- Error:
- Partial:
- Pagination strategy:
- Sort / filter:
- Bulk actions:
- Row click:

## Per-State Rendering

## Keyboard Shortcuts (if applicable)

## Gestures (mobile only)
```

---

## 04-data-model.md (Stage 2 output, conditional)

```markdown
# Data Model

## Sources & Confidence

## Entities

### [Entity name]
- Purpose:
- Fields:
- Sample record:
- Relationships:
- Lifecycle states:
- Permissions:
  - role X: read/write/none
  - role Y: read/write/none

## API Contract

### [Method] [Path]
- Purpose:
- Auth:
- Request:
- Response:
- Errors:
- Frontend consumer:

## Auth Model
- Provider:
- Roles:
- Protected routes:
- Client-side visibility rules:
- Server-side enforcement points:

## Storage
- Files / images:
- Bucket strategy:
- Naming:
- Access control:
```

---

## 05-assets-and-content.md (Stage 2 output)

```markdown
# Assets and Content

## Sources & Confidence

## Voice Lock
- Chosen sample sentence:
- Tone keywords:
- Banned phrases:
- Required phrases (if any):
- Pilot artifact: `prototype/[screen-with-real-copy].html`

## Asset Inventory

| Asset | Purpose | Source | License | Specs | Fallback |
|-------|---------|--------|---------|-------|----------|

## Page-Level Asset Map
(per screen / section, list assets used)

## Generated Asset Rules
- AI-generated allowed: [yes/no per type]

## Missing Asset Protocol
- Placeholder rule for missing assets:
```

---

## 06-tech-stack.md (Stage 2 output)

```markdown
# Tech Stack

## Sources & Confidence

## Frontend
- Framework:
- Styling:
- State / data fetching:
- Forms / validation:
- Justification vs Stage 1 architecture constraints:

## Backend (if applicable)
- Framework:
- Database:
- Auth provider:
- Background jobs:
- Justification:

## Infrastructure
- Hosting:
- CDN:
- Storage:
- Monitoring:

## Performance Budget
- Core Web Vitals targets (or mobile startup time):
  - LCP target:
  - FID / INP target:
  - CLS target:
- API response time SLA:
  - p50:
  - p95:
- Bundle size budget (if applicable):
- Caching strategy:
  - Static assets:
  - API responses:
  - User-specific data:
- Note: if the user confirmed "no specific target", state that explicitly
  so the coding agent knows this was intentional.

## Environment Variables (inventory)

## Risks and Tradeoffs
```

---

## STATUS.md (written at Step 2.0, updated throughout Stage 2)

The format is defined in full in `session-status.md`. The template below
is a condensed reminder.

```markdown
# Project Genius — Session Status

_Last updated: YYYY-MM-DD_

## Session Info
- Project name:
- Product type:
- Downstream coding agent:

## Stage 1: Requirements & Planning
- [x] 1.1 – 1.7 (all sub-steps)
- [x] Stage 1 sign-off received
- Output: `00-requirements.md` — written

## Stage 2: Design & Prototyping
(Sub-gates 2.A through 2.L — see session-status.md for full checklist)

## Handoff
(Handoff gate items)

## Stale Decisions / Open Conflicts
(None — or list them here)
```

---

## 03b-native-behaviors.md (Stage 2 output — Mobile and Desktop only)

```markdown
# Native Behaviors

## Sources & Confidence

## Platform
- Primary platform: [iOS / Android / macOS / Windows / Linux / cross-platform]
- Framework: [React Native / Flutter / Electron / Tauri / native / other]

## Navigation Transitions

| From | To | Transition | Dismiss gesture |
|------|----|------------|----------------|

## Gesture Map

| Screen | Gesture | Action | Conflict resolution |
|--------|---------|--------|---------------------|

## Haptic Feedback (Mobile only)

| Action | Haptic type | Platform |
|--------|-------------|----------|

## Native vs Custom Component Decisions

| Pattern | Decision | Reason |
|---------|----------|--------|

## Keyboard Behavior

| Screen / Form | Avoidance strategy | Return key | Dismiss trigger |
|---------------|--------------------|------------|-----------------|

## Push Notifications (if applicable)

| Type | Trigger | Tap action | Rich? |
|------|---------|-----------|-------|

## OS Integrations (if applicable)

| Feature | Implementation | Notes |
|---------|----------------|-------|

## Window Management (Desktop only)

- Single / multi-window:
- Minimum size:
- Resizable:
- Saved position on relaunch:

## Native Menu Structure (Desktop only)

| Menu > Item | Shortcut | Action | Enabled condition |
|-------------|----------|--------|-------------------|

## Global Shortcuts (Desktop only)

| Shortcut | Action |
|----------|--------|

## Tray / Menu Bar Icon (Desktop only — if applicable)

- Click behavior:
- Variants: idle / active / alert
- Right-click menu items:
```

---

## 10-testing.md (Stage 2 output — Testing module)

```markdown
# Testing Strategy

## Sources & Confidence

## Test Layer Priorities

Ordered by value for this product:
1.
2.
3.

## CI Gate

Checks that must pass before a PR can merge:
- [ ] Linting
- [ ] Type checking
- [ ] Unit tests
- [ ] Integration tests
- [ ] E2E tests (subset: [which journeys])
- [ ] Visual regression (main branch only)
- [ ] Accessibility scan

Estimated CI run time target:

## E2E Coverage (if E2E is prioritized)

- Framework:
- Browser targets:
- Mandatory journeys (must have E2E):

| Journey | Entry | Exit condition |
|---------|-------|----------------|

- Auth strategy in tests:
- Run on: every PR / merge to main only

## Integration Tests

- Test against real DB: yes / no (if no: reason)
- Test data strategy: fixtures / factories / shared seed
- External API calls: real sandbox / VCR cassettes / mocked

## Unit Tests

- Framework:
- Coverage threshold (if any):
- Scope: pure functions only / also component render tests

## Visual Regression (if activated)

- Baseline: locked prototype HTML / first-build screenshots
- Pixel diff threshold:
- Guarded screens:

## Accessibility Testing

- axe-core in CI: yes / no
- Manual screen-reader audit in v1: yes / no
- WCAG target level: AA / AAA / none

## Test Data and PII

- Seed strategy:
- PII handling: anonymized / synthetic / none
- Payment flow test data:
```

---

## 11-analytics.md (Stage 2 output — Analytics module)

```markdown
# Analytics

## Sources & Confidence

## Tool

- Primary tool:
- Additional destinations (if Segment):
- Hosting: cloud / self-hosted
- Privacy/consent required: yes / no
- Consent manager (if yes):

## Primary Metrics

The 2-3 numbers the team watches weekly to know if the product is working:

1.
2.
3.

## Event Naming Convention

Chosen convention: [snake_case_verb_noun / Object Verbed / category:action]

All events below follow this convention. Deviations are bugs.

## Page / Screen View Events

- Auto-tracked: yes / no
- User properties attached on view: [list]
- UTM capture on landing: yes / no

## Funnel Events

### [Funnel name]

| Step | Event name | Properties |
|------|-----------|------------|

### [Funnel name — repeat per funnel]

## Core Feature Events

| Feature | Event name | Key properties |
|---------|-----------|----------------|

## Error and Dead-End Events

| Scenario | Event name | Properties |
|----------|-----------|------------|

## Identity

- Anonymous ID strategy:
- Identified on: [sign-up / first login / other]
- Properties set at identification:
- Group analytics: yes (org_id, plan) / no

## Privacy and Consent

- PII in events: none / hashed / [field list — must not be plaintext]
- Analytics loaded before consent: yes / no
- Data retention in tool: [N days / unlimited]

## Missing Event Protocol

If an event is not listed here, the coding agent must NOT add it without
approval. Missing events belong in v1.5 scope.
```

---

## 07-delivery-plan.md (Handoff output)

```markdown
# Delivery Plan

## Sources & Confidence

## Phases

### Phase 1: Pilot Slice
- Status: not started
- Scope: [one locked screen, end-to-end]
- Acceptance criteria (pointing to prototype):
  - matches `prototype/[screen].html` visually
  - implements interactions per `03-interactions.md` § [screen]
  - data wired per `04-data-model.md` § [entity]
- Verification:
- Stop point: user reviews; do not proceed without approval

### Phase 2: [Name]
- Status:
- User stories covered:
- Dependencies on previous phases:
- Acceptance criteria:
- Verification:
- Stop point:

## Pilot Slice
- Chosen screen / vertical slice:
- Why this one (most representative):
- Locked artifact reference:
```

---

## 08-handoff.md (Handoff output)

```markdown
# Handoff

## Sources & Confidence

## Downstream Coding Agent
- Identity (Claude Code / Codex / Cursor / other):
- Workspace conventions:

## Single Source of Truth Order
1. `prototype/` (the locked HTML/CSS files — primary)
2. `01-design-system.md` (tokens)
3. `04-data-model.md` (entities, API)
4. `03-interactions.md` (interaction specs)
5. `02-surface-map.md` (navigation)
6. `00-requirements.md` (context)
7. `06-tech-stack.md` (implementation choices)
8. `05-assets-and-content.md` (assets, copy)
9. `07-delivery-plan.md` (build order)

If documents conflict with the prototype, the prototype wins.

## First Coding-Agent Prompt
(Concrete prompt to paste into the downstream agent.)

## Implementation Sequence
(Phase 1 → 2 → 3 → ... from delivery plan.)

## Pilot Slice First-Prompt
(Specific instruction for Phase 1.)

## Acceptance Checklist
- scope match
- prototype fidelity per locked screen
- design tokens used
- interactions match spec
- data model wired
- error and empty states present
- no invented assets, endpoints, credentials
```

---

## 09-ai-guardrails.md (Handoff output)

```markdown
# AI Guardrails

## Must Follow
- Implement Phase 1 pilot slice ONLY first; stop and ask for review.
- Match the locked prototype's layout, vibe, and interactions.
- Use the locked tech stack; do not silently swap.

## Must Ask Before
- Changing data model.
- Changing auth model.
- Changing the design system.
- Diverging from the prototype's layout for any locked screen.
- Adding paid dependencies.
- Building screens beyond Phase 1 scope.

## Must Not Invent
- Real assets (logos, real photos, real testimonials).
- API endpoints not in `04-data-model.md`.
- Database tables not in `04-data-model.md`.
- Credentials, environment variable values, or secrets.

## Missing Asset Behavior
- Use clearly labeled placeholders.
- Ask the user for the asset.
- Use AI-generated draft only when explicitly allowed in
  `05-assets-and-content.md`.

## Scope Boundaries
- Stay within v1 from `00-requirements.md`.
- v1.5 and v2 items are explicitly NOT in scope unless promoted by the
  user.
```
