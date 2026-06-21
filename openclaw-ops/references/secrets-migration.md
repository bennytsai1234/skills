# Secrets migration: plaintext → SecretRef

Notes from migrating OpenClaw 2026.6.9 plaintext secrets to a `file` SecretRef provider
on a single-user WSL host. Goal: clear the `doctor` **Security** warning
("openclaw.json contains plaintext secret-bearing config fields") and get
`openclaw secrets audit --check` to `plaintext=0`.

## Audit first

```bash
openclaw secrets audit --check
```
- Lists `[PLAINTEXT_FOUND]` (config fields + auth-profile keys), `[LEGACY_RESIDUE]`, etc.
- **Exits non-zero when findings exist** — that is normal for `--check`, not an error.
- The `doctor` Security warning only names the `openclaw.json` fields
  (`gateway.auth.token`, `plugins.entries.<p>.config...apiKey`, `channels.<c>.botToken`).
  The auth-profile keys in the sqlite store show up only in `secrets audit`.

## Backends

`env`, `file`, `exec`. On a single-user Linux/WSL box, **`file` is simplest** — no systemd
env wiring, the value just lives in a 0600 JSON file the gateway reads at start.

## Key gotcha: the `file` provider does NOT write values for you

`openclaw secrets configure` maps fields to references and scrubs the source, but for a
file provider it assumes **you manage the file** — it will not copy the current plaintext
value into it. So **pre-populate the JSON file with the current values first**, otherwise
resolution fails after the plaintext is scrubbed.

```bash
# Build ~/.openclaw/secrets.json (mode 600) from current plaintext values.
python3 - <<'PY'
import json, os
cfg = json.load(open('/home/benny/.openclaw/openclaw.json'))
def dig(d, path):
    for k in path.split('.'): d = d[k]
    return d
secrets = {
  "gatewayAuthToken":      dig(cfg, "gateway.auth.token"),
  "tavilyWebSearchApiKey": dig(cfg, "plugins.entries.tavily.config.webSearch.apiKey"),
  "telegramBotToken":      dig(cfg, "channels.telegram.botToken"),
}
p = '/home/benny/.openclaw/secrets.json'
fd = os.open(p, os.O_WRONLY|os.O_CREAT|os.O_TRUNC, 0o600)
json.dump(secrets, os.fdopen(fd, 'w'), indent=2)
PY
```

For auth-profile keys (sqlite), read them from the `auth_profile_store` table of
`~/.openclaw/agents/main/agent/openclaw-agent.sqlite` (`store_json` → `profiles.<id>.key`)
and add them to the same file. Note: `minimax:global.key` and `minimax-portal:global.key`
are typically the **same key**, so store it once and point both at one pointer.

## Run the interactive configure (REQUIRES a TTY)

`openclaw secrets configure` **fails headless** ("requires an interactive TTY"). The agent
cannot drive it — hand the user these steps:

1. provider source `file`, alias `default`, file path `/home/benny/.openclaw/secrets.json`,
   file mode `json`.
2. At "Select credential field", pick the config fields and/or auth-profile `.key` fields
   (skip `.token` and the openai OAuth profile).
3. Map each to provider `default` + a JSON pointer (leading slash):

   | field | pointer |
   |---|---|
   | `gateway.auth.token` | `/gatewayAuthToken` |
   | `plugins.entries.tavily.config.webSearch.apiKey` | `/tavilyWebSearchApiKey` |
   | `channels.telegram.botToken` | `/telegramBotToken` |
   | `profiles.minimax:global.key` | `/minimaxApiKey` |
   | `profiles.minimax-portal:global.key` | `/minimaxApiKey` |

4. Continue/Finish → it backs up, preflights, applies, and scrubs the plaintext.

(Re-running `configure` later reuses the already-configured `default` provider — just
continue to mapping.)

## Verify

```bash
openclaw secrets audit --check   # plaintext=0  (openai OAuth stays as legacy=1, expected)
openclaw secrets reload          # re-resolve refs into the running gateway, no restart needed
openclaw models status           # profiles should read e.g. minimax:global=ref(file:/minimaxApiKey)
openclaw gateway status --deep   # Runtime running / probe ok — proves the gateway resolves the refs
```

`legacy=1` for an openai OAuth profile is expected and out of scope for static SecretRef
migration; it is not plaintext and clears only if you remove that provider.
