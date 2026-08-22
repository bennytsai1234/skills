# Skills

This repository is the canonical home for reusable Codex and agent skills.

## Structure

- Each skill lives in its own directory.
- Each skill directory should include a `SKILL.md` file.
- Supporting scripts, references, assets, and metadata should stay inside the skill directory they belong to.

## Maintenance

- Treat `/home/benny/skills` as the source of truth for long-lived skills.
- Prefer relative paths inside skill documentation and scripts.
- Keep tool-specific mount points or compatibility links outside this repository unless they are part of a skill itself.
- Commit changes here when adding, updating, or removing skills.

## Current Skills

- `codebase-atlas`
- `codebase-memory`
- `codex-update`
- `compass` — 把偏掉的對話拉回正確方向
- `hermes-ops`
- `mmx-cli`
- `openclaw-ops`
- `blueprint` — 把已確認內容整理成可執行方案
- `project-genius`
- `summarize-project-work`
- `video-to-text`
- `windows-cjk-font-substitution`
