#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."

if [ -f "mailcombine/resources/linux64/readpst" ]; then
  chmod +x mailcombine/resources/linux64/readpst || true
fi

python3 -m venv .venv 2>/dev/null || true
source .venv/bin/activate
python -m pip install --upgrade pip >/dev/null
pip install -r requirements.txt pyinstaller >/dev/null

pyinstaller --clean build_linux.spec
echo "Console build at: dist/mail-combine-linux"
