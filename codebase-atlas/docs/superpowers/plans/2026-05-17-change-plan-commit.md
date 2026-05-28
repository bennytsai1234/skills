# Change Plan Commit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** After a user confirms a Before/After or Decision Gate, automatically write a structured plan file to `docs/changes/` and git commit it before any source files are touched.

**Architecture:** Two file changes: (1) a new `change_plan.md` template that defines the plan file structure, and (2) a one-step insertion in `change_workflow.md`'s External Reporting Layer that generates and commits the plan file post-confirmation.

**Tech Stack:** Markdown templates with `{{PLACEHOLDER}}` substitution convention (matches existing template style in this repo).

---

### Task 1: Create `assets/templates/change_plan.md`

**Files:**
- Create: `assets/templates/change_plan.md`

- [ ] **Step 1: Verify the placeholder convention used in existing templates**

  Run:
  ```bash
  grep -n '{{' /home/benny/skills/codebase-atlas/assets/templates/change_workflow.md | head -10
  ```
  Expected: lines showing `{{ATLAS_TITLE}}`, `{{REPORTING_LEVEL}}`, `{{DELIVERY_POLICY}}` — confirms double-brace style is correct.

- [ ] **Step 2: Create the change_plan.md template**

  Write `/home/benny/skills/codebase-atlas/assets/templates/change_plan.md` with this exact content:

  ```markdown
  # Change Plan: {{SLUG}}

  **Date:** {{DATE}}
  **Task Type:** {{TASK_TYPE}}

  ## Before

  {{BEFORE}}

  ## After

  {{AFTER}}

  ## Scope

  {{SCOPE}}

  ## Validation Steps

  {{VALIDATION_STEPS}}

  ## Rollback

  {{ROLLBACK}}
  ```

  Field guide (for the agent filling this template):
  - `{{SLUG}}`: kebab-case label derived from the task (e.g., `fix-null-pointer-auth`)
  - `{{DATE}}`: ISO date YYYY-MM-DD of the confirmed change
  - `{{TASK_TYPE}}`: one of: bug, feature, optimization, refactor, release, dependency, migration, config, hotfix, cleanup
  - `{{BEFORE}}`: the confirmed Before statement verbatim
  - `{{AFTER}}`: the confirmed After statement verbatim
  - `{{SCOPE}}`: bullet list of files and modules expected to change
  - `{{VALIDATION_STEPS}}`: the minimum verification steps for the chosen task type (from change_workflow Internal Task Types)
  - `{{ROLLBACK}}`: the rollback path for the chosen task type (from change_workflow Internal Task Types)

- [ ] **Step 3: Verify the file was created correctly**

  Run:
  ```bash
  cat /home/benny/skills/codebase-atlas/assets/templates/change_plan.md
  ```
  Expected: all 7 `{{PLACEHOLDER}}` fields present, no missing sections.

- [ ] **Step 4: Commit**

  ```bash
  cd /home/benny/skills/codebase-atlas
  git add assets/templates/change_plan.md
  git commit -m "feat: add change_plan template for post-confirmation plan commits"
  ```

---

### Task 2: Insert the plan-commit step into `change_workflow.md`

**Files:**
- Modify: `assets/templates/change_workflow.md` lines 106–119 (External Reporting Layer)

- [ ] **Step 1: Confirm exact current content of External Reporting Layer**

  Run:
  ```bash
  sed -n '106,120p' /home/benny/skills/codebase-atlas/assets/templates/change_workflow.md
  ```
  Expected output:
  ```
  ## External Reporting Layer

  1. If Decision Gate triggers matched, present the Decision Gate format first.
     Wait for the user to choose before continuing.
  1. Confirm with the user using the Before / After format below.
  1. Wait for explicit user confirmation before editing any files.
  1. After confirmation, implement the change.
  ...
  ```

- [ ] **Step 2: Replace the External Reporting Layer block**

  Replace the current External Reporting Layer (lines 106–119) with the version below, which inserts the new step 4 between "Wait for explicit user confirmation" and "After confirmation, implement the change":

  ```markdown
  ## External Reporting Layer

  1. If Decision Gate triggers matched, present the Decision Gate format first.
     Wait for the user to choose before continuing.
  1. Confirm with the user using the Before / After format below.
  1. Wait for explicit user confirmation before editing any files.
  1. Write the change plan and commit it before touching source files:
     - Fill `assets/templates/change_plan.md` with the confirmed Before, After,
       task type, expected file scope, validation steps, and rollback path.
     - Save to `docs/changes/{{DATE}}-{{SLUG}}.md` (create `docs/changes/` if
       it does not exist).
     - Run `git add docs/changes/{{DATE}}-{{SLUG}}.md` and
       `git commit -m "plan: {{SLUG}}"`.
     - Do not edit any source files until this commit succeeds.
  1. After the plan is committed, implement the change.
  1. Run the minimum verification listed for the chosen task type. Include the
     verification result in the user-facing report. If verification fails, do
     not claim completion; either fix and re-verify, or report the failure
     honestly and ask the user how to proceed.
  1. Validate the affected behavior and boundaries.
  1. Finish with one plain-language sentence describing what changed and how it
     was verified.
  ```

- [ ] **Step 3: Verify the insertion is correct**

  Run:
  ```bash
  sed -n '106,125p' /home/benny/skills/codebase-atlas/assets/templates/change_workflow.md
  ```
  Expected: the new step 4 block (`Write the change plan and commit it`) appears between "Wait for explicit user confirmation" and "After the plan is committed, implement the change." Confirm total step count is now 7 (was 6).

- [ ] **Step 4: Verify no other sections were accidentally changed**

  Run:
  ```bash
  git diff /home/benny/skills/codebase-atlas/assets/templates/change_workflow.md
  ```
  Expected: diff shows only the External Reporting Layer block changed. No changes to Internal Reasoning Layer, Internal Task Types, Reporting Rules, Before/After Format, Decision Gate, Atlas Update Conditions, or Delivery Policy sections.

- [ ] **Step 5: Commit**

  ```bash
  cd /home/benny/skills/codebase-atlas
  git add assets/templates/change_workflow.md
  git commit -m "feat: write and commit change plan after user confirmation"
  ```
