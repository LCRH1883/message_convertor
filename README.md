# MsgSecure

MsgSecure delivers two Windows desktop experiences built on the same mail-processing core. Both ship from this repository and reuse the mailcore and mailcombine packages.

- **MsgSecure Viewer** – an installed WPF application for reviewing, searching, and exporting .msg, .eml, and .pst content. The installer bundles the embedded Python runtime so viewing and conversion features work immediately after setup.
- **MsgSecure Converter** – a conversion utility available as both a portable single-file executable and a traditional installer. Use it when you want the conversion workflow without the full viewer shell.

Current release: **0.1.0**. Build outputs land under dist/viewer/0.1.0/ and dist/converter/0.1.0/.

## MsgSecure Viewer
### Quick Start
- Install: dist/viewer/0.1.0/MsgSecure-0.1.0-setup.exe.
- Launch **MsgSecure** from the Start Menu and open either a PST or a folder of .msg/.eml files.
- The installer places a private .venv, mailcore, and mailcombine beside MsgSecure.exe; the viewer automatically starts the bundled RPC backend.

### Build From Source
`powershell
pwsh packaging/windows/build_viewer_installer.ps1
# => dist/viewer/0.1.0/MsgSecure-0.1.0-setup.exe
`
The script publishes the WPF app, mirrors the runtime dependencies into dist/viewer/0.1.0/publish/, and invokes Inno Setup.

### Sign & Verify
`powershell
cd D:\Repos\message_convertor
 = 1
& '.\.venv\Scripts\sigstore.exe' sign 
  'dist\viewer\0.1.0\MsgSecure-0.1.0-setup.exe' 
  --bundle 'dist\viewer\0.1.0\MsgSecure-0.1.0-setup.sigstore' 
  --oidc-disable-ambient-providers 
  --overwrite

& '.\.venv\Scripts\sigstore.exe' verify identity 
  'dist\viewer\0.1.0\MsgSecure-0.1.0-setup.exe' 
  --bundle 'dist\viewer\0.1.0\MsgSecure-0.1.0-setup.sigstore' 
  --cert-identity lh@lcrhalpin.com 
  --cert-oidc-issuer https://github.com/login/oauth 
  --offline
`

## MsgSecure Converter
### Quick Use
- Portable Windows EXE: dist/converter/0.1.0/MsgSecure-Converter-win.exe.
- Windows installer: dist/converter/0.1.0/MsgSecure-Converter-0.1.0-setup.exe.
- Linux AppImage: dist/converter/0.1.0/MsgSecure-Converter-x86_64.AppImage (chmod +x before running).

Steps: choose an input source (folder or single .pst/.msg/.eml file), pick an output text file, then optionally enable JSON and hash reporting. Progress is written to a JSONL file and msgsecure_startup.log beside the executable.

### CLI Entry Point
`ash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements-gui.txt
python -m mailcombine.cli -i <input-path> -o combined.txt --attachments --hashes
`
Flags mirror the GUI (--no-json, --hashes-path, --progress-file, etc.).

### Build Artifacts
- Portable EXE: pwsh packaging/windows/build_win_portable.ps1.
- Windows installer: pwsh packaging/windows/build_win_installer.ps1.
- Linux builds (run on Linux):
  `ash
  cd packaging/linux
  bash build_linux_appimage.sh    # dist/converter/0.1.0/MsgSecure-Converter-x86_64.AppImage
  bash build_linux_console.sh     # dist/converter/0.1.0/MsgSecure-Converter-linux-cli
  `

### Sign & Verify (Optional)
`powershell
cd D:\Repos\message_convertor
 = 1
& '.\.venv\Scripts\sigstore.exe' sign 
  'dist\converter\0.1.0\MsgSecure-Converter-0.1.0-setup.exe' 
  --bundle 'dist\converter\0.1.0\MsgSecure-Converter-0.1.0-setup.sigstore' 
  --oidc-disable-ambient-providers 
  --overwrite

& '.\.venv\Scripts\sigstore.exe' verify identity 
  'dist\converter\0.1.0\MsgSecure-Converter-0.1.0-setup.exe' 
  --bundle 'dist\converter\0.1.0\MsgSecure-Converter-0.1.0-setup.sigstore' 
  --cert-identity lh@lcrhalpin.com 
  --cert-oidc-issuer https://github.com/login/oauth 
  --offline
`
Need to sign a portable EXE? Re-run the same commands, swapping the installer path for the executable.

### Hash Verification
- Windows: Get-FileHash -Algorithm SHA256 <path>
- Linux/macOS: sha256sum <path>
Match the value against the sha256 column in *_hashes.csv.

## Documentation
- Viewer docs: [docs/viewer/](docs/viewer/README.md)
- Converter docs: [docs/converter/](docs/converter/README.md)
- Packaging scripts: [packaging/windows](packaging/windows) / [packaging/linux](packaging/linux)
