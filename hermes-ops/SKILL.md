---
name: hermes-ops
description: "Use when operating Hermes Agent itself: checking the version, updating from upstream, running doctor/doctor --fix, installing the browser stack, setting tokens, managing the gateway service, and telling apart real fixables from by-design 'optional integration not configured' doctor noise."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, agent, update, doctor, service-management, troubleshooting]
    related_skills: [openclaw-ops]
---

# Hermes Ops

## Overview

Hermes Agent is a Python AI assistant (checkout at `~/.hermes/hermes-agent`, launched via
`~/.local/bin/hermes`) with a long-running messaging gateway. The recurring operator tasks
are: check the version, update from upstream git, run `doctor`, fix the handful of *real*
warnings, and — importantly — recognise which warnings are **by-design informational noise**
so you don't chase them forever.

This skill is for **operating Hermes itself**, not for using Hermes to complete another task.
For the sibling agent, see `openclaw-ops`.

## When to Use

- Check whether Hermes is behind upstream and update it safely
- Run `hermes doctor` and fix config/dependency warnings
- Install or repair the browser automation stack (agent-browser + Chromium)
- Set tokens/keys (e.g. `GITHUB_TOKEN`) or understand "not configured" warnings
- Back up / restore the Hermes home, or inspect the gateway service

Do **not** use this skill for: OpenClaw operations (use `openclaw-ops`), or generic Python/npm
troubleshooting unrelated to Hermes.

## Quick Checks

```bash
hermes --version      # version, upstream commit, "Up to date" or "N commits behind — run 'hermes update'"
hermes status         # component/gateway/tool status
hermes doctor         # full diagnostics (see warning taxonomy below)
```

## Update Workflow

```bash
hermes update --check        # is an update available? (no changes)
hermes update                # interactive: pulls git, reinstalls deps, builds web UI,
                             #   syncs bundled skills, migrates config, restarts gateway
hermes update --yes          # non-interactive: auto-yes config migration + stash restore;
                             #   API-key entry is skipped (run 'hermes config migrate' for those)
```

Useful flags: `--no-backup` / `--backup` (a pre-update backup runs by default), `--branch NAME`.

What a real update does (observed jumping v0.16.0 → v0.17.0, ~387 commits, cleanly):
- `git pull` + dependency reinstall, rebuilds the web UI,
- syncs bundled skills (user-modified ones are kept; `hermes skills list-modified` to inspect),
- **migrates the config format** (e.g. v29 → v30) — this also clears the
  "Config version outdated" doctor warning,
- drains and restarts the `hermes-gateway` service.

Verify afterwards: `hermes --version` should read **"Up to date"**, then `hermes doctor`.

## doctor & doctor --fix

```bash
hermes doctor                  # diagnose
hermes doctor --fix            # auto-fix what it can (config migrate, etc.)
hermes doctor --ack <ID>       # acknowledge a security advisory so it stops banner-nagging
```

## Doctor Warning Taxonomy — what to fix vs what to ignore

The single most important thing about `hermes doctor`: **most ⚠ are advisories for optional
integrations you simply haven't configured, not failures.** Do not try to drive them to zero
on a box that doesn't use those integrations.

**By-design / informational (leave them unless you actually use the integration):**
- **Auth Providers "not logged in"** — Nous Portal, Google Gemini OAuth, MiniMax OAuth, xAI OAuth.
  Hardcoded per-provider checks; the only way to clear one is to actually log in. Not gated by
  whether you use it.
- **Tool Availability "missing <KEY>" / "system dependency not met"** — e.g. `discord`,
  `x_search`, `moa`, `spotify`, `homeassistant`, `computer_use`, `video_gen`, `browser-cdp`,
  `hermes-yuanbao`. The doctor checks the deps of **every registered toolset** regardless of
  enable/disable. **Verified:** `hermes tools disable <tool>` does **NOT** silence these — it
  only changes what the model is offered, not the dependency check. Only configuring the
  integration clears the row.
- **`docker not found`**, **`OpenRouter API (not configured)`** — optional.

**Actually fixable:**
- **Config version outdated** → `hermes update` (migrates during update) or `hermes config migrate`.
- **agent-browser not installed** → see "Browser stack" below.
- **npm workspace vulnerability** (e.g. `ui-tui ... high`) → clears via the lockfile bump that
  `hermes update` performs (it's build-time tooling, not runtime).
- **No `GITHUB_TOKEN`** (skills hub 60 req/hr limit) → add `GITHUB_TOKEN=...` to `~/.hermes/.env`.

## Browser stack (agent-browser + Chromium)

The `browser` tool can show ✓ while the doctor still warns **"agent-browser not installed
(run: npm install)"** — the tool is registered but its Node backend isn't present, so it
silently fails at runtime. The doctor looks for `~/.hermes/hermes-agent/node_modules/agent-browser`.

```bash
cd ~/.hermes/hermes-agent
npm install                          # installs agent-browser (a declared dependency) into node_modules
./node_modules/.bin/agent-browser install   # downloads the Playwright-managed Chromium (slow, ~hundreds of MB)
```

Verify: `hermes doctor` should show **"agent-browser (Node.js) ✓"** and **"Playwright Chromium ✓"**.

## Tokens & config

```bash
hermes config path     # config.yaml location
hermes config env-path # .env location (~/.hermes/.env)
```
Put provider keys / `GITHUB_TOKEN` in `~/.hermes/.env` (mode 600). After rotating a leaked
token, replace the line directly in `.env` rather than echoing the new value where it could be
logged.

## Backup / Restore

```bash
hermes backup                  # writes hermes-backup-<date>.zip to $HOME (excludes the hermes-agent checkout)
hermes import <backup.zip>     # restore
```
`hermes update` also takes a pre-update backup by default. Take one before any risky change.

## Gateway service

Hermes runs a `hermes-gateway` systemd user service. `doctor` confirms **systemd linger** is
enabled (so it survives logout). `hermes update` drains and restarts it automatically; use
`hermes status` to see live component state.

## Common Pitfalls

1. **Chasing optional-integration warnings to zero.** They are advisories; `hermes tools
   disable` does not silence them. Configure the integration or accept the ⚠.
2. **Assuming `browser` works because doctor shows the tool ✓.** Check for the
   "agent-browser not installed" / "Playwright Chromium" rows — install the backend.
3. **Running `hermes update` headless without `--yes`.** It will block on interactive prompts.
4. **Forgetting that config migration happens *inside* `hermes update`.** If you see a
   "config outdated" warning, an update usually fixes it without a separate step.

## Verification Checklist

- [ ] `hermes --version` reads "Up to date"
- [ ] `hermes doctor` shows no *fixable* issues (config current, browser stack present, no npm vulns)
- [ ] Remaining ⚠ are only optional-integration advisories you intentionally don't use
- [ ] `GITHUB_TOKEN` set in `~/.hermes/.env` if you use the skills hub
- [ ] Gateway service active (systemd linger enabled); `hermes status` healthy
