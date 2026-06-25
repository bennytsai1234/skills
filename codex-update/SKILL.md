---
name: codex-update
description: "Update the OpenAI Codex CLI on a controlled Windows (PowerShell) environment, including the -NoProfile workaround for the broken built-in `codex update`."
---

# Codex CLI Update (Windows / 受控環境)

在銀行受控 Windows 環境更新 Codex CLI 的標準作法與已知踩雷點。
所有指令以官方安裝腳本為準，不引入第三方相依、不關閉 TLS 驗證。

## TL;DR

```powershell
# 1) 直接用官方安裝腳本（與 `codex update` 同一支），但加上 -NoProfile
powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://chatgpt.com/codex/install.ps1 | iex"

# 2) 驗證
& "$env:LOCALAPPDATA\Programs\OpenAI\Codex\bin\codex.exe" --version
```

安裝位置：`C:\Users\<user>\AppData\Local\Programs\OpenAI\Codex\bin\codex.exe`
（亦即 `$env:LOCALAPPDATA\Programs\OpenAI\Codex\bin`，安裝時已加入 PATH。）

## 為什麼不用內建 `codex update`

`codex update` 內部會呼叫：

```
powershell -ExecutionPolicy Bypass -c '$env:CODEX_NON_INTERACTIVE=1; irm https://chatgpt.com/codex/install.ps1 | iex'
```

注意它呼叫的是 **Windows PowerShell 5.1**，而且 **沒有 `-NoProfile`**。
在本機受控環境下，使用者的 PowerShell 設定檔（profile）載入後會干擾模組
自動載入，導致安裝腳本在驗證雜湊那步報錯：

```
The term 'Get-FileHash' is not recognized as the name of a cmdlet ...
Error: ... install.ps1 | iex` failed with status exit code: 1
```

→ 這不是網路、權限或 TLS 問題。`Get-FileHash` 本身存在
（`Microsoft.PowerShell.Utility`，5.1 即內建，LanguageMode=FullLanguage），
只是 profile 阻擋了模組自動載入。加上 `-NoProfile` 即可繞過。

## 診斷指令（確認是 profile 問題而非環境壞掉）

```powershell
# 5.1 下、不載 profile，確認 Get-FileHash 與 LanguageMode 正常
powershell -NoProfile -Command '$PSVersionTable.PSVersion.ToString(); ' +
  'Get-Command Get-FileHash | Select Name,Source; ' +
  '"LanguageMode=" + $ExecutionContext.SessionState.LanguageMode'
```

若 `-NoProfile` 下正常、不加時失敗，就確定是 profile 干擾，直接用 TL;DR 的指令更新即可。

## 注意事項（受控環境）

- 這是會對外下載並安裝執行檔的動作；務必經使用者明確同意後再執行。
- 不要為了「修好」而關閉 TLS 驗證（如 `strict-ssl false`）或改動全域設定。
- 安裝腳本來源固定為官方 `https://chatgpt.com/codex/install.ps1`。
- `irm | iex` 前那段若看到 `$env:CODEX_NON_INTERACTIVE=1` 被外層 shell
  先展開而報的紅字，屬無害雜訊，只要最後出現
  `Codex CLI <version> installed successfully.` 即成功。

## 更新後驗證

```powershell
& "$env:LOCALAPPDATA\Programs\OpenAI\Codex\bin\codex.exe" --version
# 視需要：codex doctor   # 檢查安裝、設定、登入與執行環境健康度
```
