from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from ..models import Attachment, BodyPart, HashInfo, Message


def _try_parse_datetime(raw: Optional[str]) -> Optional[datetime]:
    if not raw:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%d/%m/%Y %H:%M:%S", "%m/%d/%Y %H:%M:%S"):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(raw)  # Python 3.11 tolerant of offsets
    except ValueError:
        return None


def _split_addresses(value: Optional[str]) -> List[str]:
    if not value:
        return []
    parts = [p.strip() for p in value.replace(";", ",").split(",")]
    return [p for p in parts if p]


def record_to_message(record: Dict[str, Any], *, source_override: Optional[str] = None) -> Message:
    raw_source = record.get('source', record.get('file', ''))
    source_path = Path(raw_source) if raw_source else None
    if source_override:
        source_str = source_override
    else:
        source_str = raw_source or ''
    message_id = record.get('message_id') or (source_path.stem if source_path else source_str or 'message')
    body = record.get("body") or ""

    attachments_in = record.get("attachments") or []
    attachments: List[Attachment] = []
    for idx, att in enumerate(attachments_in, start=1):
        att_id = att.get("id") or f"{message_id}-att{idx}"
        attachments.append(
            Attachment(
                id=str(att_id),
                filename=att.get("filename") or att_id,
                size=att.get("size"),
                content_type=att.get("content_type"),
                sha256=att.get("sha256"),
                source_path=None,
                data_base64=att.get("content_base64"),
            )
        )

    hash_value = record.get("source_sha256")
    hashes = [HashInfo(algorithm="sha256", value=hash_value)] if hash_value else []

    body_parts = [BodyPart(content_type="text/plain", content=body)] if body else []

    return Message(
        id=str(message_id),
        source=source_str,
        source_path=source_path,
        subject=record.get("subject") or "",
        sender=record.get("from") or "",
        to=_split_addresses(record.get("to")),
        cc=_split_addresses(record.get("cc")),
        bcc=_split_addresses(record.get("bcc")),
        sent_at=_try_parse_datetime(record.get("date")),
        body_text=body or None,
        body_html=record.get("body_html"),
        body_parts=body_parts,
        attachments=attachments,
        headers={},
        hashes=hashes,
    )
