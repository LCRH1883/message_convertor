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
Write-Host "[INFO] Viewer version: $version"

$viewerDistRoot = Join-Path $repoRoot "dist\\viewer\\$version"
$publishDir = Join-Path $viewerDistRoot "publish"
New-Item -ItemType Directory -Path $publishDir -Force | Out-Null

$projectPath = Join-Path $repoRoot "viewer/MsgSecure.Viewer/MsgSecure.Viewer.csproj"
if (-not (Test-Path $projectPath)) {
  throw "Viewer project not found at $projectPath"
}

Write-Host "[BUILD] Publishing WPF viewer..."
$publishArgs = @(
  'publish',
  $projectPath,
  '-c', 'Release',
  '-r', 'win-x64',
  '--self-contained', 'true',
  '/p:PublishSingleFile=true',
  '/p:IncludeNativeLibrariesForSelfExtract=true',
  '/p:IncludeAllContentForSelfExtract=true',
  '/p:PublishTrimmed=false',
  '-o', $publishDir
)
& dotnet @publishArgs
if ($LASTEXITCODE -ne 0) {
  throw "dotnet publish failed with exit code $LASTEXITCODE"
}

Get-ChildItem -Path $publishDir -Filter 'MsgSecure.Viewer*' | ForEach-Object {
  $newName = $_.Name -replace '^MsgSecure\.Viewer', 'MsgSecure'
  if ($newName -ne $_.Name) {
    $newPath = Join-Path $_.DirectoryName $newName
    if (Test-Path $newPath) {
      Remove-Item $newPath -Force
    }
    Rename-Item -Path $_.FullName -NewName $newName
  }
}

$primaryExe = Join-Path $publishDir 'MsgSecure.exe'
if (-not (Test-Path $primaryExe)) {
  throw "Expected viewer executable not found at $primaryExe"
}

$possibleCommands = @('iscc.exe','iscc','ISCC.exe','ISCC')
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
  $existing = @($defaultLocations | Where-Object { Test-Path $_ })
  if ($existing.Count -gt 0) {
    $innoCompiler = $existing[0]
  }
}
if (-not $innoCompiler) {
  throw "Inno Setup compiler (iscc.exe) not found. Install Inno Setup 6 and ensure ISCC.exe is on PATH."
}
Write-Host "[BUILD] Using Inno Setup compiler: $innoCompiler"

$issPath = Join-Path $PSScriptRoot 'msgsecure_viewer_installer.iss'
if (-not (Test-Path $issPath)) {
  throw "Installer script missing: $issPath"
}

$defineArgs = @("/DAppVersion=$version", "/DAppFileVersion=$($version+'.0')")
Write-Host "[BUILD] Compiling viewer installer..."
& $innoCompiler @defineArgs $issPath
if ($LASTEXITCODE -ne 0) {
  throw "Inno Setup compiler failed with exit code $LASTEXITCODE"
}

$installerPath = Join-Path $viewerDistRoot "MsgSecure-$version-setup.exe"
if (Test-Path $installerPath) {
  Write-Host "[DONE] Viewer installer ready: $installerPath" -ForegroundColor Green
} else {
  Write-Warning "Viewer installer build completed but expected artifact missing at $installerPath"
}
