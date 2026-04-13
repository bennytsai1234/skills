#!/usr/bin/env bash
set -euo pipefail

NODE_ROOT="/home/benny/.nvm/versions/node/v24.14.1"
NODE_BIN="$NODE_ROOT/bin/node"
NPM_BIN="$NODE_ROOT/bin/npm"
OPENCLAW_BIN="$NODE_ROOT/bin/openclaw"
OPENCLAW_DIST="$NODE_ROOT/lib/node_modules/openclaw/dist/index.js"
SERVICE_FILE="$HOME/.config/systemd/user/openclaw-gateway.service"
AUTH_FILE="$HOME/.openclaw/agents/main/agent/auth-profiles.json"

if [[ ! -x "$NPM_BIN" ]]; then
  echo "[ERROR] nvm npm not found at: $NPM_BIN" >&2
  exit 1
fi

echo "==> Updating nvm-managed OpenClaw"
"$NPM_BIN" install -g openclaw@latest --prefix "$NODE_ROOT"

echo "==> Removing duplicate user/system installs"
rm -rf "$HOME/.local/lib/node_modules/openclaw" "$HOME/.local/bin/openclaw"
sudo rm -rf /usr/lib/node_modules/openclaw /usr/bin/openclaw /bin/openclaw || true

echo "==> Writing user service"
mkdir -p "$(dirname "$SERVICE_FILE")"
cat > "$SERVICE_FILE" <<SERVICE
[Unit]
Description=OpenClaw Gateway ($("$OPENCLAW_BIN" --version | awk '{print $2}'))
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=$NODE_BIN $OPENCLAW_DIST gateway --port 18789
Restart=always
RestartSec=5
TimeoutStopSec=30
TimeoutStartSec=30
SuccessExitStatus=0 143
KillMode=control-group
Environment=HOME=$HOME
Environment=TMPDIR=/tmp
Environment=NODE_EXTRA_CA_CERTS=/etc/ssl/certs/ca-certificates.crt
Environment=OPENCLAW_STATE_DIR=$HOME/.openclaw
Environment=PATH=$NODE_ROOT/bin:$HOME/.local/bin:$HOME/.local/share/pnpm:/usr/local/bin:/usr/bin:/bin
Environment=OPENCLAW_GATEWAY_PORT=18789
Environment=OPENCLAW_SYSTEMD_UNIT=openclaw-gateway.service
Environment="OPENCLAW_WINDOWS_TASK_NAME=OpenClaw Gateway"
Environment=OPENCLAW_SERVICE_MARKER=openclaw
Environment=OPENCLAW_SERVICE_KIND=gateway
Environment=OPENCLAW_SERVICE_VERSION=$($OPENCLAW_BIN --version | awk '{print $2}')

[Install]
WantedBy=default.target
SERVICE

echo "==> Clearing stale provider cooldowns"
python3 - <<'PY'
import json
from pathlib import Path
p = Path("/home/benny/.openclaw/agents/main/agent/auth-profiles.json")
if p.exists():
    obj = json.loads(p.read_text())
    obj.pop("usageStats", None)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")
PY

echo "==> Restarting gateway service"
systemctl --user daemon-reload
systemctl --user restart openclaw-gateway

echo "==> Verification"
"$OPENCLAW_BIN" --version
which openclaw || true
type -a openclaw || true
systemctl --user status openclaw-gateway --no-pager | sed -n '1,12p'
openclaw health
openclaw infer model run --model minimax-portal/MiniMax-M2.7 --prompt 'Reply with exactly OK.' --json
