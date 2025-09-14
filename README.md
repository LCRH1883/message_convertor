# mail-combine

Combine `.msg`, `.eml`, and `.pst` messages into a single searchable `.txt` file — **self-contained** builds for Linux and Windows.
- `.msg` parsing via `extract-msg`
- `.eml` parsing via Python `email` lib
- `.pst` via an **embedded** `readpst` binary shipped in `mailcombine/resources/<platform>/` (no external installs needed)

> GUI planned: the core is CLI-first; a GUI can be layered later without changing internals.

---

## Quick Start (from source)

```bash
# 1) Clone and enter
git clone <your-repo-url>.git
cd mail-combine

# 2) Create a venv and install deps
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 3) (Optional) add embedded readpst binaries
# Linux:   mailcombine/resources/linux64/readpst   (chmod +x)
# Windows: mailcombine/resources/win64/readpst.exe

# 4) Run
python -m mailcombine.cli -i /path/to/mail -o combined_emails.txt
```

The tool recursively processes `.msg` and `.eml`. If `.pst` files are present:
- If an embedded `readpst` is found for your platform, they will be converted internally and included.
- Otherwise the run continues (PST skipped with a notice).

---

## Build Self-Contained Binaries (PyInstaller)

### Linux (Ubuntu):
```bash
bash build_linux.sh
# output: dist/mail-combine-linux
```

### Windows (PowerShell):
```powershell
.uild_windows.ps1
# output: dist\mail-combine-win.exe
```

> Both builds include *only* the platform's embedded `readpst`. Ship the correct binary in `mailcombine/resources/<platform>/` before building.

---

## Usage

```bash
mail-combine --input /path/to/folder --output combined_emails.txt
# or from source
python -m mailcombine.cli --input /path/to/folder --output combined_emails.txt
```

Options:
- `-i, --input`   Root folder to search (recursively) for `.msg/.eml/.pst`. Default: `./msg_files`
- `-o, --output`  Output text file. Default: `combined_emails.txt`
- `--encoding`    Output encoding (default `utf-8`)

Output format (legal-friendly):
```
==========================================================================================
FILE: example.msg
SOURCE: /abs/path/to/example.msg
DATE: 2024-07-01T12:34:56-07:00
FROM: Alice <alice@example.com>
TO: Bob <bob@example.com>
SUBJECT: Project Update
MESSAGE-ID: <abc123@example.com>

Body text...
==========================================================================================
```

---

## Repository layout

```
mail-combine/
├─ mailcombine/
│  ├─ __init__.py
│  ├─ cli.py
│  ├─ extractors.py
│  ├─ writer.py
│  └─ resources/
│     ├─ linux64/readpst        # (optional; you provide)
│     └─ win64/readpst.exe      # (optional; you provide)
├─ requirements.txt
├─ build_linux.spec
├─ build_windows.spec
├─ build_linux.sh
├─ build_windows.ps1
├─ .gitignore
└─ LICENSE
```

---

## Notes

- If you need an attachments index (filenames or text from `.txt/.csv` attachments), open an issue or extend `extractors.py` with an `--list-attachments` flag. The writer is already modular.
- For chain-of-custody, consider adding a JSON sidecar with file hashes (e.g., `--hashes sha256`).