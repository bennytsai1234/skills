---
name: codex-update
description: "Update the OpenAI Codex CLI on this controlled Windows environment using the official installer (the built-in `codex update` is unreliable here)."
---

# Codex CLI Update (Windows)

在這台 Windows 更新 Codex CLI 的正確步驟。不要用內建 `codex update`，直接跑官方安裝腳本。

## 更新

```powershell
$env:PSModulePath += ";$env:WINDIR\System32\WindowsPowerShell\v1.0\Modules"
powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://chatgpt.com/codex/install.ps1 | iex"
```

跑完出現 `Codex CLI <version> installed successfully.` 即成功。

## 驗證

```powershell
& "$env:LOCALAPPDATA\Programs\OpenAI\Codex\bin\codex.exe" --version
```

安裝位置：`$env:LOCALAPPDATA\Programs\OpenAI\Codex\bin\codex.exe`（安裝時已加入 PATH）。

## 注意

- 不要關閉 TLS 驗證（如 `strict-ssl false`），不要改全域設定。
- 安裝來源固定為官方 `https://chatgpt.com/codex/install.ps1`。
