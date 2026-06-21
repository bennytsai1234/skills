---
name: skill-installer
description: "Use when the user asks to install / add a Claude Code skill (\"install this skill\", \"add this skill\", \"安裝這個 skill\", \"幫我裝 skill\"). Installs by SYMLINKING the skill folder from /home/benny/skills (the canonical git source of truth) into ~/.claude/skills/<name> — never by copying — so `git pull` updates propagate automatically. Handles the varying source layouts and the /plugin exception for marketplace-packaged collections."
version: 1.0.0
metadata:
  type: tooling
---

# Skill Installer

## Overview

When the user asks to install a Claude Code skill, install it by **symlinking** the skill's
directory (the folder that directly contains `SKILL.md`) into `~/.claude/skills/<name>`:

```bash
ln -sfn /home/benny/skills/<...>/<skill> ~/.claude/skills/<skill>
```

**Do NOT copy.** `/home/benny/skills` is a git repo and the canonical source of truth for
long-lived skills; symlinking means a later `git pull` propagates updates automatically with
no reinstall.

## When to Use

- The user says "install this skill", "add this skill", "安裝這個 skill", "幫我裝這個 skill",
  or points at a folder / repo containing a `SKILL.md` and wants it active in Claude Code.

Do **not** use this skill for installing plugins via the interactive `/plugin` command — see
the exception below.

## Procedure

1. **Locate the folder that directly contains `SKILL.md`.** Source layouts vary:
   - Standalone skills: `SKILL.md` at the folder root.
   - Collections: nested under `skills/<name>/` or `.claude/skills/<name>/`.
   Symlink the exact folder that holds `SKILL.md`, not its parent.

2. **Create the symlink:**
   ```bash
   ln -sfn /home/benny/skills/<path-to-skill> ~/.claude/skills/<name>
   ```
   `-s` symlink, `-f` force-replace an existing link, `-n` treat an existing link-to-dir as a
   file so it gets replaced rather than nested inside.

3. **Verify the link resolves:**
   ```bash
   cat ~/.claude/skills/<name>/SKILL.md >/dev/null && echo OK
   ```
   `~/.claude/skills/<name>/SKILL.md` must be readable through the link. Relative symlinks
   *inside* a skill (e.g. `data`, `scripts`, `../../docs/...`) still resolve because the OS
   follows the real path.

## Exception — marketplace-packaged plugin collections

Collections that ship a `ckm:`-namespaced multi-skill plugin with a
`.claude-plugin/marketplace.json` (e.g. `ui-ux-pro-max-skill`) are **not** symlinked.
Install them via:

```
/plugin marketplace add <path>
/plugin install <plugin>@<marketplace>
```

The interactive `/plugin` command **cannot be run by Claude** — tell the user to run these
themselves.

## Notes

- To see what is currently installed: `ls -la ~/.claude/skills/` (symlinks show their target).
- This skill itself was created by converting a long-lived feedback memory into a skill.
