---
name: windows-cjk-font-substitution
description: Diagnose and configure Windows Chinese/Japanese/Korean font fallback, especially replacing Noto Sans SC/TC and Noto Sans CJK SC/TC with Sarasa/Gengsha UI fonts system-wide. Use when users report mixed simplified/traditional Chinese font shapes in VS Code, Electron/Chromium apps, Markdown/extension README pages, or other Windows apps; when Noto Sans SC/TC must be substituted; or when ClearType color fringing appears after CJK font changes.
---

# Windows CJK Font Substitution

## Core Rule

Do not assume a FontSubstitutes registry entry is effective. First determine whether the requested font is still installed. If `Noto Sans SC` or `Noto Sans TC` is installed as a real font, many apps will use the real Noto face and skip substitution.

Prefer this order:

1. Confirm the target replacement font is installed and visible.
2. Confirm whether real Noto SC/TC fonts are installed.
3. Write system-level `HKLM` font substitutes.
4. Unregister real Noto SC/TC from Windows Fonts if needed.
5. Reboot and validate from Windows font enumeration.
6. Handle app-specific fallback or ClearType issues only after system state is correct.

## Diagnostic Commands

Use PowerShell. For HKLM edits, ask the user to run PowerShell as Administrator if the current shell is not elevated.

Check elevation:

```powershell
$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
```

Check Sarasa/Gengsha installation:

```powershell
$sarasa = "$env:LOCALAPPDATA\Microsoft\Windows\Fonts\Sarasa-SuperTTC.ttc"
[pscustomobject]@{
  SarasaSuperTTCExists = Test-Path -LiteralPath $sarasa
  SarasaPath = $sarasa
}

Add-Type -AssemblyName System.Drawing
(New-Object System.Drawing.Text.InstalledFontCollection).Families.Name |
  Where-Object { $_ -match 'Sarasa|更紗|更纱' } |
  Sort-Object
```

Expected key families include:

```txt
更纱黑体 UI SC
更紗黑體 UI TC
Sarasa Term SC
Sarasa Term TC
等距更纱黑体 SC
等距更紗黑體 TC
```

Check whether real Noto SC/TC fonts are still installed:

```powershell
Add-Type -AssemblyName System.Drawing
(New-Object System.Drawing.Text.InstalledFontCollection).Families.Name |
  Where-Object { $_ -match '^Noto Sans (SC|TC)$|^Noto Sans CJK (SC|TC)$' }

Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" |
  Select-Object "Noto Sans SC (TrueType)","Noto Sans TC (TrueType)"

Get-ChildItem -LiteralPath "$env:WINDIR\Fonts" -Filter "NotoSans*" -ErrorAction SilentlyContinue |
  Select-Object Name,Length |
  Sort-Object Name
```

If `InstalledFontCollection` still lists `Noto Sans SC` or `Noto Sans TC`, substitution is not reliable yet.

## System Substitution

Back up registry keys before editing:

```powershell
reg export "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" "$env:USERPROFILE\Desktop\fonts-backup.reg"
reg export "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\FontSubstitutes" "$env:USERPROFILE\Desktop\fontsubstitutes-backup.reg"
```

Write `HKLM` substitutes. `HKCU` substitutes may exist, but do not rely on them for system-wide behavior.

```powershell
$key = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\FontSubstitutes"
New-Item -Path $key -Force | Out-Null

New-ItemProperty -Path $key -Name "Noto Sans SC" -Value "更纱黑体 UI SC" -PropertyType String -Force | Out-Null
New-ItemProperty -Path $key -Name "Noto Sans CJK SC" -Value "更纱黑体 UI SC" -PropertyType String -Force | Out-Null
New-ItemProperty -Path $key -Name "Noto Sans TC" -Value "更紗黑體 UI TC" -PropertyType String -Force | Out-Null
New-ItemProperty -Path $key -Name "Noto Sans CJK TC" -Value "更紗黑體 UI TC" -PropertyType String -Force | Out-Null
```

If real Noto SC/TC is installed, unregister it from the Windows font registry:

