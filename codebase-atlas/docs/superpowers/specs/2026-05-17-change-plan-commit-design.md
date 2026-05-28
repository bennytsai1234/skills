# Design: Change Plan Commit

**Date:** 2026-05-17  
**Status:** approved

## Overview

After the user confirms a Before/After (or Decision Gate), the skill writes a structured plan file to `docs/changes/` and commits it to git before touching any source files. This creates a persistent, auditable record of every confirmed change intent — separate from the implementation commit.

## Why

The Before/After gate is ephemeral: it exists only in the conversation. Once the session ends, there is no record of what was agreed upon or why. Writing and committing the plan before implementation makes the intent durable and queryable via git history.

## Changes Required

### 1. New file: `assets/templates/change_plan.md`

A template that defines the structure of every generated plan file.

**Fields:**

| Field | Content |
|-------|---------|
| `{{SLUG}}` | kebab-case identifier derived from the task description |
| `{{DATE}}` | ISO date (YYYY-MM-DD) |
| `{{TASK_TYPE}}` | one of the ten internal task types |
| `{{BEFORE}}` | the confirmed Before statement |
| `{{AFTER}}` | the confirmed After statement |
| `{{SCOPE}}` | list of files and modules expected to change |
| `{{VALIDATION_STEPS}}` | minimum verification steps for the chosen task type |
| `{{ROLLBACK}}` | rollback path for the chosen task type |

**Output location:** `docs/changes/{{DATE}}-{{SLUG}}.md`

### 2. Modified file: `assets/templates/change_workflow.md`

In the External Reporting Layer, insert a new step between step 2 (wait for user confirmation) and the existing step that begins implementation:

> **Step 3 (new): Write and commit the change plan.**
> After the user confirms the Before/After (or Decision Gate choice), generate the plan file at `docs/changes/YYYY-MM-DD-<slug>.md` using `assets/templates/change_plan.md`. Run `git add` and `git commit` with message `plan: <slug>`. Do not edit any source files until the commit succeeds.

The existing step numbering after this point shifts by one.

## Scope

- `assets/templates/change_plan.md` — new file
- `assets/templates/change_workflow.md` — one insertion in External Reporting Layer

`SKILL.md` is not changed. Core Rules do not need updating because this behavior lives in the change workflow template.

## Applies To

All confirmed changes routed through the change workflow, regardless of size. Small bug fixes produce a short plan (Before/After + one or two files). Complex changes produce a fuller plan (Decision Gate outcome + broader scope list).

## Git Commit Convention

Plan commits use the prefix `plan:` so they are visually distinct in git log from implementation commits.

Example:
```
plan: fix-null-pointer-in-auth-middleware
```

## What This Does Not Change

- The Before/After gate format
- The Decision Gate format
- Atlas update conditions
- Verification and rollback rules per task type
