# Post-update model route + auth triage

Use when OpenClaw updates successfully but model behavior changes afterward — especially when requests start timing out, falling back unexpectedly, or using a different provider/runtime path than before.

## Durable pattern

A real post-update failure mode is:

- gateway restarts fine
- CLI and gateway versions match
- default model is silently rewritten
- auth still exists, but the runtime path changed
- requests begin failing on auth refresh or falling back to a secondary model

## Concrete indicators

### Config rewrite pattern

Inspect these files:

- `~/.openclaw/openclaw.json`
- `~/.openclaw/openclaw.json.bak`
- older backups like `~/.openclaw/openclaw.json.bak.2`, `.bak.3`, `.bak.4`

In the observed case:

- older backups showed:
  - `openai-codex/gpt-5.5`
  - then `codex/gpt-5.4`
- current config showed:
  - `agents.defaults.model.primary = openai/gpt-5.4`
- while `agents.defaults.models.openai/gpt-5.4.agentRuntime.id = codex`

That means the apparent model name changed less than the actual execution route.

## Commands to run

```bash
openclaw models status
openclaw config get agents.defaults.model.primary
openclaw config get agents.defaults.models
openclaw models auth list
openclaw models auth order get --provider openai-codex --json
```

If needed:

```bash
diff -u ~/.openclaw/openclaw.json.bak ~/.openclaw/openclaw.json
python - <<'PY'
import json, pathlib
base=pathlib.Path('~/.openclaw'.replace('~', str(pathlib.Path.home())))
for name in ['openclaw.json.bak.2','openclaw.json.bak.3','openclaw.json.bak.4','openclaw.json.last-good','openclaw.json']:
    p=base/name
    if not p.exists():
        continue
    obj=json.loads(p.read_text())
    print(name, obj.get('agents',{}).get('defaults',{}).get('model',{}).get('primary'))
PY
```

## Auth-state pitfall

Inspect:

- `~/.openclaw/agents/main/agent/auth-profiles.json`
- `~/.openclaw/agents/main/agent/auth-state.json`

Observed durable pattern:

- a stale profile like `openai-codex:<email>` can remain in `auth-profiles.json`
- `expires` may be `0` / unknown
- `auth-state.json` can still mark that stale profile as `lastGood`
- a healthier profile like `openai-codex:default` may exist at the same time
- `openclaw models status` may show the default profile as healthy while the stale email-scoped profile still appears as `unknown` and keeps old failure/cooldown metadata around

This matters because log analysis can look contradictory unless you inspect both files.

## Log signatures worth grepping

```bash
rg -n "auth refresh|token has been invalidated|Failed to extract accountId|model fallback decision|cooldown" /tmp/openclaw/openclaw-*.log
```

Observed signatures:

- `auth refresh request timed out after 10s`
- `Your authentication token has been invalidated. Please try signing in again.`
- `Failed to extract accountId from token`
- fallback from the requested GPT-5 route to `minimax/MiniMax-M2.7`

## Recommended operator sequence

1. Verify whether the update rewrote the default model route.
2. Verify whether the current model uses a different runtime path (`agentRuntime.id = codex`).
3. Check for stale `openai-codex` auth profiles and `lastGood` pointers.
4. Restore the intended default model first if the route was rewritten.
5. Restart gateway and re-test.
6. Only then re-login the provider if auth is still bad.

## Known-good first repair

If the operator expected the older route, restore the exact model family they had before the rewrite instead of guessing.

In the observed single-user case behind this note, the only correct route was `openai-codex/gpt-5.4`. Nearby-looking alternatives such as `codex/gpt-5.4` and `openai/gpt-5.4` were not acceptable substitutes. If you already know the sole known-good route for the machine, restore that exact string first and do not experiment.

### Case A: old route was `codex/gpt-5.4`

```bash
openclaw models set codex/gpt-5.4
systemctl --user restart openclaw-gateway.service
openclaw models status
openclaw gateway status --deep
```

### Case B: old route was `openai-codex/gpt-5.4`

```bash
openclaw models set openai-codex/gpt-5.4
systemctl --user restart openclaw-gateway.service
openclaw models status
openclaw gateway status --deep
systemctl --user status openclaw-gateway.service --no-pager -n 25
```

In the observed case, this produced a service log line like:

```text
[gateway] agent model: openai-codex/gpt-5.4
```

That is stronger verification than checking only `openclaw config get agents.defaults.model.primary`.

Then, if failures persist:

```bash
openclaw models auth login --provider openai-codex
```

## Post re-login verification

Do not assume the provider will recreate `openai-codex:default`.

In one successful cleanup + re-login sequence:

- all `openai-codex` profiles were removed first
- the operator logged in again
- the resulting healthy state contained exactly one OAuth profile:
  - `openai-codex:<email>`
- there was no `openai-codex:default`
- `auth-state.json` contained no `lastGood.openai-codex`
- `openclaw models status` reported the profile as `ok`
- validity was about 10 days, not 7

That means the post-login success criteria should be:

- exactly one `openai-codex` OAuth profile is present
- its status is `ok`
- there is no stale duplicate `openai-codex` profile
- there is no stale `lastGood` / cooldown / failure entry tied to a removed profile
- default model remains `openai-codex/gpt-5.4`

Recommended checks:

```bash
openclaw models auth list
openclaw models status
cat ~/.openclaw/agents/main/agent/auth-profiles.json
cat ~/.openclaw/agents/main/agent/auth-state.json
systemctl --user status openclaw-gateway.service --no-pager -n 25
```

Interpretation rule:

- single healthy email-scoped profile = acceptable
- multiple `openai-codex` profiles with mixed expiry/state = suspicious
- fixed assumptions like "it always expires in 7 days" = wrong; trust the live expiry instead

## Why this belongs in the skill

This is not a one-off broken machine story. The durable lesson is the triage order:

- confirm config rewrite
- confirm runtime path
- inspect auth-state/profile split
- restore intended model route
- only then refresh login
