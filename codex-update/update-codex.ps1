#!/usr/bin/env pwsh
<#
.SYNOPSIS
    更新 OpenAI Codex CLI 在公司管控 Windows 環境上。
    不會修改系統、npm 或 git 的全域設定。

.DESCRIPTION
    優先使用內建 codex update，失敗時降級使用官方安裝腳本重試。
    全程保留 HTTPS 與 checksum 驗證，不會關閉 TLS。

.NOTES
    請以系統管理員身份執行。
#>

$ErrorActionPreference = "Stop"
$Host.UI.RawUI.WindowTitle = "Codex CLI Updater"

function Write-Step {
    param([string]$Message)
    Write-Host ">> $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-WarningMsg {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

function Write-ErrorMsg {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

# ─── Step 1: 檢查目前狀態 ─────────────────────────────────────────
Write-Step "檢查目前已安裝的 Codex CLI 版本..."
codex --version
if ($LASTEXITCODE -ne 0) {
    Write-ErrorMsg "找不到 codex 指令。請確認 Codex CLI 已安裝且加入 PATH。"
    exit 1
}

codex doctor
Write-Host ""

# ─── Step 2: 嘗試內建更新 ─────────────────────────────────────────
Write-Step "執行內建更新：codex update"
codex update

if ($LASTEXITCODE -eq 0) {
    Write-Success "codex update 成功！"
} else {
    Write-WarningMsg "內建更新失敗 (exit code: $LASTEXITCODE)，準備降級使用官方安裝腳本..."
    Write-Host ""
    Write-Step "降級：以 -NoProfile 執行官方安裝腳本（保留 TLS 驗證）"
    powershell.exe -NoProfile -ExecutionPolicy Bypass -Command '$env:CODEX_NON_INTERACTIVE="1"; Invoke-RestMethod https://chatgpt.com/codex/install.ps1 | Invoke-Expression'

    if ($LASTEXITCODE -ne 0) {
        Write-ErrorMsg "官方安裝腳本也失敗了 (exit code: $LASTEXITCODE)。"
        Write-Host ""
        Write-Step "收集診斷資訊..."
        codex doctor
        Write-Host ""
        Write-ErrorMsg "請將上述輸出提供給 IT 部門。可能原因：憑證、Proxy、權限、或受管理裝置限制。"
        Write-WarningMsg "提醒：請勿關閉 TLS 驗證或使用 strict-ssl false 繞過安全性檢查。"
        exit 1
    }
}

# ─── Step 3: 驗證結果 ─────────────────────────────────────────────
Write-Host ""
Write-Step "驗證更新結果..."
codex --version
codex doctor

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Success "Codex CLI 更新完成，所有檢查通過！"
} else {
    Write-Host ""
    Write-WarningMsg "更新已完成，但 codex doctor 回報問題，請查看上方輸出。"
}
