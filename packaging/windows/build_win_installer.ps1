Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path "$PSScriptRoot/../.."
Write-Host "[INFO] Repo root: $repoRoot"

$initPath = Join-Path $repoRoot "mailcombine/__init__.py"
$versionMatch = Select-String -Path $initPath -Pattern '__version__\s*=\s*"([^"]+)"' -ErrorAction Stop | Select-Object -First 1
if (-not $versionMatch) {
  throw "Unable to determine version from $initPath"
}
$version = $versionMatch.Matches[0].Groups[1].Value
Write-Host "[INFO] Building MsgSecure $version"

$versionParts = @($version.Split('.'))
while ($versionParts.Count -lt 4) {
  $versionParts += '0'
}
$winFileVersion = ($versionParts[0..3] -join '.')
Write-Host "[INFO] Windows file version: $winFileVersion"

Write-Host "[BUILD] Refreshing PyInstaller onefile payload..."
& "$PSScriptRoot\\build_win_portable.ps1"

$portableExe = Join-Path $repoRoot "dist/msgsecure-win-gui.exe"
if (-not (Test-Path $portableExe)) {
  throw "Missing portable executable: $portableExe. Did the PyInstaller build succeed?"
}

$possibleCommands = @("iscc.exe", "iscc", "ISCC.exe", "ISCC")
$innoCompiler = $null
foreach ($cmd in $possibleCommands) {
  $candidate = Get-Command $cmd -ErrorAction SilentlyContinue
  if ($candidate) {
    $innoCompiler = $candidate.Source
    break
  }
}
if (-not $innoCompiler) {
  $defaultLocations = @()
  $pf = [Environment]::GetEnvironmentVariable('ProgramFiles')
  if ($pf) { $defaultLocations += [System.IO.Path]::Combine($pf, 'Inno Setup 6', 'ISCC.exe') }
  $pf86 = [Environment]::GetEnvironmentVariable('ProgramFiles(x86)')
  if ($pf86) { $defaultLocations += [System.IO.Path]::Combine($pf86, 'Inno Setup 6', 'ISCC.exe') }
  $local = [Environment]::GetEnvironmentVariable('LOCALAPPDATA')
  if ($local) { $defaultLocations += [System.IO.Path]::Combine($local, 'Programs', 'Inno Setup 6', 'ISCC.exe') }
  $defaultLocations = @($defaultLocations | Where-Object { Test-Path $_ })
  if ($defaultLocations.Count -gt 0) {
    $innoCompiler = $defaultLocations[0]
  }
}
if (-not $innoCompiler) {
  throw "Inno Setup compiler (iscc.exe) not found. Install Inno Setup 6 and ensure ISCC.exe is on PATH."
}
Write-Host ("[BUILD] Using Inno Setup compiler: {0}" -f $innoCompiler)

$issPath = Join-Path $PSScriptRoot "msgsecure_installer.iss"
if (-not (Test-Path $issPath)) {
  throw "Installer script missing: $issPath"
}

$defineArgs = @("/DAppVersion=$version", "/DAppFileVersion=$winFileVersion")
Write-Host "[BUILD] Compiling installer via Inno Setup..."
& $innoCompiler @defineArgs $issPath
if ($LASTEXITCODE -ne 0) {
  throw "Inno Setup compiler failed with exit code $LASTEXITCODE"
}

$installerPath = Join-Path $repoRoot "dist/MsgSecure-$version-setup.exe"
if (Test-Path $installerPath) {
  Write-Host "[DONE] Installer ready: $installerPath" -ForegroundColor Green
} else {
  Write-Warning "Installer build finished but expected artifact was not found at $installerPath."
}
