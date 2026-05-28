# Frontend Blueprint Rules

Deep reference used during Stage 2 Steps 2.3 (surface map), 2.4
(per-screen iteration), and 2.5 (per-interaction micro-locks). The
new flow does not produce a separate "frontend blueprint" document — these
rules feed `prototype/` and the per-screen sections of `02-surface-map.md`
and `03-interactions.md`.

Frontend plans must follow the product essence and architecture reasoning. Do
not design a page in a way that contradicts the chosen rendering model, state
model, media strategy, or data/API boundary.

## Page or screen specification

For each page or screen define:
- route or screen name.
- role in the product.
- user intent.
- sections in order.
- components.
- required data.
- user interactions.
- responsive behavior.
- loading, empty, error, and success states.
- accessibility notes.
- v1/v1.5/v2 priority.

## Section specification

For each important section define:
- purpose.
- content elements.
- actions.
- media assets.
- state dependencies.
- implementation notes.
- acceptance criteria.

## Design consistency

All frontend plans must reference the design system and media plan. Do not create page-specific visual styles unless they extend declared tokens.

## Mock data

If backend is inactive, define mock data shapes so the coding agent can build UI without inventing arbitrary structures.

Mock data must be labeled as mock. If the shape is inferred from screenshots,
sample content, or reference products, mark it as inferred in the output
document's `Sources & Confidence` block.
