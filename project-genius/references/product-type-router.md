# Product Type Router

This file handles product type routing. Product type is the first decision
(Step 1.1) and determines question trees and prototype skeleton. Module
activation (Step 1.7) is a separate downstream decision — see
`module-router.md` for that. Each type maps to its own question tree and
its own first-pass prototype skeleton. See `type-question-trees.md` for
per-type details.

## When the Type Router Runs

In **Stage 1, Step 1.1**, immediately after the Session Opening
introduction. The router never runs in Stage 2 — by then the type is
locked.

## The 15 Recognized Types

**Frontend-led:**

1. **Web app / SaaS dashboard** — authenticated app with primary working
   surface, navigation chrome, multiple connected screens. Examples:
   Linear, Notion, Stripe Dashboard, Intercom.
2. **Admin system / Internal tool** — role-gated ops surface; data tables,
   bulk actions, audit logs, admin-only screens. Examples: Retool, internal
   CMS, ops dashboards.
3. **Marketing site / Landing page** — narrative scroll; hero / social
   proof / pricing / CTA funnel. Examples: stripe.com homepage,
   linear.app marketing, vercel.com.
4. **Portfolio / Personal site** — showcase, bio, project listing, contact.
   Examples: personal portfolio, agency site.
5. **Content site / Blog / Documentation** — list/detail templates,
   taxonomy, search, OG previews. Examples: nytimes.com,
   tailwindcss.com docs, paulgraham.com.
6. **Ecommerce / Catalog** — product listing, cart, checkout, order
   management. Examples: Shopify storefronts, custom catalog.
7. **Media-heavy product** — video/audio streaming, gallery, upload-centric,
   media pipeline. Examples: YouTube-like, photo gallery app.
8. **Prototype / Mock-only experience** — visual mockup only; no real
   backend; all data mocked.

**Service / platform-led:**

9. **API service / Backend** — endpoints, auth model, request/response
   shapes, error model, webhooks. Examples: Stripe API, Twilio API,
   GitHub API.
10. **Event-driven system / Workflow engine** — queues, state machines,
    long-running jobs, recoverable execution. Examples: n8n-style workflow,
    job queue system.
11. **Integration / Third-party connector** — glue between external APIs,
    webhooks in/out, sync pipelines. Examples: Zapier-style connector,
    CRM sync.

**Other surfaces:**

12. **Browser extension** — popup, sidebar, content script injection,
    toolbar icon states. Examples: 1Password, Grammarly, Bitwarden.
13. **Mobile app** *(shallow depth)* — native or hybrid; tab/stack/drawer
    navigation; touch-first; native components. Examples: Things, Headspace,
    Instagram. Flag depth limit explicitly in outputs.
14. **Desktop app** *(shallow depth)* — window/tray/menu bar, OS integration,
    file associations, global shortcuts. Examples: Raycast, Linear desktop,
    Things desktop. Flag depth limit explicitly in outputs.
15. **Mixed / other** — combine the relevant trees. Examples: SaaS with
    marketing site + admin panel + extension + mobile.

## Routing Logic

1. Ask: "What kind of product is this?" Present the 8 candidates as a
   choice list. Let the user combine.
2. If the user is unsure, ask follow-ups:
   - Does it run inside a browser, on a phone, on a desktop, or as a
     server?
   - Do users log in?
   - Is there a primary working surface (app) or is it mostly content
     (marketing / blog)?
   - Does it expose machine-readable endpoints (API)?
3. Resolve to one or more types.
4. Set the corresponding question tree from `type-question-trees.md` as
   the active branch.

## Mixed Products

When the user genuinely has multiple types:

- Identify the **primary** surface (the one a user spends most time on).
- Identify the **adjacent** surfaces.
- Activate the question tree for each. Run them in priority order
  (primary first).
- Maintain a separate `prototype/<surface>/` directory per surface so
  locks do not collide.
- Use a shared design system unless the user explicitly wants different
  visual languages per surface (rare; typical for marketing vs app).

## Type Affects More Than Questions

The chosen type determines:

- **Stage 1 questions**: per-type anchor questions added to the standard
  set.
- **Stage 2 surface map shape**: pages vs screens vs sections vs
  endpoints.
- **Stage 2 prototype skeleton**: file layout under `prototype/`.
- **Stage 2 interaction checklist**: which buttons/forms/gestures
  matter.
- **Stage 2 asset list**: marketing needs hero images, mobile needs app
  icons, etc.
- **Handoff content**: pilot slice choice, guardrails specific to type.

## Type Detection Heuristics from Initial Description

When the user gives a one-line description, infer probable types:

| Signal in description | Probable type |
|-----------------------|---------------|
| "dashboard for X" | Web app / SaaS |
| "landing page", "promote", "convert", "leads" | Marketing |
| "blog", "articles", "docs", "knowledge base" | Content |
| "API", "SDK", "developer", "webhook", "integrate" | API service |
| "extension", "chrome", "addon", "inject" | Browser extension |
| "desktop", "menu bar", "tray", ".app", ".exe" | Desktop |
| "app", "iOS", "Android", "mobile-first" | Mobile |
| "platform" without other signals | Usually Web app, ask to clarify |

**Inference is a starting point, not a lock.** Always read the inferred
type back to the user and confirm before proceeding.

## Out of Scope for v2

Project Genius v2 provides partial depth for:
- Real-time collaborative systems (CRDT, OT, presence) — produce brief
  with shallow architecture, recommend specialist follow-up.
- Game development.
- Embedded / hardware-coupled software.
- ML/AI training pipelines (the model side; consuming an LLM API is in
  scope).
- Infrastructure / DevOps tools.

For these, still produce Stage 1 + a high-level Stage 2 sketch, but
flag the depth limit explicitly in the output documents.
