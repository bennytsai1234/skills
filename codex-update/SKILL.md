---
name: codex-update
description: "Update or diagnose the OpenAI Codex CLI on this controlled Windows environment. Use for version checks, CLI updates, and update failures. Never bypass TLS or change global certificate settings."
---

# Codex CLI Update

在公司管控 Windows 上，只更新 Codex CLI；不要修改系統、npm 或 git 的全域設定。

## Quick Run（固定腳本，免逐行讀取）

```powershell
# 以系統管理員身份執行
powershell -NoProfile -ExecutionPolicy Bypass -File "path\to\update-codex.ps1"
```

或直接在存放腳本的目錄下：

```powershell
.\update-codex.ps1
```

腳本會自動：檢查目前版本 → 嘗試內建 `codex update` → 失敗時降級官方安裝腳本 → 驗證結果。

## Manual Steps（手動逐步操作）

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

If the update fails, collect the exact error and run `codex doctor`.

If the error is `Get-FileHash is not recognized` (or an equivalent missing-command error) during the official installer’s checksum verification, retry the same official installer in a one-off Windows PowerShell process without the user profile:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command '$env:CODEX_NON_INTERACTIVE="1"; Invoke-RestMethod https://chatgpt.com/codex/install.ps1 | Invoke-Expression'
```

This preserves the installer’s normal HTTPS and checksum verification and does not change PowerShell, system, npm, or git settings. Then run the verification commands again. If the retry fails, retain the exact error, run `codex doctor`, and escalate certificate, proxy, permission, or managed-device failures to IT with the command output. Do not disable TLS validation or use `strict-ssl false`.
