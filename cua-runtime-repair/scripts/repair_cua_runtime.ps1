[CmdletBinding()]
param(
  [Parameter()]
  [string]$RuntimeRoot = '',

  [Parameter()]
  [switch]$VerifyOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-Info {
  param([Parameter(Mandatory)][string]$Message)

  Write-Output "[cua-runtime-repair] $Message"
}

function Get-ManifestPath {
  param(
    [Parameter(Mandatory)]$Manifest,
    [Parameter(Mandatory)][string]$Name,
    [Parameter(Mandatory)][string]$Root
  )

  $property = $Manifest.PSObject.Properties[$Name]
  if ($null -eq $property -or [string]::IsNullOrWhiteSpace([string]$property.Value)) {
    throw "Runtime manifest is missing '$Name'."
  }

  $relativePath = ([string]$property.Value) -replace '/', '\'
  return Join-Path $Root $relativePath
}

if ([string]::IsNullOrWhiteSpace($RuntimeRoot)) {
  $localAppData = [Environment]::GetFolderPath('LocalApplicationData')
  $RuntimeRoot = Join-Path $localAppData 'Programs\Codex\resources\cua_node'
}

$RuntimeRoot = [IO.Path]::GetFullPath($RuntimeRoot)
$manifestPath = Join-Path $RuntimeRoot 'manifest.json'
if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
  throw "CUA runtime manifest not found: $manifestPath"
}

$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
$nodePath = Get-ManifestPath -Manifest $manifest -Name 'node_path' -Root $RuntimeRoot
$nodeModules = Get-ManifestPath -Manifest $manifest -Name 'node_modules' -Root $RuntimeRoot
$nodeReplPath = Get-ManifestPath -Manifest $manifest -Name 'node_repl_path' -Root $RuntimeRoot
$nodeBinDir = Split-Path -Parent $nodePath

foreach ($requiredFile in @($nodePath, $nodeReplPath)) {
  if (-not (Test-Path -LiteralPath $requiredFile -PathType Leaf)) {
    throw "Required CUA runtime file not found: $requiredFile"
  }
}
if (-not (Test-Path -LiteralPath $nodeModules -PathType Container)) {
  throw "CUA runtime node_modules directory not found: $nodeModules"
}

Write-Info "runtime=$RuntimeRoot"
Write-Info "node=$nodePath"
Write-Info "node_modules=$nodeModules"
if ($VerifyOnly) {
  Write-Info 'mode=verify-only'
}

$encodedItems = New-Object 'System.Collections.Generic.List[System.IO.FileSystemInfo]'
$pendingDirectories = New-Object 'System.Collections.Generic.Stack[string]'
$pendingDirectories.Push($nodeModules)

while ($pendingDirectories.Count -gt 0) {
  $currentDirectory = $pendingDirectories.Pop()
  try {
    $children = ([IO.DirectoryInfo]::new($currentDirectory)).EnumerateFileSystemInfos()
  } catch {
    Write-Info "skip unreadable directory: $currentDirectory ($($_.Exception.Message))"
    continue
  }

  foreach ($item in $children) {
    try {
      $attributes = $item.Attributes
    } catch {
      Write-Info "skip unreadable item: $($item.FullName) ($($_.Exception.Message))"
      continue
    }

    if (($attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
      continue
    }
    if ($item.Name -match '%[0-9A-Fa-f]{2}') {
      [void]$encodedItems.Add($item)
    }
    if (($attributes -band [IO.FileAttributes]::Directory) -ne 0) {
      $pendingDirectories.Push($item.FullName)
    }
  }
}

$encodedItems = @(
  $encodedItems |
    Sort-Object @{Expression = { $_.FullName.Length }; Ascending = $true}, FullName
)

$createdCount = 0
$skippedCount = 0
$pendingCount = 0
$invalidCount = 0

foreach ($item in $encodedItems) {
  $decodedName = [Uri]::UnescapeDataString([string]$item.Name)
  if ($decodedName -eq $item.Name) {
    continue
  }

  if ($decodedName.IndexOfAny([IO.Path]::GetInvalidFileNameChars()) -ge 0) {
    $invalidCount++
    Write-Info "skip invalid decoded name: $($item.FullName) -> $decodedName"
    continue
  }

  $parentPath = [IO.Path]::GetDirectoryName($item.FullName)
  $decodedPath = Join-Path $parentPath $decodedName
  if (Test-Path -LiteralPath $decodedPath) {
    $skippedCount++
    continue
  }

  if ($VerifyOnly) {
    $pendingCount++
    Write-Info "would create: $decodedPath"
    continue
  }

  if (($item.Attributes -band [IO.FileAttributes]::Directory) -ne 0) {
    New-Item -ItemType Junction -Path $decodedPath -Target $item.FullName | Out-Null
  } else {
    New-Item -ItemType HardLink -Path $decodedPath -Target $item.FullName | Out-Null
  }

  $createdCount++
  Write-Info "created: $decodedPath -> $($item.FullName)"
}

Write-Info "aliases created=$createdCount skipped=$skippedCount pending=$pendingCount invalid=$invalidCount"

$probe = @'
// tinyskyAlt reads its config from node_repl's globalThis.nodeRepl when imported, so outside
// the REPL only its resolution can be checked; cua.getState() in the REPL is the final check.
const resolveOnly = new Set(["@oai/cua/tinyskyAlt"]);
const packages = ["@oai/cua/tinyskyAlt", "@oai/sky", "@oai/sky/service"];
let failed = false;
for (const packageName of packages) {
  try {
    if (resolveOnly.has(packageName)) {
      import.meta.resolve(packageName);
      console.log(packageName + ":resolved");
      continue;
    }
    await import(packageName);
    console.log(packageName + ":ok");
  } catch (error) {
    failed = true;
    console.error(packageName + ":" + (error?.name ?? "Error") + ":" + (error?.message ?? String(error)));
  }
}
if (failed) process.exitCode = 1;
'@

$probePath = Join-Path $nodeBinDir ("cua-runtime-probe-" + [Guid]::NewGuid().ToString('N') + '.mjs')
[IO.File]::WriteAllText($probePath, $probe, [Text.UTF8Encoding]::new($false))
Push-Location $nodeBinDir
try {
  $savedErrorActionPreference = $ErrorActionPreference
  $ErrorActionPreference = 'Continue'
  try {
    $probeOutput = @(& $nodePath $probePath 2>&1)
    $probeExitCode = $LASTEXITCODE
  } finally {
    $ErrorActionPreference = $savedErrorActionPreference
  }
  $probeOutput | ForEach-Object { Write-Output $_ }
  if ($probeExitCode -ne 0) {
    throw "CUA package import verification failed with exit code $probeExitCode."
  }
} finally {
  Pop-Location
  if (Test-Path -LiteralPath $probePath) {
    Remove-Item -LiteralPath $probePath -Force
  }
}

$setupPath = Join-Path $nodeBinDir 'setup.ps1'
if (Test-Path -LiteralPath $setupPath -PathType Leaf) {
  $savedErrorActionPreference = $ErrorActionPreference
  $ErrorActionPreference = 'Continue'
  try {
    $setupOutput = @(& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $setupPath 2>&1)
    $setupExitCode = $LASTEXITCODE
  } finally {
    $ErrorActionPreference = $savedErrorActionPreference
  }
  $setupOutput | ForEach-Object { Write-Output $_ }
  if ($setupExitCode -ne 0) {
    throw "CUA runtime setup validation failed with exit code $setupExitCode."
  }
}

Write-Info 'package imports and runtime setup validation passed'
