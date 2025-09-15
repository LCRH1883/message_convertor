Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..\..

# 1) venv + GUI deps + PyInstaller
if (-not (Test-Path ".venv")) { python -m venv .venv }
\.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-gui.txt pyinstaller

# 2) PST support check (optional)
if (-not (Test-Path "mailcombine\resources\win64\readpst.exe")) {
  Write-Warning "readpst.exe not found. PST files will be skipped in the portable EXE."
}

# 3) Build onefile GUI EXE
pyinstaller build_windows_gui.spec

# 4) Verify artifact
if (-not (Test-Path "dist\mail-combine-win-gui.exe")) {
  throw "Build failed: dist\mail-combine-win-gui.exe was not created."
}
Write-Host "✅ Portable ready: dist\mail-combine-win-gui.exe" -ForegroundColor Green

