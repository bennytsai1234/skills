# Windows Desktop App Mode

Use this mode when the Windows desktop app previously worked but now fails to start, falls back to a portable installation, or logs an updater/bootstrap error such as `處理程序沒有套件識別資料`.

## Responsibility model

- A portable `ChatGPT.exe` under `%LOCALAPPDATA%\Programs\Codex` is not proof that the Windows package is registered.
- The Windows package identity is owned by AppX/MSIX registration. Check `Get-AppxPackage -Name OpenAI.Codex` before treating a desktop startup error as an application-data problem.
- The updater message can be secondary recovery noise. Check the earlier bootstrap failure and whether the packaged app actually launches.
- An `AppxManifest.xml` copied into a flattened portable directory is not a valid replacement for a real MSIX package; do not register it unless its referenced files are present and the package is trusted.

## Read-only triage

Collect evidence before changing anything:

```powershell
Get-AppxPackage -Name OpenAI.Codex | Select-Object Name,PackageFullName,Version,Status,InstallLocation
Get-Command ChatGPT.exe -ErrorAction SilentlyContinue
Get-Process ChatGPT -ErrorAction SilentlyContinue | Select-Object Id,Path,MainWindowTitle,Responding
```

Then inspect the latest desktop log under:

```text
%LOCALAPPDATA%\Codex\Logs\YYYY\MM\
```

If the portable executable exists, the AppX package is absent, and the log contains bootstrap failure followed by `處理程序沒有套件識別資料`, the likely root cause is a missing package identity. If the app was previously working, also inspect installer/update-manager history for a `portable-fallback` transition; do not conclude that the app was never installed as MSIX.

## Safe repair

Only perform the repair after the user has authorized the fix.

1. Preserve the portable installation and user data. Use a new temporary directory; do not delete the old install or reset app data.
2. Obtain the current x64 MSIX from the configured trusted/approved distribution source. Do not disable TLS validation or change Windows Store policy to make the download work.
3. Verify the downloaded file before installation:

   ```powershell
   Get-FileHash .\OpenAI.Codex_*.msix -Algorithm SHA256
   Get-AuthenticodeSignature .\OpenAI.Codex_*.msix
   ```

   Require a valid Authenticode signature and the expected OpenAI package identity/publisher. Record the exact size, hash, signer, and package version.

4. Register the package:

   ```powershell
   Add-AppxPackage -Path .\OpenAI.Codex_*.msix -ForceApplicationShutdown -ErrorAction Stop
   ```

5. Verify registration and package contents:

   ```powershell
   $pkg = Get-AppxPackage -Name OpenAI.Codex
   $pkg | Select-Object Name,PackageFullName,Version,Status,InstallLocation,PackageFamilyName
   ```

   Confirm `Status` is `Ok`, the manifest application is `App`, and the install location contains `app\ChatGPT.exe`, `app\resources\app.asar`, and the required package assets.

6. Launch the registered app through its package identity, using the actual package family name:

   ```powershell
   explorer.exe "shell:AppsFolder\<PackageFamilyName>!App"
   ```

   Verify the process path is under `C:\Program Files\WindowsApps\...`, the main window becomes responsive, and the latest log reports packaged startup, successful initialization handshake, and completed critical-path startup phases.

## Update-manager follow-up

If a third-party Codex/App manager records `windowsInstallMode: portable`, change it to the supported MSIX mode through its normal UI before the next update. Do not edit its LevelDB/settings files by hand. If the manager is unsigned or not affiliated with OpenAI/Microsoft, treat it as a separate trust boundary and verify its download, signature, and selected install mode.

## Boundaries and reporting

- Do not uninstall the portable copy as part of this repair.
- Do not modify `HKLM` Store policies, global certificates, npm TLS settings, or credentials.
- If `Add-AppxPackage` fails, preserve the exact HRESULT and deployment error; do not work around it by disabling security controls.
- Report the before/after package identity, version, install location, launch result, log evidence, and any remaining update-manager mode mismatch.
