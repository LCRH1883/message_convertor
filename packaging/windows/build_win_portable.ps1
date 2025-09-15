Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Go to repo root
Set-Location $PSScriptRoot\..\..

function Find-Python {
  # Try python first (most installs add this to PATH)
  $candidates = @(
    "python", "python3", "py -3.12", "py -3", "py"
  )
  foreach ($c in $candidates) {
    try {
      & $c --version *> $null
      if ($LASTEXITCODE -eq 0) { return $c }
    } catch { }
  }
  # Fall back to common absolute paths (adjust/add if needed)
  $common = @(
    "C:\Program Files\Python312\python.exe",
    "C:\Program Files\Python311\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe"
  )
  foreach ($p in $common) {
    if (Test-Path $p) { return $p }
  }
  return $null
}

$pyCmd = Find-Python
if (-not $pyCmd) {
  Write-Error @"
Python not found.

Fix:
1) Install Python 3.12 (64-bit) from https://www.python.org/downloads/windows/
   - Check "Add python.exe to PATH"
   - Check "Install launcher for all users (py.exe)"
2) If 'python' opens the Microsoft Store, turn OFF Windows "App execution aliases" for python/python3.
"@
}

# Require embedded readpst so PST works in the single-file EXE
$readpst = "mailcombine\resources\win64\readpst.exe"
if (-not (Test-Path $readpst)) {
  Write-Error "Missing $readpst. Place readpst.exe there before building."
}

# Create venv if missing
if (-not (Test-Path ".venv")) {
  Write-Host "[SETUP] Creating venv with: $pyCmd -m venv .venv"
  & $pyCmd -m venv .venv
}

# Activate venv
$activate = ".\.venv\Scripts\Activate.ps1"
if (-not (Test-Path $activate)) { Write-Error "Activation script not found: $activate" }
. $activate

# Deps
Write-Host "[SETUP] Installing build deps…"
python -m pip install --upgrade pip
pip install -r requirements-gui.txt pyinstaller

# Build onefile GUI EXE (resources embedded via spec)
Write-Host "[BUILD] Running PyInstaller…"
pyinstaller build_windows_gui.spec

$artifact = "dist\msgsecure-win-gui.exe"
if (-not (Test-Path $artifact)) {
  # Fallback check in case spec name wasn’t updated yet
  if (Test-Path "dist\mail-combine-win-gui.exe") {
    Rename-Item "dist\mail-combine-win-gui.exe" "dist\msgsecure-win-gui.exe" -Force
  } else {
    Write-Error "Build failed: dist\msgsecure-win-gui.exe not created."
  }
}

Write-Host "✅ Portable ready: dist\msgsecure-win-gui.exe" -ForegroundColor Green
