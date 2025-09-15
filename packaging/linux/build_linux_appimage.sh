#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."

# 1) venv + GUI deps + PyInstaller
python3 -m venv .venv 2>/dev/null || true
source .venv/bin/activate
pip install --upgrade pip >/dev/null
pip install -r requirements-gui.txt pyinstaller >/dev/null

# 2) PST support (optional)
if [ ! -f "mailcombine/resources/linux64/readpst" ]; then
  echo "[WARN] readpst not found; PST will be skipped in the AppImage."
else
  chmod +x mailcombine/resources/linux64/readpst || true
fi

# 3) Build onedir (needed for AppImage staging)
pyinstaller build_linux_gui.spec --onedir

# 4) Stage AppDir
APPDIR="packaging/linux/appdir"
mkdir -p "$APPDIR/usr/bin"
cp -r dist/mail-combine-linux-gui/* "$APPDIR/usr/bin/"

# AppRun launcher
cat > "$APPDIR/AppRun" << 'EOF'
#!/bin/sh
HERE="$(dirname "$(readlink -f "$0")")"
exec "$HERE/usr/bin/mail-combine-linux-gui" "$@"
EOF
chmod +x "$APPDIR/AppRun"

# 5) Ensure desktop + icon exist
if [ ! -f "$APPDIR/usr/share/applications/mail-combine.desktop" ]; then
  echo "[ERROR] Missing desktop file at $APPDIR/usr/share/applications/mail-combine.desktop"
  exit 1
fi
if [ ! -f "$APPDIR/usr/share/icons/hicolor/256x256/apps/mail-combine.png" ]; then
  echo "[ERROR] Missing icon at $APPDIR/usr/share/icons/hicolor/256x256/apps/mail-combine.png"
  exit 1
fi

# 6) Fetch appimagetool if missing
if [ ! -f "packaging/linux/appimagetool-x86_64.AppImage" ]; then
  wget -O packaging/linux/appimagetool-x86_64.AppImage \
    https://github.com/AppImage/AppImageKit/releases/download/13/appimagetool-x86_64.AppImage
  chmod +x packaging/linux/appimagetool-x86_64.AppImage
fi

# 7) Build AppImage
./packaging/linux/appimagetool-x86_64.AppImage "$APPDIR" "dist/Mail-Combine-x86_64.AppImage"
echo "✅ Portable ready: dist/Mail-Combine-x86_64.AppImage"

