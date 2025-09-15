# MatterMail

MatterMail converts `.msg`, `.eml`, and `.pst` emails into a **single searchable .txt** file, with optional **JSON sidecar** and **hashes.csv**.  
It ships as a **single-file** portable app on Windows (.exe) and Linux (.AppImage), with **embedded PST (readpst)** support.

## Quick Use (GUI)
Just run the app:
- **Windows:** `mail-combine-win-gui.exe`
- **Linux:** `Mail-Combine-x86_64.AppImage` (if needed: `chmod +x` then double-click)

Pick an input folder, choose an output `.txt`, optionally turn on:
- Include attachments in text
- Write JSON sidecar
- Write hashes.csv (SHA-256)

## Building the portable apps (dev)

### Prereqs
- Place PST converters in these paths **before building**:
  - Windows: `mailcombine/resources/win64/readpst.exe`
  - Linux: `mailcombine/resources/linux64/readpst` (make executable: `chmod +x`)
- Python 3.10+ on the build machine

### Windows portable EXE
```powershell
cd packaging/windows
.\build_win_portable.ps1
# => dist\mail-combine-win-gui.exe

Linux portable AppImage
cd packaging/linux
bash build_linux_appimage.sh
# => dist/Mail-Combine-x86_64.AppImage

CLI (optional)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-gui.txt
python -m mailcombine.gui                # GUI
# or:
python -m mailcombine.cli -i samples -o combined_emails.txt --attachments --json --hashes

CLI options

--attachments — include attachment list (name, size, sha256) in text

--json [path] — write JSON sidecar (default <output>.json)

--no-json — disable JSON sidecar

--hashes — write hashes CSV (default <output>_hashes.csv)

--hashes-path PATH — custom hashes CSV path

--progress-file PATH — machine-readable JSONL progress (for GUI/monitoring)

Verifying hashes later

Windows (PowerShell):

Get-FileHash -Algorithm SHA256 "C:\path\to\file"


Linux/macOS:

sha256sum /path/to/file


Match the computed hash to the sha256 column in *_hashes.csv. If it matches, integrity is verified.

```

