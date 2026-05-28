---
name: openclaw-ops
description: "Use when operating OpenClaw itself: checking versions, updating the CLI, managing the gateway service, verifying health, and handling restart edge cases after upgrades."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [openclaw, gateway, update, service-management, troubleshooting]
    related_skills: [hermes-agent, codex, opencode]
---

# OpenClaw

## Overview

OpenClaw is an autonomous agent CLI with a long-running gateway service. The recurring operator tasks are: check the installed version, inspect whether an update is available, run the update safely, restart the gateway, and verify that both the CLI and the running gateway are on the expected version.

This skill is for **operating OpenClaw itself**, not for using OpenClaw to complete another coding task.

## When to Use

Use this skill when you need to:
- Check whether OpenClaw is out of date
- Update OpenClaw to the latest stable release
- Restart or verify the OpenClaw gateway service
- Confirm whether a failed-looking update actually succeeded
- Inspect managed-service status after an upgrade

Do **not** use this skill for:
- General npm troubleshooting unrelated to OpenClaw
- Hermes Agent configuration
- Code review or feature work inside a random project repo

## Quick Checks

Start with the live state, not guesses:

```bash
openclaw --version
openclaw update --dry-run
openclaw gateway status --deep
```

If OpenClaw is managed by a user-level systemd service on Linux/WSL, also check:

```bash
systemctl --user status openclaw-gateway.service --no-pager -n 30
```

What these tell you:
- `openclaw --version` → installed CLI version
- `openclaw update --dry-run` → current version, target version, planned actions
- `openclaw gateway status --deep` → service manager, command path, gateway version, connectivity probe, listening port
- `systemctl --user status ...` → whether the service is actually running and recent logs

## Standard Update Workflow

### 1. Confirm the target version

```bash
openclaw --version
openclaw update --dry-run
```

Read the dry-run output for:
- current version
- target version
- whether it will restart the gateway automatically
- whether plugin sync will run

### 2. Run the real update

```bash
openclaw update
```

Typical behavior:
- stops the managed gateway service first
- updates the global package
- runs `openclaw doctor`
- syncs plugins
- restarts the gateway

### 3. Verify the final state explicitly

Do not trust the updater summary alone.

```bash
openclaw --version
openclaw gateway status --deep
openclaw models status
```

If the installation uses a systemd user service:

```bash
systemctl --user status openclaw-gateway.service --no-pager -n 30
```

Success criteria:
- CLI version matches the target version
- gateway version matches the target version
- runtime is `running`
- connectivity probe is `ok`
- expected loopback port is listening
- default model and fallbacks are unchanged

## Restart Workflow

### Preferred path

If OpenClaw is installed with service management, restart the managed service:

```bash
systemctl --user restart openclaw-gateway.service
```

Then verify:

```bash
openclaw gateway status --deep
systemctl --user status openclaw-gateway.service --no-pager -n 20
```

> **Note on probe timeout**: A brief `Connectivity probe: failed / timeout` immediately after restart is expected — the gateway needs a few seconds to warm up. Wait 5–15 seconds and re-run `openclaw gateway status --deep` before treating it as a failure.

### If you only need a health check

```bash
openclaw gateway status --deep
```

This is the fastest ground-truth command because it checks both runtime state and gateway connectivity.

## Common Pitfalls

1. **Treating updater warnings as the final truth.**
   An `openclaw update` run can report a restart/health-check problem even after the core package already upgraded successfully. Always verify with:
   ```bash
   openclaw --version
   openclaw gateway status --deep
   ```

2. **Assuming "port already in use" means the update failed.**
   If the updater says the gateway did not become healthy because the port is already in use, that may simply mean the service is already back up and the probe/restart path got confused. Check the live versions and runtime before attempting rollback.

3. **Skipping a manual restart after an ambiguous post-update state.**
   If the version is updated but the updater exits non-zero or prints a restart warning, do one clean managed restart and re-verify:
   ```bash
   systemctl --user restart openclaw-gateway.service
   openclaw gateway status --deep
   ```

