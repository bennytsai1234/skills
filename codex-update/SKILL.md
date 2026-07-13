---
name: codex-update
description: "Update or diagnose the OpenAI Codex CLI on this controlled Windows environment. Use for version checks, CLI updates, and update failures. Never bypass TLS or change global certificate settings."
---

# Codex CLI Update

在公司管控 Windows 上，只更新 Codex CLI；不要修改系統、npm 或 git 的全域設定。

## Update

1. Check the installed CLI:

   ```powershell
   codex --version
   codex doctor
   ```

2. Run the built-in updater:

   ```powershell
   codex update
   ```

3. Verify the result:

   ```powershell
   codex --version
   codex doctor
   ```

## Failure handling

If the update fails, collect the exact error and run `codex doctor`. Do not disable TLS validation, use `strict-ssl false`, or change npm, git, or system certificate settings. Escalate certificate, proxy, permission, or managed-device failures to IT with the command output.
