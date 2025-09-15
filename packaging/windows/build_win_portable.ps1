Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..\..

function Find-Python {
  $candidates = @(
    { & py -3.12 --version *> $null; if ($LASTEXITCODE -eq 0) { "py -3.12" } },
    { & py -3 --version   *> $null; if ($LASTEXITCODE -eq 0) { "py -3"   } },
    { & python --version  *> $null; if ($LASTEXITCODE -eq 0) { "python"  } },
    { & python3 --version *> $null; if ($LASTEXITCODE -eq 0) { "python3" } }
  )
  foreach ($probe in $candidates) { $cmd = & $probe; if ($cmd) { return $cmd } }
  return $null
}

$pyCmd = Find-Python
if (-not $pyCmd) {
  Write-Error "Python not found. Install Python 3.12 (64-bit), add to PATH, then re-run."
}

# REQUIRE PST support present at build time
$readpst = "mailcombine\resources\win64\readpst.exe"
if (-not (Test-Path $readpst)) {
  Write-Error "Missing $readpst. Place readpst.exe there before building."
}

# venv + deps
if (-not (Test-Path ".venv")) { & $pyCmd -m venv .venv }
. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-gui.txt pyinstaller

# Build onefile GUI EXE
pyinstaller build_windows_gui.spec

$artifact = "dist\msgsecure-win-gui.exe"
if (-not (Test-Path $artifact)) { Write-Error "Build failed: $artifact missing." }
Write-Host "✅ Portable ready: $artifact" -ForegroundColor Green
