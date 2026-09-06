# Upgrade migration deadlock (2026.7.x → 2026.8.x): crash-loop where `doctor --fix` cannot fix itself

## Scenario

`openclaw update` moved the core package from `2026.7.1-2` to `2026.8.1`. The updater
exited **non-zero (`ERROR`)** with `Reason: openclaw doctor`, but the core package had
already swapped:

```
✓ global update      Before: 2026.7.1-2  After: 2026.8.1
✓ global install swap
✗ openclaw doctor    Legacy exec approvals exist ... Run `openclaw doctor --fix` ...
Restarted managed gateway service after failed update.
```

After the auto-restart the gateway went into a **systemd crash-loop** (`NRestarts` climbing,
port `18789` never listening). `openclaw gateway status --deep` showed `Runtime: running`
but `Connectivity probe: failed (ECONNREFUSED)` and a persistent `npm install` child.

## Why it deadlocks (the keystone)

There were three stacked blockers, and the tool's own repair entry point was jammed by the
deepest one:

1. **Strict plugin verification (2026.8 is fail-closed).** A plugin declared
   `enabled: true` in `openclaw.json` → `plugins.entries` **but never actually installed**
   (here: `duckduckgo`) is only a *warning* in 2026.7, but a **fatal startup error** in
   2026.8: `OpenClaw plugin verification failed; refusing to report the gateway ready`.
   Installed-but-external plugins (`codex`, `deepseek`, `tavily`) additionally needed
   **capability re-consent** and were on the old version (version drift).

2. **Legacy `exec-approvals.json` makes `doctor` throw.** The `core/doctor/security`
   health check **throws** `ExecApprovalsMigrationRequiredError` when it sees the legacy
   `~/.openclaw/exec-approvals.json` (`version: 1`). Because the health-check phase runs
   *before* the repair phase, `openclaw doctor --fix` (and `--fix --non-interactive`, and
   `openclaw update repair`) **abort before applying any migration** — including the ones
   they are being asked to run. `approvals get` / `approvals set` throw the same error, so
   the approvals CLI cannot self-migrate either. Classic chicken-and-egg.

3. **Legacy session store blocks gateway startup.** Independently, gateway startup fails
   with `Gateway failed to start: Legacy session store requires migration:
   .../sessions/sessions.json. Run "openclaw doctor --fix" ...` — a migration that is
   *also* gated behind the jammed `doctor --fix`.

So: **exec-approvals is the keystone.** While the legacy file is present, `doctor --fix`
throws, so the session-store / catalog / heartbeat / TOOLS.md migrations never run, so the
gateway can never reach a healthy boot. Every error message says "Run `openclaw doctor
--fix`" and running it does nothing.

## Recovery procedure (verified)

Always `openclaw backup create` (or copy `openclaw.json` + `exec-approvals.json`) first.

```bash
# 0. Stop the crash-loop so restarts stop fighting the repair
systemctl --user stop openclaw-gateway.service
systemctl --user reset-failed openclaw-gateway.service
```

**1. Clear the fail-closed plugin blocker.**
A declared-but-not-installed plugin cannot be removed with `plugins disable` (that command
only acts on *installed* plugins and returns `Plugin not found`). Remove the dangling entry
from `openclaw.json` → `plugins.entries` directly (delete the key), or install it for real
with `--accept-capabilities` if you actually want it.

**2. Converge the real external plugins to the new version + re-consent capabilities.**

```bash
openclaw plugins update codex   --accept-capabilities
openclaw plugins update tavily  --accept-capabilities
# A pinned plugin will NOT move on a bare id (it reports the pin and exits 0 without
# updating). Pass the explicit spec@version to follow the registry:
openclaw plugins update @openclaw/deepseek-provider@2026.8.1 --accept-capabilities
```

**3. Break the keystone: move the legacy exec-approvals file aside so `doctor` stops
throwing.** The migration target is the SQLite table `exec_approvals_config`
(`~/.openclaw/state/openclaw.sqlite`, `config_key = current`); `detectLegacyExecApprovals`
keys off the *presence* of the JSON file, so renaming it makes the security check pass:

```bash
mv ~/.openclaw/exec-approvals.json ~/.openclaw/exec-approvals.json.legacy-moved-$(date +%Y%m%d-%H%M%S)
openclaw doctor --fix          # now runs; cascades every pending migration
```

`doctor --fix` then migrates session store, provider catalogs, config-audit log, workspace
attestation/setup, heartbeat cadence (creates the cron monitor + folds `HEARTBEAT.md`), and
`TOOLS.md → AGENTS.md`, all into `openclaw.sqlite`, and restarts the service.

**4. Verify a clean boot.**

```bash
openclaw gateway status --deep     # CLI+Gateway = target, Runtime running, probe ok, port listening
systemctl --user show openclaw-gateway.service -p ActiveState -p NRestarts   # active, NRestarts=0
openclaw doctor --lint             # security ERROR gone; only benign warnings remain
```

## Why moving the exec-approvals file aside is safe

The **effective** exec policy is driven by `openclaw.json` → `tools.exec`
(`mode`/`security`/`ask`), **not** by the allowlist file. Confirm with `openclaw approvals
get --json` after boot: with `ask: off` the `effectivePolicy` still resolves to
`security=full / ask=off`, identical to before. The moved file only held cached
`allow-always` grants, which are inert when `ask: off`. If a host actually relies on
prompted approvals (`ask: on`), re-import the policy after boot with
`openclaw approvals set --file <backup>` (needs the gateway running), otherwise the moved
file is just a historical backup with no live reference.

## Gotchas seen

- `openclaw doctor --fix` printing the legacy-exec-approvals line and exiting is **not** a
  fix — check the file's `mtime`/`version` to confirm nothing changed; it means the throw
  aborted the run.
- A brief `restart-loop breaker tripped: N unclean boot(s)` in the journal is the crash
  loop, not a new fault — stop the service, fix the root cause, then start once.
- Model route is untouched by this: compare `agents.defaults.model` in `openclaw.json`
  against `openclaw.json.bak` to prove the update didn't rewrite `primary`/`fallbacks`.
