---
name: minimax-cli-web-search
description: Web search via MiniMax MCP using a local CLI wrapper (mcporter), with environment preflight, API-key/config checks, and normalized result formatting. Use when tasks require real-time web lookup, source links, quick research, or time-sensitive facts. Prefer this skill over built-in web search tools when MiniMax MCP is available.
---

# MiniMax CLI Web Search

Use this skill to run web search through MiniMax MCP from CLI, then return clean, source-first results.

> ⚠️ **IMPORTANT — 2025-04-12**: The `minimax.web_search` tool does **NOT exist** in the official MiniMax MCP server (`uvx minimax-mcp`). Available tools: `text_to_audio`, `list_voices`, `voice_clone`, `play_audio`, `generate_video`, `query_video_generation`, `text_to_image`, `music_generation`, `voice_design`. This skill will NOT work as intended with the official server — it requires an MCP server that provides a `web_search` tool backed by MiniMax.

## Phase 1: Environment Preparation (must run first)

### 1) mcporter wrapper (required — NOT in PATH by default)

mcporter is installed via `npx` but not in `$PATH`. Create a wrapper:

```bash
cat > ~/.local/bin/mcporter << 'WRAPPER'
#!/bin/bash
exec npx --yes mcporter "$@"
WRAPPER
chmod +x ~/.local/bin/mcporter
```

Verify: `which mcporter` → should return `~/.local/bin/mcporter`

### 2) MiniMax MCP server config

Create `~/.mcporter/mcporter.json` with your API key from `~/.hermes/.env`:

```bash
python3 -c "
import json, re
env = {}
with open('/home/benny/.hermes/.env') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            env[k] = v
key = env.get('MINIMAX_API_KEY', '')
host = env.get('MINIMAX_BASE_URL', 'https://api.minimax.io').replace('/v1', '')
cfg = {'mcpServers': {'minimax': {'command': 'uvx', 'args': ['minimax-mcp'], 'env': {'MINIMAX_API_KEY': key, 'MINIMAX_API_HOST': host}}}}
with open('/home/benny/.mcporter/mcporter.json', 'w') as f:
    json.dump(cfg, f, indent=2)
print('Done')
"
```

### 3) Preflight checks

```bash
mcporter list --json   # should show status: ok for "minimax"
```

If using the wrapper script:

```bash
scripts/minimax_web_search.sh --preflight
```

This verifies:
- `mcporter` exists in PATH
- MiniMax MCP server is discoverable (`mcporter list --json`)
- Server status is healthy (`name=minimax`, `status=ok`)

### 4) If preflight fails, repair by failure type
- `mcporter not found`
  - Install/setup mcporter in PATH.
- `minimax MCP server not ready`
  - Check `config/mcporter.json` includes minimax server.
  - Verify command/transport is valid.
- Auth/API-key related errors
  - Ensure MiniMax API key is configured for the minimax MCP server.
  - Re-run preflight.

### 3) Initiate / smoke test
Run one query after preflight passes:

```bash
scripts/minimax_web_search.sh --query "latest OpenClaw release" --count 3
```

If this returns results, environment is ready.

---

## Phase 2: Search Usage (runtime)

### Quick usage

```bash
scripts/minimax_web_search.sh --query "your query" --count 5
```

### Supported options
- `--query <text>`: required search query
- `--count <n>`: max printed results (default `5`)
- `--freshness <value>`: freshness hint appended to query (optional)
- `--json`: normalized JSON output
- `--raw`: raw tool JSON output
- `--timeout <sec>`: command timeout (default `35`)

### Output contract (default text)
- Show top-N results in order
- For each item: title, URL, snippet, date (when available)
- Keep output concise and directly actionable

### Agent behavior guideline
1. Start with a focused query (3–7 keywords).
2. If low quality, rephrase once with narrower terms.
3. Return key findings + links (no table required).
4. For time-sensitive asks, include time words in query (e.g., `today`, `latest`, date).

---

## Error model (for reliable automation)

Script exit codes:
- `0`: success
- `2`: argument error
- `3`: dependency missing (`mcporter`/`python3`)
- `4`: config/auth issue (MCP server unavailable, API key/auth problems)
- `5`: upstream/runtime/network failure
- `6`: no results (non-fatal)

Treat code `6` as a normal “no match” outcome, not a crash.

---

## Risks and handling

1. **CLI/config drift across machines**
   - Use `--preflight` before first use in a new environment.
2. **API key exposure risk**
   - Never print key values; report only missing/invalid status.
3. **Temporary file safety**
   - Wrapper uses `mktemp` for stderr/output temp files and cleans them with `trap`.
3. **Upstream response variance**
   - Use `--json` normalized output for downstream automation.
4. **Timeout/network instability**
   - Increase `--timeout` and retry with narrower query/count.
5. **Weak relevance**
   - Rephrase query, add concrete entities/time ranges.

---

## Additional reference

- For setup/verification commands and publish readiness checks, read:
  - `references/environment-checklist.md`

## Reference style

When presenting findings, include direct links for verification. Prefer 3–5 high-signal sources over large dumps.
