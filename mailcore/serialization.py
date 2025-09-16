"""Serialization helpers for mailcore objects."""
from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from .models import Attachment, BodyPart, HashInfo, Mailbox, Message


def _normalize(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, list):
        return [_normalize(v) for v in value]
    if isinstance(value, dict):
        return {k: _normalize(v) for k, v in value.items()}
    return value


def mailbox_to_dict(mailbox: Mailbox) -> Dict[str, Any]:
    return _normalize(asdict(mailbox))


def message_to_dict(message: Message) -> Dict[str, Any]:
    return _normalize(asdict(message))


def dict_to_message(data: Dict[str, Any]) -> Message:
    attachments = [Attachment(**att) for att in data.get("attachments", [])]
    body_parts = [BodyPart(**part) for part in data.get("body_parts", [])]
    hashes = [HashInfo(**hashinfo) for hashinfo in data.get("hashes", [])]
    sent_at_raw = data.get("sent_at")
    sent_at_value = None
    if isinstance(sent_at_raw, str) and sent_at_raw:
        try:
            sent_at_value = datetime.fromisoformat(sent_at_raw)
        except ValueError:
            sent_at_value = None
    elif isinstance(sent_at_raw, datetime):
        sent_at_value = sent_at_raw

    source_path_raw = data.get("source_path")
    source_path_value = Path(source_path_raw) if source_path_raw else None

    return Message(
        id=data.get("id", ""),
        source=data.get("source", ""),
        source_path=source_path_value,
        subject=data.get("subject", ""),
        sender=data.get("sender", ""),
        to=data.get("to", []),
        cc=data.get("cc", []),
        bcc=data.get("bcc", []),
        sent_at=sent_at_value,
        body_text=data.get("body_text"),
        body_html=data.get("body_html"),
        body_parts=body_parts,
        attachments=attachments,
        headers=data.get("headers", {}),
        hashes=hashes,
    )
