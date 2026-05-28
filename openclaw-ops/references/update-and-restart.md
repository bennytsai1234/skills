# OpenClaw update + restart edge case

## Scenario

A managed OpenClaw installation was updated from `2026.5.7` to `2026.5.12` using:

```bash
openclaw update
```

The updater reported:
- core update succeeded
- plugins synced
- restart step reported: `Gateway did not become healthy after restart`
- diagnostic note: `Port 18789 is already in use`

## What actually mattered

Ground-truth verification showed the update had succeeded:

```bash
openclaw --version
openclaw gateway status --deep
systemctl --user status openclaw-gateway.service --no-pager -n 40
```

Observed final state:
- CLI version: `2026.5.12`
- Gateway version: `2026.5.12`
- Runtime: `running`
- Connectivity probe: `ok`
- Listening on `127.0.0.1:18789`

## Reliable recovery pattern

If `openclaw update` exits with a restart-health warning but the installation may already be upgraded:

1. Check the actual installed version:
   ```bash
   openclaw --version
   ```
2. Check gateway state and connectivity:
   ```bash
   openclaw gateway status --deep
   ```
3. If versions are updated but the state feels ambiguous, do one clean managed restart:
   ```bash
   systemctl --user restart openclaw-gateway.service
   ```
4. Re-run verification:
   ```bash
   openclaw gateway status --deep
   systemctl --user status openclaw-gateway.service --no-pager -n 20
   ```

## Extra note

During the update, OpenClaw also:
- synced plugins
- wrote a config backup at `~/.openclaw/openclaw.json.bak`

If behavior changes after update, inspect the backup and plugin state rather than assuming the upgrade itself failed.
