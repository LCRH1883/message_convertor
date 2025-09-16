"""Text exporter leveraging legacy writer module."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from mailcombine.writer import write_header, write_record

from ..legacy import message_to_record
from ..models import Message


def export_text(messages: Iterable[Message], dest: Path, *, source_label: str, show_attachments: bool = False, encoding: str = "utf-8") -> None:
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, "w", encoding=encoding, errors="replace") as out:
        write_header(out, source_label)
        for msg in messages:
            rec = message_to_record(msg)
            write_record(out, rec, show_attachments=show_attachments)