4. **Ignoring plugin/config side effects.**
   OpenClaw updates may sync plugins and may create config backups during rewrite. If behavior changes after update, inspect `~/.openclaw/openclaw.json.bak` and confirm which plugins were installed or updated.

5. **Ignoring stale auth-profile state after a model-route change.**
   If a provider's auth starts failing after an update, inspect both auth profiles and auth state:
   ```bash
   openclaw models auth list
   cat ~/.openclaw/agents/main/agent/auth-profiles.json
   cat ~/.openclaw/agents/main/agent/auth-state.json
   ```
   Watch for `lastGood` still pointing at an older OAuth profile with `expires = 0`, `unknown`, cooldown markers, or prior auth failures. **This pitfall only applies to OAuth providers (e.g. `openai-codex`). Static API key providers (e.g. `minimax`, `minimax-portal`) store the key in `auth-profiles.json` and it survives updates without any re-login.**

6. **Using only process-list checks.**
   A process existing is weaker than `openclaw gateway status --deep`. Prefer the OpenClaw-native status command for the final verification pass.

## Post-Update Model/Auth Triage

If the gateway is up but model behavior changed after an update:

1. Check the active default model and fallbacks:
   ```bash
   openclaw models status
   ```
2. Compare current config with backups:
   ```bash
   diff -u ~/.openclaw/openclaw.json.bak ~/.openclaw/openclaw.json
   ```
   Also inspect older numbered backups if needed (`openclaw.json.bak.2`, `.bak.3`, ...).
3. Check whether `agents.defaults.model.primary` was rewritten and whether `agents.defaults.models.<model>.agentRuntime.id` changed the execution path.
4. Inspect auth health:
   ```bash
   openclaw models auth list
   openclaw models auth order get --provider openai-codex --json
   ```
5. Search logs for auth refresh and fallback signals:
   ```bash
   rg -n "auth refresh|token has been invalidated|Failed to extract accountId|model fallback decision" /tmp/openclaw/openclaw-*.log
   ```
6. If the update changed the default model route, restore the intended default model first, then restart and re-test. The current known-good model is `minimax/MiniMax-M2.7`:
   ```bash
   openclaw models set minimax/MiniMax-M2.7
   systemctl --user restart openclaw-gateway.service
   openclaw models status
   openclaw gateway status --deep
   ```
7. After the restart, confirm the service log actually shows the expected route:
   ```bash
   systemctl --user status openclaw-gateway.service --no-pager -n 25
   ```
8. If auth is still broken after restoring the desired model route, re-run provider login. **Note: this step only applies to OAuth-based providers (e.g. `openai-codex`). If your provider uses a static API key (e.g. `minimax`), the key persists through updates and re-login is not needed.**
   ```bash
   openclaw models auth login --provider openai-codex   # OAuth providers only
   ```
9. After re-login, inspect the resulting profile shape before declaring victory:
   ```bash
   openclaw models auth list
   cat ~/.openclaw/agents/main/agent/auth-profiles.json
   cat ~/.openclaw/agents/main/agent/auth-state.json
   ```

## Reference Notes

- `references/update-and-restart.md` — condensed notes from a real successful upgrade where `openclaw update` returned an unhealthy-restart warning even though the CLI and gateway had already moved to the new version.
- `references/model-route-and-auth-triage.md` — post-update triage for cases where OpenClaw rewrites the default model/provider route and Codex/OpenAI auth starts failing or timing out.

## Verification Checklist

- [ ] `openclaw --version` matches the intended version
- [ ] `openclaw gateway status --deep` shows `Gateway version` matching the CLI
- [ ] `Runtime` is `running`
- [ ] `Connectivity probe` is `ok`
- [ ] Expected listening port is present
- [ ] `openclaw models status` shows default model and fallbacks are unchanged
- [ ] If systemd-managed, `systemctl --user status openclaw-gateway.service` is active
- [ ] If update logs mentioned plugin/config changes, review backups or plugin list before declaring done
