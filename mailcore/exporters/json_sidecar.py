"""JSON sidecar exporter."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Optional

from ..legacy import message_to_record
from ..models import Message


def export_json(messages: Iterable[Message], dest: Path, *, source_label: str, output_text_path: Optional[Path]) -> None:
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "source_root": str(source_label),
        "output_text": str(output_text_path) if output_text_path else "",
        "messages": [message_to_record(msg) for msg in messages],
    }
    with open(dest, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
