# MsgSecure

MsgSecure is split into two deliverables:

1. **MsgSecure (Viewer)** - the installer-only desktop experience for browsing, searching, and exporting mailboxes. The Windows build is currently supported; Linux packaging will follow. Progress and planning live in [`docs/viewer/`](docs/viewer/README.md).
2. **MsgSecure Converter** - the portable conversion tool that merges `.msg`, `.eml`, and `.pst` inputs into searchable text, JSON sidecars, and hash reports. It ships as single-file executables (Windows/Linux) and as a Windows installer.

Current converter release: **0.1.0** (artifacts land under `dist/converter/0.1.0/`).

## MsgSecure Converter Quick Use

Portable binaries:
- **Windows:** `dist/converter/0.1.0/MsgSecure-Converter-win.exe`
- **Linux:** `dist/converter/0.1.0/MsgSecure-Converter-x86_64.AppImage` (make executable: `chmod +x`)

Pick an input folder, choose an output `.txt`, optionally enable:
- Include attachments in text
- Write JSON sidecar
- Write hashes.csv (SHA-256)

## Building MsgSecure Converter

### Windows portable EXE
```powershell
pwsh packaging/windows/build_win_portable.ps1
# => dist/converter/0.1.0/MsgSecure-Converter-win.exe
```

### Windows installer
```powershell
pwsh packaging/windows/build_win_installer.ps1
# => dist/converter/0.1.0/MsgSecure-Converter-0.1.0-setup.exe
```
Run the installer to install or upgrade; uninstall via **Settings -> Apps -> MsgSecure Converter -> Uninstall**.

Optional signing (elevated PowerShell):
```powershell
.\.venv\Scripts\sigstore.exe sign dist/converter/0.1.0/MsgSecure-Converter-0.1.0-setup.exe --oauth-force-oob
```

### Linux (run on a Linux host)
```bash
cd packaging/linux
bash build_linux_appimage.sh    # => dist/converter/0.1.0/MsgSecure-Converter-x86_64.AppImage
bash build_linux_console.sh     # => dist/converter/0.1.0/MsgSecure-Converter-linux-cli
```

### CLI (cross-platform)
```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements-gui.txt
python -m mailcombine.gui  # GUI
# or
python -m mailcombine.cli -i samples -o combined_emails.txt --attachments --json --hashes
```

Key CLI options:
- `--attachments` - include attachment list (name, size, SHA-256)
- `--json [path]` / `--no-json`
- `--hashes` / `--hashes-path PATH`
- `--progress-file PATH` - emit JSONL progress updates

### Verify hashes later
- **Windows:** `Get-FileHash -Algorithm SHA256 "C:\path\to\file"`
- **Linux/macOS:** `sha256sum /path/to/file`

Match the output to the `sha256` column within the generated `*_hashes.csv`.

## MsgSecure Viewer (Windows installer)
```powershell
pwsh packaging/windows/build_viewer_installer.ps1
# => dist/viewer/0.1.0/MsgSecure-0.1.0-setup.exe
```
The script publishes the WPF viewer (`dist/viewer/0.1.0/publish/MsgSecure.exe`) and produces an installer that adds Start Menu and optional desktop shortcuts. Re-run the installer to upgrade; uninstall via **Settings -> Apps -> MsgSecure -> Uninstall**.

## Documentation

- Converter docs: [`docs/converter/`](docs/converter/README.md) (versioned build notes and release information)
- Viewer docs: [`docs/viewer/`](docs/viewer/README.md)
- Packaging scripts: [`packaging/windows`](packaging/windows) / [`packaging/linux`](packaging/linux)

