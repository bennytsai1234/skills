---
name: codex-update
description: "Update the OpenAI Codex CLI on a controlled Windows environment, including the PSModulePath fix for the broken built-in `codex update` (Get-FileHash not recognized)."
---

# Codex CLI Update (Windows / 受控環境)

在銀行受控 Windows 環境更新 Codex CLI 的標準作法與已知踩雷點。
以官方安裝腳本為準，不引入第三方相依、不關閉 TLS 驗證、不改全域設定。

## TL;DR

```powershell
# 用官方安裝腳本（與 `codex update` 同一支），但先把 5.1 系統模組目錄補進 PSModulePath
powershell -NoProfile -ExecutionPolicy Bypass -Command "$env:PSModulePath += ';' + \"$env:WINDIR\System32\WindowsPowerShell\v1.0\Modules\"; irm https://chatgpt.com/codex/install.ps1 | iex"

# 驗證
& "$env:LOCALAPPDATA\Programs\OpenAI\Codex\bin\codex.exe" --version
```

安裝位置：`$env:LOCALAPPDATA\Programs\OpenAI\Codex\bin\codex.exe`
（即 `C:\Users\<user>\AppData\Local\Programs\OpenAI\Codex\bin`，安裝時已加入 PATH。）

## 為什麼內建 `codex update` 會失敗

`codex update` 內部會呼叫 **Windows PowerShell 5.1** 跑安裝腳本：

```
powershell -ExecutionPolicy Bypass -c '$env:CODEX_NON_INTERACTIVE=1; irm https://chatgpt.com/codex/install.ps1 | iex'
```

安裝腳本在驗證下載檔雜湊時用到 `Get-FileHash`，於是失敗：

```
The term 'Get-FileHash' is not recognized as the name of a cmdlet ...
Error: ... install.ps1 | iex` failed with status exit code: 1
```

## 真正的根因：PSModulePath（不是 profile、不是 -NoProfile）

`Get-FileHash` 屬於 `Microsoft.PowerShell.Utility` 模組，需要「自動載入」，
而自動載入只會去 `$env:PSModulePath` 列出的目錄找模組。5.1 的這份模組住在：

```
C:\WINDOWS\system32\WindowsPowerShell\v1.0\Modules
```

當 5.1 被啟動時繼承到的 `PSModulePath` **缺少這條路徑**，就無法載入
`Microsoft.PowerShell.Utility`，`Get-FileHash` 即「not recognized」；
再加上安裝腳本開頭設了 `$ErrorActionPreference = "Stop"`，這個錯就終止整個安裝。

關鍵在「誰啟動這個 5.1」：

- `codex update` 由 `codex.exe` 去叫 5.1，傳下去的 `PSModulePath` 缺了 v1.0 那條 → 失敗。
- 從 PowerShell 7（pwsh）去叫安裝腳本時，pwsh 7 的 `PSModulePath` 本來就含 v1.0
  那條，子 5.1 繼承到 → 自動載入成功。

→ 所以修法是「確保 `PSModulePath` 含 v1.0\Modules」，TL;DR 的指令就是直接把它補上，
與父行程無關、最穩。`-NoProfile` 與 profile 都不是原因（5.1 的 profile 只設編碼/PATH，
不碰模組載入）。

## 診斷指令

```powershell
# 重現：用「只有 7.x 路徑」的 PSModulePath 啟動 5.1，會看到 Get-FileHash 壞掉
$bad = "C:\Program Files\PowerShell\7\Modules;C:\Program Files\PowerShell\Modules"
powershell -NoProfile -Command "`$env:PSModulePath='$bad'; try { Get-FileHash `$PROFILE | Out-Null; 'OK' } catch { 'FAIL: ' + `$_.Exception.Message }"

# 確認本機 5.1 模組目錄存在
Test-Path "$env:WINDIR\System32\WindowsPowerShell\v1.0\Modules\Microsoft.PowerShell.Utility"
```

## 注意事項（受控環境）

- 這是會對外下載並安裝執行檔的動作，務必經使用者明確同意後再執行。
- 不要為了「修好」而關閉 TLS 驗證（如 `strict-ssl false`）或改動全域環境變數；
  TL;DR 只在那一次子行程的暫時環境補路徑，跑完即消失。
- 不要移除或停用 Windows PowerShell 5.1：它是 OS 內建元件、`codex update` 寫死要用它，
  移除會讓更新與其他系統工具一起壞掉。
- 安裝腳本來源固定為官方 `https://chatgpt.com/codex/install.ps1`。
- 看到 `$env:CODEX_NON_INTERACTIVE=1` 被外層 shell 先展開而報的紅字屬無害雜訊，
  只要最後出現 `Codex CLI <version> installed successfully.` 即成功。

## 更新後驗證

```powershell
& "$env:LOCALAPPDATA\Programs\OpenAI\Codex\bin\codex.exe" --version
# 視需要：codex doctor   # 檢查安裝、設定、登入與執行環境健康度
```
