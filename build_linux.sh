#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

# Ensure linux readpst (if present) is executable
if [ -f "mailcombine/resources/linux64/readpst" ]; then
  chmod +x mailcombine/resources/linux64/readpst
fi

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt pyinstaller
pyinstaller build_linux.spec

echo "Done. See dist/mail-combine-linux"
