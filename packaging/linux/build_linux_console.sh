#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."

python3 -m venv .venv 2>/dev/null || true
source .venv/bin/activate
python -m pip install --upgrade pip >/dev/null
pip install -r requirements-gui.txt pyinstaller >/dev/null

pyinstaller --clean build_linux_gui_console.spec
echo "Console build at: dist/msgsecure-linux-gui-console"

