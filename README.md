# mail-combine

Combine `.msg`, `.eml`, and `.pst` messages into a single searchable `.txt` file — **self-contained** builds for Linux and Windows.

- `.msg` parsing via `extract-msg`
- `.eml` parsing via Python `email` lib
- `.pst` via an **embedded** `readpst` binary shipped in `mailcombine/resources/<platform>/` (no external installs needed)
- Optional **attachments index** and **JSON sidecar** for chain-of-custody
- Minimal **GUI** (PySide6) included

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

# 4) Run (CLI)
python -m mailcombine.cli -i /path/to/mail -o combined_emails.txt --attachments --json
```

The tool recursively processes .msg and .eml. If .pst files are present:

- If an embedded readpst is found for your platform, they are converted internally and included.
- Otherwise the run continues (PST skipped with a notice).

### Usage (CLI)

```bash
mail-combine --input /path/to/folder --output combined_emails.txt
# or from source
python -m mailcombine.cli --input /path/to/folder --output combined_emails.txt
```

Options:

-i, --input Root folder to search (recursively). Default: ./msg_files

-o, --output Output text file. Default: combined_emails.txt

--encoding Output encoding (default utf-8)

--attachments Include an ATTACHMENTS section in text output (filename, size, sha256)

--json [path] Write JSON sidecar (default <output>.json)

--no-json Disable JSON sidecar

### New options:

--hashes [path] write a CSV (`type,parent_source,filename,size,sha256`) with message and attachment hashes (default <output>_hashes.csv)

--progress-file <path> write JSONL progress for GUI/monitoring (events: scan, processed, pst_start, pst_extracted, pst_skipped, done)

### GUI note:

The GUI shows a determinate progress bar while processing `.msg/.eml` (known totals) and switches to indeterminate during `.pst` conversion (unknown upfront). It finishes at 100% when the CLI signals `phase=done`.

### Text output example:

```
==========================================================================================
FILE: example.msg
SOURCE: /abs/path/to/example.msg
DATE: 2024-07-01T12:34:56-07:00
FROM: Alice <alice@example.com>
TO: Bob <bob@example.com>
SUBJECT: Project Update
MESSAGE-ID: <abc123@example.com>
ATTACHMENTS:
  - contract.pdf (45123 bytes) sha256=3f...c1

Body text...
==========================================================================================
```

### JSON sidecar structure:

```json
{
  "source_root": "...",
  "output_text": "...",
  "messages": [
    {
      "file": "...",
      "source": "...",          // For PST-derived: "pst_path :: extracted_eml_path"
      "date": "...",
      "from": "...",
      "to": "...",
      "subject": "...",
      "message_id": "...",
      "body": "...",
      "attachments": [
{"filename": "file.pdf", "size": 12345, "sha256": "..."}
      ],
      "source_sha256": "..."    // sha256 of original .msg/.eml file
    }
  ]
}
```

### Enable hashes (optional)

```bash
# default CSV path: <output>_hashes.csv
python -m mailcombine.cli -i /path/to/mail -o combined_emails.txt --hashes

# custom CSV path:
python -m mailcombine.cli -i /path/to/mail -o combined_emails.txt --hashes --hashes-path /evidence/report_hashes.csv
```

#### What the CSV contains

```
type,parent_source,filename,size,sha256
message,/path/mail/RE_meeting.msg,RE_meeting.msg,,89f3...c1b2
attachment,/path/mail/RE_meeting.msg,contract.pdf,45123,3a77...9d0e
```

- **type**: message or attachment  
- **parent_source**: the file it came from (PST-derived shows `pst_path :: extracted_eml_path`)  
- **filename**: item name  
- **size**: bytes (attachments); empty for message rows  
- **sha256**: fingerprint (content hash)

#### Verify hashes (later)

**Linux/macOS**

```bash
# compute a file's hash
sha256sum /path/to/file
# compare to the CSV’s sha256 value
```

**Windows (PowerShell)**

```powershell
Get-FileHash -Algorithm SHA256 "C:\path\to\file"
# Compare the "Hash" field to the CSV’s sha256 column
```

If the computed hash matches the CSV entry, the file is unchanged (integrity verified). If it differs, the content has changed.

---

## Build Self-Contained Binaries (PyInstaller)

### Linux (Ubuntu):
```bash
bash build_linux.sh
# output: dist/mail-combine-linux
```

### Windows (PowerShell):
```powershell
.\build_windows.ps1
# output: dist\mail-combine-win.exe
```

### GUI builds:

- Linux GUI: `pyinstaller build_linux_gui.spec` → `dist/mail-combine-linux-gui`
- Windows GUI: `pyinstaller build_windows_gui.spec` → `dist\mail-combine-win-gui.exe`

Both builds include only the platform's embedded readpst. Place it in `mailcombine/resources/<platform>/` before building.

---

## Repo layout

```
mail-combine/
├─ mailcombine/
│  ├─ __init__.py
│  ├─ cli.py
│  ├─ gui.py
│  ├─ extractors.py
│  ├─ writer.py
│  └─ resources/
│     ├─ linux64/readpst
│     └─ win64/readpst.exe
├─ requirements.txt
├─ requirements-gui.txt
├─ build_*.spec
├─ build_linux.sh
├─ build_windows.ps1
├─ .gitignore
└─ LICENSE
```

---

