# Plugin removal & stale-state cleanup

Notes from a real maintenance pass (OpenClaw 2026.6.9) where `doctor`/`gateway status`
kept reporting **"Plugin version drift"**, **"conflicting plugin install metadata"**,
and **"Left plugin install index in place"** long after the offending plugins were gone.

Always `openclaw backup create` first (it archives `~/.openclaw`; large because it includes
workspaces — run it in the background and give it >120s). Keep per-file `.bak` copies too.

## Removing a plugin

```bash
openclaw plugins uninstall <id> --force      # --force required; non-TTY uninstall refuses otherwise
openclaw plugins install npm:@openclaw/<id> --force   # reinstall; plain install errors "already exists" if the dir lingers
openclaw gateway restart                     # uninstall/install print "Restart the gateway to apply"
```

Uninstalling a plugin does **NOT** clean up everything. It removes the config entry,
the install record, and the project dir under `~/.openclaw/npm/projects/...`, but it
leaves behind:
- auth profiles the plugin created (see "Removing a provider/Codex" below),
- stale entries in the **install index** (the source of drift/conflict warnings),
- in some cases an older copy in the **legacy shared npm workspace**.

## "Plugin version drift" that won't clear — the records live in THREE places

Official channel plugins (e.g. `discord`, `slack`) can legitimately lag the core version;
`openclaw plugins update <id>` then reports "up to date" at the older version, so the drift
is cosmetic and only matters if you actually use the channel. But if you **uninstalled** a
plugin and drift *still* lists it (often with an even older version, because the check falls
back through sources), the records are stale in up to three layers — clean all of them:

1. **Legacy install index file** — `~/.openclaw/plugins/installs.json`
   - Holds `installRecords` keyed by plugin id with old `resolvedVersion`s.
   - In 2026.6.x this file is **not regenerated** — SQLite is authoritative. Back it up and delete it:
     ```bash
     cp -a ~/.openclaw/plugins/installs.json ~/.openclaw/plugins/installs.json.bak
     rm ~/.openclaw/plugins/installs.json
     ```
   - This also clears **"conflicting plugin install metadata"** and **"Left plugin install index in place"**.

2. **Shared SQLite index** — `~/.openclaw/state/openclaw.sqlite`, table `installed_plugin_index`,
   column `install_records_json` (a JSON blob keyed by plugin id). Prune removed plugins' keys.
   **Stop the gateway first** so it doesn't hold/overwrite the DB:
   ```bash
   openclaw gateway stop
   cp -a ~/.openclaw/state/openclaw.sqlite ~/.openclaw/state/openclaw.sqlite.bak
   python3 - <<'PY'
   import sqlite3, json
   db = '/home/benny/.openclaw/state/openclaw.sqlite'
   c = sqlite3.connect(db)
   (ir_json,) = c.execute("select install_records_json from installed_plugin_index").fetchone()
   ir = json.loads(ir_json)
   for k in ('discord', 'slack'):      # plugins you removed
       ir.pop(k, None)
   import time
   c.execute("update installed_plugin_index set install_records_json=?, updated_at_ms=?",
             (json.dumps(ir), int(time.time()*1000)))
   c.commit(); c.close()
   PY
   openclaw gateway start
   ```

3. **Legacy shared npm workspace** — `~/.openclaw/npm/` (an older install scheme; `package.json`
   lists `@openclaw/<id>` deps and `node_modules/@openclaw/<id>` holds an old copy). Remove the
   plugin there too (keep ones you still use, e.g. codex):
   ```bash
   cd ~/.openclaw/npm
   cp -a package.json package.json.bak
   # edit package.json: delete the @openclaw/<id> entries from "dependencies"
   rm -rf node_modules/@openclaw/<id>
   ```

Then reconcile and verify:
```bash
openclaw plugins registry --refresh
openclaw gateway restart
openclaw gateway status --deep        # "Plugin version drift" should be gone
```

## Removing or keeping a provider / Codex

- The `codex` plugin owns the `openai` (ChatGPT OAuth) provider via the codex-app-server
  (`source=codex-app-server`, `synthetic=plugin-owned`). Uninstalling `codex` drops that
  provider after a gateway restart.
- There is **no `openclaw models auth remove`** command. Auth profiles live in the
  `auth_profile_store` table of `~/.openclaw/agents/main/agent/openclaw-agent.sqlite`
  (older installs used `auth-profiles.json`). An uninstalled provider's OAuth profile lingers
  there until you re-login or edit the store.
- To **keep** openai/codex: `openclaw plugins install npm:@openclaw/codex --force`, restart,
  then refresh the OAuth: `openclaw models auth login --provider openai`. That clears the
  "openai expired" + "legacy Codex OAuth sidecar" warnings.

## `doctor --fix` is conservative

`openclaw doctor --fix` disables unusable skills and migrates some legacy state, but it
deliberately does **not** remove auth profiles or the unreferenced legacy Codex OAuth sidecar
("left in place because external agent dirs may still reference them"). Don't expect it to
zero out everything.

## `gateway install --force`

Regenerates the systemd unit to the current CLI version. Clears "service installed by
older version" and "PATH missing required dirs". The nvm/version-manager warnings remain by
design on a single-nvm WSL host (see SKILL.md pitfall #7).
