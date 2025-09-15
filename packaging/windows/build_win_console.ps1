Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..\..

# ensure venv active if needed
if (-not (Test-Path ".venv")) {
  Write-Host "[SETUP] Creating venv…"
  py -3.13 -m venv .venv
}
\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-gui.txt pyinstaller

# require PST for packaged PST support
if (-not (Test-Path "mailcombine\resources\win64\readpst.exe")) {
  Write-Warning "Missing mailcombine\resources\win64\readpst.exe (PST will fail)."
}

pyinstaller --clean build_windows_gui_console.spec
Write-Host "Console build at: dist\msgsecure-win-gui-console.exe"

