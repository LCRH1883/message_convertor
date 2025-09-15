#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."

# REQUIRE PST support present at build time
if [ ! -f "mailcombine/resources/linux64/readpst" ]; then
  echo "[ERROR] Missing mailcombine/resources/linux64/readpst (executable). Place it before building."
  exit 1
fi
chmod +x mailcombine/resources/linux64/readpst || true

python3 -m venv .venv 2>/dev/null || true
source .venv/bin/activate
pip install --upgrade pip >/dev/null
pip install -r requirements-gui.txt pyinstaller >/dev/null

# Build onedir for staging into AppImage
pyinstaller build_linux_gui.spec --onedir

APPDIR="packaging/linux/appdir"
mkdir -p "$APPDIR/usr/bin"
cp -r dist/mail-combine-linux-gui/* "$APPDIR/usr/bin/"

# AppRun
cat > "$APPDIR/AppRun" << 'EOF'
#!/bin/sh
HERE="$(dirname "$(readlink -f "$0")")"
exec "$HERE/usr/bin/mail-combine-linux-gui" "$@"
EOF
chmod +x "$APPDIR/AppRun"

# Desktop + icon must exist
[ -f "$APPDIR/usr/share/applications/mail-combine.desktop" ] || { echo "[ERROR] missing .desktop"; exit 1; }
[ -f "$APPDIR/usr/share/icons/hicolor/256x256/apps/mail-combine.png" ] || { echo "[ERROR] missing icon"; exit 1; }

# appimagetool
if [ ! -f "packaging/linux/appimagetool-x86_64.AppImage" ]; then
  wget -O packaging/linux/appimagetool-x86_64.AppImage \
    https://github.com/AppImage/AppImageKit/releases/download/13/appimagetool-x86_64.AppImage
  chmod +x packaging/linux/appimagetool-x86_64.AppImage
fi
./packaging/linux/appimagetool-x86_64.AppImage "$APPDIR" "dist/Mail-Combine-x86_64.AppImage"
echo "✅ Portable ready: dist/Mail-Combine-x86_64.AppImage"

