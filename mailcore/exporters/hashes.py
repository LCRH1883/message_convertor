"""Hash CSV exporter."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, List

from ..models import Message


def export_hashes(messages: Iterable[Message], dest: Path) -> None:
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    rows: List[List[str]] = []
    for msg in messages:
        sha256 = next((h.value for h in msg.hashes if h.algorithm.lower() == "sha256"), "")
        filename = msg.source_path.name if msg.source_path else msg.id
        rows.append(["message", msg.source, filename, "", sha256 or ""])
        for att in msg.attachments:
            size = att.size if att.size is not None else ""
            rows.append(["attachment", msg.source, att.filename, str(size), att.sha256 or ""])
    with open(dest, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["type", "parent_source", "filename", "size", "sha256"])
        writer.writerows(rows)
