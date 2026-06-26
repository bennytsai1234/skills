<!--
OPTIONAL TEMPLATE — generate ONLY when a project has a real design system to map
AND the user opts in. This is NOT part of the required atlas output shape
(index + module docs + adapter).

Format-only: this adopts the google-labs-code/design.md DOCUMENT FORMAT (YAML token
front-matter + prose rationale, canonical section order). It NEVER requires
installing or running @google/design.md (its CLI / lint / export), so it stays
compatible with no-build and supply-chain-restricted environments.

Normativity follows the project's DECLARED source of truth: if the project declares
its code/CSS/tokens canonical, this front-matter is a MIRROR (regenerate it when the
source changes); only if the project declares this file canonical is it normative.

Replace placeholders, keep the section order, delete these guidance comments.
-->
---
# design.md front-matter — structured design tokens for {{PROJECT_NAME}}.
# Source of truth: {{TOKEN_SOURCE_OF_TRUTH}}  (e.g. a CSS :root block, a tokens
# file, or a theme config). This block MIRRORS that source unless the project
# declares this file canonical. Working language for prose: {{WORKING_LANGUAGE}}.
version: "alpha"
name: "{{PROJECT_NAME}} Design System"
description: "{{ONE_LINE_PRODUCT_AND_STYLE}}"

colors:
  # token-name: "<CSS color: hex / rgb / oklch / named>"  — only REAL tokens from
  # the source of truth; do not invent tokens for component-local hard-coded values.
  primary: "{{COLOR_PRIMARY}}"

typography:
  base:
    fontFamily: "{{FONT_FAMILY}}"
    fontSize: "{{BASE_FONT_SIZE}}"
  # role-name: { fontSize, fontWeight, lineHeight, ... }   # type scale

rounded:
  # scale-level: "<dimension>"

spacing:
  # scale-level: "<dimension | number>"

components:
  # component-name: { backgroundColor, textColor, typography, rounded, padding,
  #                   size, height, width }
  # Valid props ONLY: backgroundColor, textColor, typography, rounded, padding,
  # size, height, width. The schema has NO borderColor / boxShadow / z-index /
  # breakpoint — express those in body prose (sections 5/6), not here.
  # Variants use separate entries: <name>-hover, <name>-active, ...
  # Token references use {path.to.token}, e.g. {colors.primary}.
---

# {{PROJECT_NAME}} Design System

> Format: two-layer google-labs-code/design.md (front-matter tokens + prose
> rationale). Sections 1–8 below follow design.md's canonical order; sections
> outside 1–8 are preserved (design.md keeps unknown sections without error) — use
> them for anything the front-matter schema cannot express.
>
> Source of truth: {{TOKEN_SOURCE_OF_TRUTH}}. Conflicts resolve to the source of
> truth; regenerate the front-matter from it. Format-only — do not introduce
> @google/design.md runtime / CLI / build.

## 1. Overview            <!-- brand, product positioning, style, tech basis, normativity statement -->
## 2. Colors
## 3. Typography
## 4. Layout              <!-- spacing scale, container, vertical rhythm, breakpoints pointer -->
## 5. Elevation & Depth   <!-- shadows, z-index — no front-matter token type, prose only -->
## 6. Shapes              <!-- radii, border strategy — no borderColor prop, prose only -->
## 7. Components
## 8. Do's and Don'ts

<!--
Preserved sections (outside the 1–8 canonical order; design.md keeps them without
error). Add ONLY the ones the project actually needs, e.g.:
Accessibility checklist · Interaction & Motion · Responsive · Iconography ·
Maintenance · Gaps & Open Decisions · and any project-specific layering such as a
per-page override system. Keep such layering in the document; do not hardcode it
into the skill.
-->
