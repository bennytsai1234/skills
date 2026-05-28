# Project Genius

Project Genius is a software product planning skill that covers SDLC
Stage 1 (Requirements) and Stage 2 (Design & Prototyping). It does not
write production code; the downstream coding agent (Claude Code, Codex,
Cursor, or similar) handles Stages 3-5.

The goal is **mental-image fidelity**: when the downstream agent finishes
building, the running product should match what the user originally
pictured in their head. Project Genius achieves this by treating a
locked visual prototype — not the documents — as the primary spec.

## What It Produces

Stage 1 output:
- `00-requirements.md`

Stage 2 outputs (after the iterative prototype is locked):
- `prototype/` — the locked HTML/CSS prototype, primary source of truth
- `01-design-system.md` — tokens
- `02-surface-map.md` — screens / sections / endpoints
- `03-interactions.md` — per-button, per-form, per-state behavior
- `04-data-model.md` — entities, API contract (when relevant)
- `05-assets-and-content.md` — voice, asset inventory
- `06-tech-stack.md` — stack choices

Handoff outputs:
- `07-delivery-plan.md`
- `08-handoff.md`
- `09-ai-guardrails.md`

## Core Mechanisms

- **Reference Pinning Protocol** — forbid adjective-only answers for
  visual / interaction / voice decisions; force concrete reference
  products.
- **Convergence Loop** — propose 2-3 candidates, user picks/refines,
  iterate until lock.
- **Pilot-Per-Lock** — every lock produces a tangible HTML/CSS artifact.
- **Confirmation Gates** — lock-required fields per stage prevent
  premature output.

## Type Routing

Stage 1 routes by product type. Different types use different question
trees: Web app / SaaS dashboard, Mobile app, Marketing site, Content
site, API service, Browser extension, Desktop app, or mixed.

## Handoff

After Stage 2 sign-off, Project Genius hands the locked prototype +
supporting docs + delivery plan + guardrails to the downstream coding
agent. The agent implements a pilot slice first, stops for user review,
then scales the confirmed pattern.

When used with Codebase Atlas, Project Genius is the upstream planning
phase and Atlas is the downstream execution phase.
