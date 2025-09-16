# MsgSecure

MsgSecure converts `.msg`, `.eml`, and `.pst` emails into a **single searchable .txt** file, with optional **JSON sidecar** and **hashes.csv**.  
It now ships as a **Windows installer** (with upgrade/uninstall support) or as a **single-file** portable app on Windows (.exe) and Linux (.AppImage), all with **embedded PST (readpst)** support.

Current release: **0.1.0**

## Quick Use (GUI)
Installed build:
- **Windows:** Start Menu -> MsgSecure (installs to `%ProgramFiles%\MsgSecure\msgsecure-win-gui.exe`)

Portable builds (no install required):
- **Windows:** `msgsecure-win-gui.exe`
- **Linux:** `MsgSecure-x86_64.AppImage` (if needed: `chmod +x` then double-click)

Pick an input folder, choose an output `.txt`, optionally turn on:
- Include attachments in text
- Write JSON sidecar
- Write hashes.csv (SHA-256)

## Windows Installer (0.1.0)

### Build it
1. Place the PST helper at `mailcombine/resources/win64/readpst.exe` (required for PST extraction).
2. Install [Inno Setup 6](https://jrsoftware.org/isinfo.php) so `ISCC.exe` is available on your PATH (or in the default install location).
3. From the repo root, run:
   ```powershell
   pwsh packaging/windows/build_win_installer.ps1
   ```
   The script rebuilds the PyInstaller payload and emits `dist\MsgSecure-0.1.0-setup.exe`.

### Install or update
- Double-click the generated installer and follow the wizard (defaults to `%ProgramFiles%\MsgSecure`).
- Rerun a newer installer build to perform an in-place upgrade; no manual uninstall needed.

### Uninstall
- Use **Settings -> Apps -> Installed Apps -> MsgSecure -> Uninstall**, or launch `Uninstall MsgSecure` from the Start Menu group.

### Optional: Sigstore signing
- After building, sign `dist\MsgSecure-0.1.0-setup.exe` with your Sigstore workflow (for example `sigstore sign file dist\MsgSecure-0.1.0-setup.exe --identity <email>`). See [Sigstore documentation](https://docs.sigstore.dev/) for environment-specific flags.

## Building the portable apps (dev)

### Prereqs
- Place PST converters in these paths **before building**:
  - Windows: `mailcombine/resources/win64/readpst.exe`
  - Linux: `mailcombine/resources/linux64/readpst` (make executable: `chmod +x`)
- Python 3.10+ on the build machine

### Windows portable EXE
```powershell
cd packaging/windows
./build_win_portable.ps1
# => dist\msgsecure-win-gui.exe

Linux portable AppImage
cd packaging/linux
bash build_linux_appimage.sh
# => dist/MsgSecure-x86_64.AppImage

CLI (optional)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-gui.txt
python -m mailcombine.gui                # GUI
# or:
python -m mailcombine.cli -i samples -o combined_emails.txt --attachments --json --hashes

CLI options

--attachments - include attachment list (name, size, sha256) in text

--json [path] - write JSON sidecar (default <output>.json)

--no-json - disable JSON sidecar

--hashes - write hashes CSV (default <output>_hashes.csv)

--hashes-path PATH - custom hashes CSV path

--progress-file PATH - machine-readable JSONL progress (for GUI/monitoring)

Verifying hashes later

Windows (PowerShell):

Get-FileHash -Algorithm SHA256 "C:\path\to\file"


Linux/macOS:

sha256sum /path/to/file


Match the computed hash to the sha256 column in *_hashes.csv. If it matches, integrity is verified.

