# Handoff and Guardrails

Use this file at the end of Stage 2 (when sign-off is approved) and
whenever the user asks how to pass the blueprint to a coding agent.

## Core Philosophy

**The locked prototype is the spec.** Supporting documents describe the
prototype; they do not replace it. If the downstream coding agent's
output diverges from the locked prototype, the agent MUST stop and ask.

Project Genius covers SDLC Stage 1 and Stage 2 only. Handoff hands work
to the downstream agent for Stages 3-5 (development, testing,
deployment).

## Single Source of Truth Order

When documents conflict, follow this priority:

1. **`prototype/`** — the locked HTML/CSS files. Highest authority.
2. **`01-design-system.md`** — tokens.
3. **`04-data-model.md`** — entities, API contracts.
4. **`03-interactions.md`** — per-button, per-form, per-state behavior.
5. **`02-surface-map.md`** — navigation, screen relationships.
6. **`00-requirements.md`** — context, user, problem, MVP scope.
7. **`06-tech-stack.md`** — implementation choices.
8. **`05-assets-and-content.md`** — voice, assets.
9. **`07-delivery-plan.md`** — phasing.

If two artifacts contradict, the higher-priority one wins. If the
prototype contradicts a doc, the prototype wins. If the user's verbal
direction contradicts the prototype, the agent stops and asks the user
to update the prototype.

## Pilot Slice (Required)

The downstream agent MUST implement a pilot slice first, before any
broader build phase.

### For frontend-heavy products (Web app / SaaS / Mobile / Marketing / Content / Extension / Desktop)

Pilot = one fully locked screen, re-implemented in the chosen stack,
visually matching `prototype/[screen].html` and behaviorally matching
`03-interactions.md` for that screen.

For SaaS, the pilot is usually the post-login landing or the primary
working surface.

For marketing sites, the pilot is usually the hero section + first
below-fold section.

For mobile, the pilot is usually one tab's home view including modal /
sheet interactions.

### For full-stack products

Pilot = one vertical slice including:
- One UI screen.
- One data entity wired end-to-end.
- One API endpoint or server action.
- One success state and one error state.
- Auth check (if relevant).

### For API / backend products

Pilot = one fully implemented endpoint plus its persistence path,
auth/permission branch (if relevant), and contract tests or request
examples.

## Stop Rule

The downstream coding agent MUST stop after the pilot slice and ask for
user review. It MUST NOT continue building all phases automatically.

After pilot approval, phase by phase, with stop points between phases
unless the user explicitly grants extended autonomy.

## Acceptance Checklist (per phase)

The downstream agent verifies before declaring a phase done:

- Scope match: only the screens / endpoints in this phase's scope.
- Prototype fidelity: locked screens match visually within reasonable
  rendering differences.
- Design token usage: no ad-hoc styles outside the token system.
- Component consistency: shared components stay shared.
- Interactions match `03-interactions.md` for in-scope items.
- Data and API aligned with `04-data-model.md`.
- Auth and permission behavior matches.
- Error, empty, loading states present.
- Responsive behavior present where required.
- Accessibility basics (labels, focus order, contrast).
- No invented assets, endpoints, credentials, services.
- No silent dependency additions.

## Guardrails — The Downstream Agent MUST NOT

- Invent real assets (logos, photos, testimonials, brand marks).
- Invent API endpoints not in `04-data-model.md`.
- Silently change tech stack from `06-tech-stack.md`.
- Redesign the visual language after pilot approval.
- Change high-cost architecture decisions (data model, auth model,
  rendering model, sync model) without confirmation.
- Add features outside v1 scope.
- Ignore missing requirements (e.g. skip permission checks because the
  doc didn't spell it out for every page).
- Build all screens before pilot approval.
- Convert mock data into production data without explicit permission.

## Guardrails — The Downstream Agent MUST Ask Before

- Changing data model.
- Changing auth model.
- Changing storage strategy.
- Replacing the locked design system or its tokens.
- Using external paid services.
- Adding paid dependencies.
- Skipping a documented state (empty / loading / error).
- Choosing a library or pattern that contradicts
  `06-tech-stack.md`.

## Atlas Handoff (Optional)

When Codebase Atlas is part of the workflow:
- Place the blueprint documents under `docs/genius/`.
- Keep `prototype/` outside `docs/` so the coding agent can run it in a
  browser easily.
- Keep delivery phases independently executable.
- Map every phase to user story IDs and acceptance criteria.
- Let Atlas scan the repository and execute one phase at a time.
- Do not create Atlas docs manually; Atlas owns its own repo map and
  workflows.

## Resuming Handoff

If the downstream coding agent crashes mid-phase or the session is
resumed later:

- Re-read `07-delivery-plan.md` to see which phase is in progress.
- Verify the pilot slice still matches the prototype before continuing.
- If the user has revised the prototype since the last build, surface
  the diff and ask before continuing.
