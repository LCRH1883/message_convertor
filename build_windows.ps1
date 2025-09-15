Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt pyinstaller

if (-not (Test-Path "mailcombine\resources\win64\readpst.exe")) {
  Write-Warning "readpst.exe is not present. PST files will be skipped in this build."
}

pyinstaller build_windows.spec

Write-Host "Done. See dist\mail-combine-win.exe"
