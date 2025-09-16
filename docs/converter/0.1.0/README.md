# MsgSecure Converter 0.1.0

Artifacts produced by the build scripts land in `dist/converter/0.1.0/`:

- `MsgSecure-Converter-win.exe` – Windows portable single-file build.
- `MsgSecure-Converter-0.1.0-setup.exe` – Windows installer generated via Inno Setup.
- `MsgSecure-Converter-x86_64.AppImage` – Linux AppImage package (after running the Linux build script).
- `MsgSecure-Converter-linux-gui` – Raw PyInstaller onefile GUI for Linux (copied alongside the AppImage).
- `MsgSecure-Converter-linux-cli` – CLI-focused PyInstaller build (`build_linux_console.sh`).

## Build commands

```powershell
# Windows portable + place artifact in dist/converter/0.1.0
pwsh packaging/windows/build_win_portable.ps1

# Windows installer -> dist/converter/0.1.0/MsgSecure-Converter-0.1.0-setup.exe
pwsh packaging/windows/build_win_installer.ps1
```

```bash
# Linux AppImage + portable CLI binaries (run on Linux)
cd packaging/linux
bash build_linux_appimage.sh
bash build_linux_console.sh
```

## Documentation

- [Release notes](release_notes.md)
