---
name: openclaw-update
description: Safely update and repair OpenClaw on Benny's machine. Use when the user asks to update OpenClaw, repair OpenClaw after an update, fix Telegram/gateway breakage, remove duplicate OpenClaw installs, or re-point the user service to the nvm-managed install.
metadata: {"clawdbot":{"emoji":"🦞","requires":{"bins":["openclaw","npm","systemctl"]},"os":["linux"]}}
---

# OpenClaw Update

Use this skill when OpenClaw needs to be updated or repaired on this machine.

## Machine Rule

This machine uses exactly one supported OpenClaw install:

- `nvm` Node path: `/home/benny/.nvm/versions/node/v24.14.1/...`

Do not keep parallel OpenClaw installs under these paths:

- `~/.local/bin/openclaw`
- `~/.local/lib/node_modules/openclaw`
- `/usr/bin/openclaw`
- `/bin/openclaw`
- `/usr/lib/node_modules/openclaw`

Different binaries will share the same `~/.openclaw` state directory and can corrupt gateway, model, and session state.

## Required Workflow

1. Inspect the current state first:

```bash
which openclaw
openclaw --version
type -a openclaw
npm config get prefix
systemctl --user status openclaw-gateway --no-pager
```

2. Run the repair/update script:

```bash
bash ~/skills/tooling/openclaw/openclaw-update/scripts/update-openclaw.sh
```

3. Validate after the script completes:

```bash
openclaw --version
which openclaw
type -a openclaw
openclaw health
systemctl --user status openclaw-gateway --no-pager
openclaw infer model run --model minimax-portal/MiniMax-M2.7 --prompt 'Reply with exactly OK.' --json
```

## What the Script Does

- Updates the `nvm`-managed OpenClaw package to latest
- Removes duplicate `~/.local` and system-level OpenClaw installs if present
- Rewrites `~/.config/systemd/user/openclaw-gateway.service` to point at the `nvm` install
- Reloads and restarts the user service
- Clears stale provider cooldown state from `~/.openclaw/agents/main/agent/auth-profiles.json`
- Prints final verification output

## If Telegram Still Fails

Check these in order:

1. `systemctl --user status openclaw-gateway --no-pager`
2. `openclaw health`
3. `openclaw infer model run --model minimax-portal/MiniMax-M2.7 --prompt 'Reply with exactly OK.' --json`
4. `~/.openclaw/agents/main/agent/auth-profiles.json` for stale `usageStats` entries like `model_not_found`

## Notes

- Do not change `~/.openclaw` to a different state directory on this machine.
- Do not reintroduce a `~/.npmrc` prefix override for OpenClaw updates.
- If the Node version changes in `nvm`, update the hardcoded path in both the skill and the service file before rerunning the workflow.
