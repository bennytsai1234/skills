# Architecture (of the Skill Itself)

Project Genius is structured around **SDLC Stage 1 (Requirements) + Stage
2 (Design & Prototyping)** with a downstream-agent handoff. It does not
write production code; that is Stages 3-5 (Development, Testing,
Deployment) and belongs to the downstream coding agent (Claude Code,
Codex, Cursor, or similar).

## Core Layers

1. **Product type** — the routing decision. See `product-type-router.md`.
2. **Question trees** — per-type questions for Stage 1 anchor + Stage 2
   surface, interaction, and asset specs. See `type-question-trees.md`.
3. **Convergence mechanisms** — reference pinning, convergence loop,
   pilot-per-lock. See `convergence-protocol.md`.
4. **Confirmation gates** — lock-required field lists per stage. See
   `confirmation-gates.md`.
5. **Core workflow** — the stage-by-stage step list. See
   `core-workflow.md`.
6. **Architecture reasoning** — the irreversible-decisions analysis used
   during Stage 1 Step 1.6. See `architecture-reasoning.md`.
7. **Output templates** — Markdown templates for the final artifacts.
   See `output-templates.md`.
8. **Handoff guardrails** — protocol for passing to the downstream
   agent. See `handoff-guardrails.md`.

## Core Principle

> **The locked visual prototype is the spec. Documents are metadata.**

The skill achieves mental-image fidelity not by writing better documents
but by iterating on a tangible HTML/CSS prototype with the user until
every screen matches what the user pictures in their head. Documents are
extracted from the locked prototype, not the other way around.

This is the key architectural shift from older blueprint-style tools
that treated the document as the primary artifact and the prototype as
an afterthought.

## Stage Boundaries

| Stage | Owner | Primary artifact |
|-------|-------|------------------|
| 1. Requirements | Project Genius | `00-requirements.md` |
| 2. Design & Prototyping | Project Genius | `prototype/` (locked) + supporting docs |
| 3. Development | Downstream coding agent | Implementation |
| 4. Testing | Downstream coding agent / user | Tests, fixes |
| 5. Deployment | Downstream / user | Live product |

Project Genius hands off after Stage 2 sign-off. The handoff package
includes the prototype, supporting docs, a delivery plan, and guardrails.

## v2 Depth and Limits

Strongest for:
- Frontend-facing web products.
- Full-stack web products.
- SaaS dashboards.
- Marketing sites.
- Content sites and blogs.
- Backend / API services.
- Browser extensions.
- Desktop apps (Electron-style or web-based).
- AI-coding-agent handoff with prototype-first spec.

Partial depth for:
- Native mobile apps (covers the surface design; native-specific
  patterns like deep platform integration may need specialist
  follow-up).
- Realtime collaboration (CRDT / OT specifics).
- Infrastructure-heavy platforms.
- ML training pipelines.
- Embedded / hardware-coupled systems.
- High-regulation domains (finance, health) — still produces docs but
  flags compliance depth limits.

For partial-depth products, still produce Stage 1 + Stage 2 with
explicit "depth limit" markers in the documents.

## What Is NOT Project Genius's Job

- Writing application code.
- Choosing or running tests.
- Configuring deployment.
- Setting up CI/CD.
- Implementing accessibility audits.
- Performance profiling.
- Security penetration testing.

These belong to Stages 3-5 and to specialist downstream agents or
people.

## Compatibility With Codebase Atlas

When Codebase Atlas is also in use:
- Atlas scans repositories and executes phases.
- Project Genius produces the upstream blueprint that Atlas executes.
- Documents live under `docs/genius/`; prototype lives at the repo root
  so the user can open it in a browser.
- Atlas owns the executable phase plan; Project Genius owns the spec
  the phase plan implements.
