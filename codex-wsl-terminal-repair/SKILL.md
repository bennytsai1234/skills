---
name: codex-wsl-terminal-repair
description: Repair and configure the integrated terminal in Codex Desktop for Windows when using WSL or PowerShell, including terminals that close immediately, fail to open, or need to work from every project and folder.
---

# Codex Desktop Terminal Repair

Use the selected terminal mode globally. Preserve unrelated Codex settings and project state.

## WSL mode

1. Resolve the active Windows Codex home and Ubuntu distribution.
2. Run:

   ```bash
   /home/benny/skills/codex-wsl-terminal-repair/scripts/install-wsl-terminal-fix.sh
   python3 /home/benny/skills/codex-wsl-terminal-repair/scripts/configure-terminal-mode.py \
     --config /mnt/c/Users/benny/.codex/config.toml \
     --mode wsl
   ```

3. Keep these global values under `[desktop]`:

   ```toml
   runCodexInWindowsSubsystemForLinux = true
   integratedTerminalShell = "wsl"
   ```

4. Do not replace WSL with PowerShell as a fallback.
5. Do not change `defaultTerminalLocation` unless the user requests a panel location.
6. Open one new integrated terminal in the current Codex task.
7. Confirm all of the following:
   - the terminal tab remains open;
   - the process is an interactive shell inside the selected WSL distribution;
   - `SHELL` is `/bin/bash` or the user's configured Linux shell;
   - the terminal working directory matches the requested folder;
   - `/usr/bin/git --version` succeeds;
   - the installed compatibility layer is `/usr/local/libexec/codex-wsl-sh-compat`;
   - `/bin/sh` delegates ordinary commands to `/usr/bin/dash`.

The WSL compatibility installation is distribution-wide and is not scoped to a repository, project, task ID, terminal session ID, drive, or working directory.

## PowerShell mode

Run:

```bash
python3 /home/benny/skills/codex-wsl-terminal-repair/scripts/configure-terminal-mode.py \
  --config /mnt/c/Users/benny/.codex/config.toml \
  --mode powershell
```

Keep these global values under `[desktop]`:

```toml
runCodexInWindowsSubsystemForLinux = false
integratedTerminalShell = "powershell"
```

Open one new integrated terminal and confirm that it remains open, uses PowerShell, and starts in the requested folder.

## Switching modes

- Keep the WSL compatibility layer installed when switching to PowerShell so WSL mode remains ready for later use.
- Apply only the two mode keys shown above.
- Preserve project registrations, task bindings, terminal placement, permissions, providers, models, MCP servers, and all unrelated configuration.
- Reload Codex Desktop only when the agent runtime itself does not adopt a changed execution mode live.
- Stop after the selected terminal opens successfully and the mode and working directory are confirmed.
