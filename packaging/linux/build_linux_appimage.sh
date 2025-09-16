#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."

APPDIR="packaging/linux/appdir"
APPIMAGE_TOOL="packaging/linux/appimagetool-x86_64.AppImage"
OUT_APPIMAGE="dist/MsgSecure-x86_64.AppImage"

# 0) Require embedded PST binary (so PST works inside the single file)
if [ ! -f "mailcombine/resources/linux64/readpst" ]; then
  echo "[ERROR] Missing mailcombine/resources/linux64/readpst (executable). Place it before building."
  exit 1
fi
chmod +x mailcombine/resources/linux64/readpst || true

# 1) venv + deps
python3 -m venv .venv 2>/dev/null || true
source .venv/bin/activate
python -m pip install --upgrade pip >/dev/null
pip install -r requirements-gui.txt pyinstaller >/dev/null

# 2) Build GUI (onefile) and stage into AppDir
pyinstaller --clean build_linux_gui.spec

# 3) Stage AppDir
mkdir -p "$APPDIR/usr/bin"
rm -rf "$APPDIR/usr/bin/"* || true
cp dist/msgsecure-linux-gui "$APPDIR/usr/bin/"

# 4) AppRun launcher
cat > "$APPDIR/AppRun" << 'EOF'
#!/bin/sh
HERE="$(dirname "$(readlink -f "$0")")"
exec "$HERE/usr/bin/msgsecure-linux-gui" "$@"
EOF
chmod +x "$APPDIR/AppRun"

# 5) Desktop + icon must exist
[ -f "$APPDIR/usr/share/applications/msgsecure.desktop" ] || { echo "[ERROR] missing msgsecure.desktop"; exit 1; }
[ -f "$APPDIR/usr/share/icons/hicolor/256x256/apps/msgsecure_logo.png" ] || { echo "[ERROR] missing msgsecure_logo.png"; exit 1; }
# Copy desktop file and icon to AppDir root so appimagetool can find them
cp "$APPDIR/usr/share/applications/msgsecure.desktop" "$APPDIR/" 2>/dev/null || true
cp "$APPDIR/usr/share/icons/hicolor/256x256/apps/msgsecure_logo.png" "$APPDIR/" 2>/dev/null || true

# 6) Get appimagetool if missing
if [ ! -f "$APPIMAGE_TOOL" ]; then
  wget -O "$APPIMAGE_TOOL" \
    https://github.com/AppImage/AppImageKit/releases/download/13/appimagetool-x86_64.AppImage
  chmod +x "$APPIMAGE_TOOL"
fi

# 7) Build AppImage
mkdir -p dist
"$APPIMAGE_TOOL" "$APPDIR" "$OUT_APPIMAGE"
echo "✅ Portable ready: $OUT_APPIMAGE"
