# MsgSecure Converter Release Notes

## 0.1.0
- First tagged MsgSecure Converter release with PyInstaller-based Windows and Linux builds.
- Windows portable executable `MsgSecure-Converter-win.exe` plus Inno Setup installer `MsgSecure-Converter-0.1.0-setup.exe`.
- Linux AppImage (`MsgSecure-Converter-x86_64.AppImage`) and standalone CLI/GUI binaries staged alongside the installer outputs.
- Core conversion pipeline supporting MSG, EML, and PST ingestion with merged text output, JSON sidecar, and SHA-256 hash reports (requires bundled `readpst`).