```powershell
$fontsKey = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"
Remove-ItemProperty -Path $fontsKey -Name "Noto Sans SC (TrueType)" -ErrorAction SilentlyContinue
Remove-ItemProperty -Path $fontsKey -Name "Noto Sans TC (TrueType)" -ErrorAction SilentlyContinue
```

Prefer unregistering/removing from Windows font settings over renaming files in `C:\Windows\Fonts`. If `Rename-Item` returns `Access to the path is denied`, do not treat that as failure when the registry entries are already gone. The file may be protected or cached while no longer registered as an installed font.

Reboot after changing HKLM font registration. Logging out is often insufficient.

## Validation

After reboot, validate:

```powershell
Add-Type -AssemblyName System.Drawing
(New-Object System.Drawing.Text.InstalledFontCollection).Families.Name |
  Where-Object { $_ -match '^Noto Sans (SC|TC)$|^Noto Sans CJK (SC|TC)$' }

Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\FontSubstitutes" |
  Select-Object "Noto Sans SC","Noto Sans CJK SC","Noto Sans TC","Noto Sans CJK TC"

Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" |
  Select-Object "Noto Sans SC (TrueType)","Noto Sans TC (TrueType)"
```

Expected:

- The `InstalledFontCollection` Noto query prints nothing.
- `FontSubstitutes` maps SC names to `更纱黑体 UI SC`.
- `FontSubstitutes` maps TC names to `更紗黑體 UI TC`.
- The HKLM Fonts query for `Noto Sans SC (TrueType)` and `Noto Sans TC (TrueType)` is blank.

If Noto still appears after reboot, clear font cache from an elevated PowerShell, then reboot again:

```powershell
Stop-Service FontCache -Force
Remove-Item "$env:WinDir\ServiceProfiles\LocalService\AppData\Local\FontCache\*" -Force -ErrorAction SilentlyContinue
Remove-Item "$env:WinDir\System32\FNTCACHE.DAT" -Force -ErrorAction SilentlyContinue
Start-Service FontCache
```

## App Caveats

Windows font substitution cannot override fonts embedded by an app or loaded by web content through `@font-face`.

If a specific app still renders Noto-like shapes after system validation:

- Check whether it bundles or downloads Noto fonts.
- Check whether it requests a different family such as `Noto Sans HK`, `Noto Sans JP`, or `Noto Sans CJK JP`.
- Fully exit background Electron/Chromium processes before retesting.
- Reboot before judging VS Code, Discord, Chrome, Edge, or other long-running apps.

For VS Code editor consistency, use user settings like:

```json
"editor.fontFamily": "'Cascadia Code', 'Microsoft YaHei', monospace",
"editor.fontSize": 16,
"editor.fontWeight": "normal",
"editor.unicodeHighlight.allowedLocales": {
  "zh-hant": true
},
"editor.unicodeHighlight.nonBasicASCII": false,
"files.autoGuessEncoding": true
```

For normal Markdown preview, add Sarasa to the preview stack:

```json
"markdown.preview.fontFamily": "'更紗黑體 UI TC', '更纱黑体 UI SC', 'Microsoft JhengHei UI', 'Microsoft YaHei UI', -apple-system, BlinkMacSystemFont, 'Segoe WPC', 'Segoe UI', system-ui, sans-serif"
```

Do not assume VS Code extension detail pages consume `markdown.preview.fontFamily`; they may use workbench/webview CSS instead.

## ClearType Color Fringing

If glyph edges look red, blue, or color-shifted after the font change, treat it as ClearType/subpixel rendering, not font substitution failure.

Try in this order:

1. Run `cttune.exe` and choose samples with the least red/blue edge color.
2. Confirm Windows display resolution and scaling are both set to the recommended values.
3. If a display is rotated, test in landscape orientation; ClearType is sensitive to subpixel layout.
4. Disable ClearType from `cttune.exe` if color fringing matters more than sharpness.
5. If only Chromium/Electron apps are affected, disable hardware acceleration for that app and retest.

For VS Code, hardware acceleration can be disabled in `argv.json`:

```json
"disable-hardware-acceleration": true
```
