#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."

VERSION=$(python3 -c "import re, pathlib; text = pathlib.Path('mailcombine/__init__.py').read_text(); m = re.search(r'__version__\\s*=\\s*\"([^\"]+)\"', text); print(m.group(1))")
CONVERTER_DIST_DIR="dist/converter/${VERSION}"
mkdir -p "$CONVERTER_DIST_DIR"

if [ -f "mailcombine/resources/linux64/readpst" ]; then
  chmod +x mailcombine/resources/linux64/readpst || true
fi

python3 -m venv .venv 2>/dev/null || true
source .venv/bin/activate
python -m pip install --upgrade pip >/dev/null
pip install -r requirements.txt pyinstaller >/dev/null

pyinstaller --clean build_linux.spec
CLI_STAGE_PATH="dist/mail-combine-linux"
if [ ! -f "$CLI_STAGE_PATH" ]; then
  echo "[ERROR] Expected PyInstaller CLI build $CLI_STAGE_PATH not found."
  exit 1
fi
CLI_DEST="$CONVERTER_DIST_DIR/MsgSecure-Converter-linux-cli"
mv "$CLI_STAGE_PATH" "$CLI_DEST"

echo "? Converter CLI ready: $CLI_DEST"
