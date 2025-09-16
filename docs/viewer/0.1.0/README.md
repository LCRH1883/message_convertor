# MsgSecure Viewer 0.1.0

Artifacts produced by the viewer build land in `dist/viewer/0.1.0/`:

- `publish/MsgSecure.exe` (and supporting files) — self-contained WPF binary published via `dotnet publish`.
- `MsgSecure-0.1.0-setup.exe` — Windows installer generated with Inno Setup.

## Build commands

```powershell
# Publish viewer binaries and build installer
pwsh packaging/windows/build_viewer_installer.ps1
# => dist/viewer/0.1.0/MsgSecure-0.1.0-setup.exe
```

## Code signing

Sign the shipped installer with Sigstore using the project email identity:

```powershell
pwsh -NoLogo -NoProfile -Command \
  ".\\.venv\\Scripts\\sigstore.exe sign dist/viewer/0.1.0/MsgSecure-0.1.0-setup.exe --bundle dist/viewer/0.1.0/MsgSecure-0.1.0-setup.sigstore --oidc-disable-ambient-providers"
```

When prompted, authenticate with `lh@lcrhalpin.com` to issue the signing certificate.
```

## Installation & QA checklist
- Install the generated setup and launch MsgSecure from the Start Menu.
- Re-run the installer to verify in-place upgrade keeps settings.
- Uninstall via **Settings -> Apps -> MsgSecure -> Uninstall**, confirming removal of the install directory and shortcuts.
- Launch `MsgSecure.exe` directly from `dist/viewer/0.1.0/publish/` for smoke testing without installing (optional).

## Documentation
- [Release notes](release_notes.md)
- Implementation details: [`docs/installable_viewer_roadmap.md`](../../installable_viewer_roadmap.md)
