---
name: codex-update
description: "Update or diagnose the OpenAI Codex CLI and ChatGPT/Codex Windows desktop app on this controlled Windows environment. Use for CLI update failures (including npm ERR_SSL_WRONG_VERSION_NUMBER on registry.npmjs.org, which also breaks opencodex `ocx update`) or desktop startup failures caused by a missing MSIX/AppX package identity. Do not use for CUA runtime package-resolution failures. Never bypass TLS or change global certificate settings."
---

# Codex CLI and Windows Desktop App Update

在公司管控 Windows 上，處理 Codex CLI 更新或 ChatGPT/Codex Windows 桌面 App 的套件註冊問題；不要修改系統、npm 或 git 的全域設定。

## Mode selection

- CLI version/update failure: follow the workflow below.
- Desktop startup failure mentioning `ChatGPT.exe`, AppX/MSIX, package identity, bootstrap, or `處理程序沒有套件識別資料`: read [references/windows-desktop-app.md](references/windows-desktop-app.md).
- CUA package-resolution failure such as missing `@oai/cua`: use `cua-runtime-repair` instead.

## Quick Run（固定腳本，免逐行讀取）

腳本在本 skill 目錄（`~/skills/codex-update/update-codex.ps1`）：

```powershell
# 以系統管理員身份執行
powershell -NoProfile -ExecutionPolicy Bypass -File "$HOME\skills\codex-update\update-codex.ps1"
```

腳本會自動：檢查目前版本 → 嘗試內建 `codex update` → 失敗且為 npm 安裝時改走內部 Verdaccio 重試 → 仍失敗才降級官方安裝腳本 → 驗證結果。

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

## npm registry TLS failure

Applies to any npm-based update on this machine, including `codex update` of an npm-managed install and `ocx update` (opencodex, `@bitkyc08/opencodex`).

Confirmed root cause (2026-09-23): McAfee Web Gateway rule `1150513_DevSvrRepoNuNpm download package` answers `registry.npmjs.org:443` with a **plaintext HTML block page**, so npm/curl report `ERR_SSL_WRONG_VERSION_NUMBER` / curl exit 35. This is a policy block, not a CA/TLS config problem; never try to bypass it.

1. Confirm the block (use Bash; PowerShell AMSI may block handling the page):

   ```bash
   curl -s -m 10 http://registry.npmjs.org:443/ | grep -o "McAfee Web Gateway"
   ```

2. If the user npm config contains `strict-ssl=false`, remove that user-level override (TLS must stay on). Do not edit `~/.npmrc` `registry` without asking the user.
3. Retry through the internal Verdaccio mirror, set for that one process only:

   ```powershell
   $env:npm_config_registry = "https://ctverdaccio.cotabank.com/"
   npm install -g @openai/codex@latest   # npm-managed Codex CLI
   ocx update                            # opencodex; its transactional updater inherits the env var
   ```

   Check availability first with `npm view <pkg> dist-tags --registry https://ctverdaccio.cotabank.com/`. After `ocx update`, verify with `ocx --version`, `ocx ready --json`, then `ocx sync` (Codex app-server needs a restart via `ocx sync --restart-codex` to show new models; ask first, since it interrupts active turns).
4. For Codex CLI only, if Verdaccio does not work, use the official installer as a one-off HTTPS fallback:

   ```powershell
   powershell.exe -NoProfile -ExecutionPolicy Bypass -Command '$env:CODEX_NON_INTERACTIVE="1"; Invoke-RestMethod https://chatgpt.com/codex/install.ps1 | Invoke-Expression'
   ```

5. The installer can leave an older npm-managed install in place. Verify `Get-Command codex -All` and `where.exe codex`; the newly installed official path must be first. Do not remove the older install automatically unless cleanup is explicitly requested.
6. Confirm recovery with `codex --version`, `codex doctor`, and `npm config get strict-ssl`; the version command and doctor update status must show the newer CLI, and TLS must remain enabled.

## Failure handling

If the update fails, collect the exact error and run `codex doctor`.

If the error is `Get-FileHash is not recognized` (or an equivalent missing-command error) during the official installer’s checksum verification, retry the same official installer in a one-off Windows PowerShell process without the user profile:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command '$env:CODEX_NON_INTERACTIVE="1"; Invoke-RestMethod https://chatgpt.com/codex/install.ps1 | Invoke-Expression'
```

This preserves the installer’s normal HTTPS and checksum verification and does not change PowerShell, system, npm, or git settings. Then run the verification commands again. If the retry fails, retain the exact error, run `codex doctor`, and escalate certificate, proxy, permission, or managed-device failures to IT with the command output. Do not disable TLS validation or use `strict-ssl false`.
