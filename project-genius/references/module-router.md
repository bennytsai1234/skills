# Module Router

Runs at **Stage 1, Step 1.7**. Decides which Stage 2 blueprint files are
necessary based on product type and MVP scope. Do not ask questions for
inactive modules unless the answer would change scope, architecture, or
delivery order.

Infer as much as possible from Steps 1.1–1.6 before asking. Read the
inferred module list back to the user for confirmation rather than asking
module-by-module.

## Core Modules

Always active:

- product brief, type, scope (`00-requirements.md`)
- user stories and acceptance criteria (part of delivery plan)
- delivery plan (`07-delivery-plan.md`)
- implementation handoff and AI guardrails (`08-handoff.md`, `09-ai-guardrails.md`)

## Frontend Module

Activate when the user wants pages, screens, website UI, app UI, dashboards,
forms, navigation, visual layout, or responsive design.

Outputs:
- `01-design-system.md` — tokens, typography, spacing, components.
- `02-surface-map.md` — experience map, screens, navigation, user journeys.
- `03-interactions.md` — frontend blueprint, per-button/form/state spec.

## Backend Module

Activate when the product needs server logic, persistent data, accounts,
payments, permissions, background work, integrations, email, admin features, or
business rules that should not live only in the browser.

Outputs:
- Part of `04-data-model.md` — service boundaries, auth plan, error handling.

## Data/API Module

Activate when the product needs stored records, CRUD, analytics, search,
external API integration, import/export, webhooks, or a formal contract between
frontend and backend.

Outputs:
- `04-data-model.md` — entities, relationships, permissions, sample records.
- `04b-api-contracts.md` — endpoint shapes, request/response, error cases,
  schema ownership and migration notes.

## Auth and Permission Module

Activate when users log in, roles differ, content is private, admin tools
exist, or data access is user-specific.

Outputs:
- `04c-auth-permissions.md` — auth flow, role matrix, protected routes,
  permission checks, audit notes when relevant.

## Media and Asset Module

Activate when the product uses images, videos, background media, icons, logos,
product screenshots, user uploads, galleries, generated images, audio, fonts,
motion assets, or social sharing previews.

Outputs:
- `05-assets-and-content.md` — media and asset plan, missing asset protocol,
  licensing status, performance and accessibility rules.

## CMS/Content Module

Activate when non-developers need to edit pages, posts, docs, case studies,
product listings, images, videos, or marketing content.

Outputs:
- `05b-cms-content.md` — content model, editorial workflow, SEO and social
  sharing plan, preview/publish workflow.

## Security and Compliance Module

Activate when the project handles:
- payment or money movement.
- financial, healthcare, government, child, biometric, or other regulated data.
- sensitive customer, employee, or privileged operational data.
- auditability, legal retention, high availability, or security review needs.
- explicit "high security", "compliance", or "enterprise" requirements.

Outputs:
- `05c-security-compliance.md` — data classification, threat model, control
  gates, privacy and retention rules, incident and recovery posture.

## Infrastructure Module

Activate when the user wants deployment-ready planning, environment variables,
storage, CDN, monitoring, scheduled jobs, cost awareness, or production
operations.

Outputs:
- `06-tech-stack.md` — framework, database, storage, hosting, deployment,
  environment variable inventory, monitoring and rollback notes.

## Testing Module

Activate when any of these apply:
- The product handles money, health data, or regulated information.
- More than one developer on the team.
- User mentions CI/CD, automated tests, coverage, or QA.
- Complex business rules: permission model, pricing logic, multi-step
  workflows, state machines.
- Downstream coding agent is Claude Code, Codex, or similar autonomous agent.

Outputs:
- `10-testing.md` — test layer priorities, CI gate design, test data strategy.

See `module-testing.md` for the full question tree.

## Analytics Module

Activate when any of these apply:
- User mentions conversion, funnel, retention, DAU, or engagement metrics.
- Product has a CTA, sign-up, purchase, or upgrade flow.
- User mentions a specific analytics tool (GA4, PostHog, Mixpanel, Plausible,
  Amplitude, Segment).
- Product has a marketing site with a primary CTA.
- Product needs to demonstrate value to stakeholders via data.

Outputs:
- `11-analytics.md` — tool selection, primary metrics, event inventory,
  identity strategy, naming convention, privacy/consent decisions.

See `module-analytics.md` for the full question tree.

## Native Behaviors Module

Activate automatically for **Mobile app** and **Desktop app** product types.
Skip for all other types.

The HTML prototype captures visual layout but cannot represent gestures,
haptic feedback, platform-specific transitions, native component behavior,
or OS-level integration. This module fills that gap.

Outputs:
- `03b-native-behaviors.md` — gesture map, haptic feedback spec, native
  component decisions, keyboard behavior, OS integration decisions.

See `modules-native-behaviors.md` for the full question tree.

## Prototype/Mock-Only Mode

When the product type is "Prototype / Mock-only experience", or the user
explicitly wants a prototype only:
- activate Frontend module only unless the UI requires backend assumptions.
- mark all data as mock data.
- still define realistic future data and API assumptions when they affect
  layout, states, or user flows.
- keep the handoff focused on one pilot slice.
- skip Security, Infrastructure, and CMS modules unless the user requests them.
