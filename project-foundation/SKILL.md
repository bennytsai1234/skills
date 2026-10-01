---
name: project-foundation
description: "Initialize or standardize the minimal documentation of a software repository. Use when the human asks to set up a new repo's project docs, reorganize an existing repo into the standard AGENTS.md / README.md / optional DESIGN.md shape, or repair stale/duplicated project guidance. Keep only facts that code and git history cannot show; fold useful content from other guidance docs into these files and remove the redundant ones."
---

# Project Foundation

Create the smallest set of project documents that helps humans and coding agents work in the repository. Code and git history are the primary source of truth; documents only hold what they cannot show.

This skill is for repository documentation, not product ideation.

Read `references/document-contract.md` before creating or reorganizing files.

## Target shape

```text
AGENTS.md
README.md
DESIGN.md   # only when the repository has a real UI/design system
```

Do not create other guidance documents such as `DEVELOPMENT.md` or `docs/architecture.md`. Module structure, data flow and file layout are read from the code; they go stale when written down.

## Existing repository workflow

1. Read applicable global/project instructions.
2. Inventory current root docs and `docs/` content before writing.
3. Classify useful content using `references/document-contract.md`.
4. Keep correct project-specific facts that code and git cannot show. Merge duplicates into one canonical location.
5. Fold the still-useful parts of `DEVELOPMENT.md`, `docs/architecture.md` and similar guidance docs into `AGENTS.md` or `README.md`, then remove those files. Drop content that only restates what the code shows.
6. Update stale wording when repository evidence proves the current state changed.
7. Do not delete ecosystem-required files (LICENSE, tool configuration) or unrelated documents such as specs, changelogs or `docs/changes/` work history.
8. Create missing foundation files with repository-grounded content.
9. Decide whether `DESIGN.md` is justified; skip it when it would be empty or speculative.
10. Validate links and eliminate contradictory duplicate instructions.

## New repository workflow

1. Create `AGENTS.md` and `README.md` with the known project conventions and commands; use explicit TODOs for genuinely undecided values rather than inventing them.
2. Create `DESIGN.md` only when a UI/design system or confirmed prototype already exists.

## Design decision

`DESIGN.md` means product visual/design system guidance for coding agents: visual direction, tokens, typography, layout, components, interaction conventions, and do/don't guidance that actually exists in the product.

Do not use it for one feature proposal or a backend implementation plan. If the repository has no meaningful UI, omit it.

## Delivery

Follow current human instructions and repository `AGENTS.md` for commit/push behavior. Report which documents were created, merged, removed, or intentionally omitted and why.
