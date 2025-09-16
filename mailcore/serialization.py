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
    return {
        "source_path": str(mailbox.source_path),
        "display_name": mailbox.display_name,
        "folders": [folder_to_dict(folder) for folder in mailbox.folders],
    }


def folder_to_dict(folder) -> Dict[str, Any]:
    return {
        "id": folder.id,
        "name": folder.name,
        "path": folder.path,
        "messages": [message_to_dict(msg) for msg in folder.messages],
        "subfolders": [folder_to_dict(sub) for sub in folder.subfolders],
    }


def message_to_dict(message: Message) -> Dict[str, Any]:
    return {
        "id": message.id,
        "source": message.source,
        "source_path": str(message.source_path) if message.source_path else None,
        "subject": message.subject,
        "sender": message.sender,
        "to": list(message.to),
        "cc": list(message.cc),
        "bcc": list(message.bcc),
        "sent_at": message.sent_at.isoformat() if message.sent_at else None,
        "body_text": message.body_text,
        "body_html": message.body_html,
        "attachments": [
            {
                "id": att.id,
                "filename": att.filename,
                "size": att.size,
                "sha256": att.sha256,
            }
            for att in message.attachments
        ],
    }


def dict_to_message(data: Dict[str, Any]) -> Message:
    attachments = [Attachment(id=att.get("id", ""), filename=att.get("filename", ""), size=att.get("size"), sha256=att.get("sha256")) for att in data.get("attachments", [])]
    sent_at_raw = data.get("sent_at")
    sent_at_value = None
    if isinstance(sent_at_raw, str) and sent_at_raw:
        try:
            sent_at_value = datetime.fromisoformat(sent_at_raw)
        except ValueError:
            sent_at_value = None
    return Message(
        id=data.get("id", ""),
        source=data.get("source", ""),
        source_path=Path(data["source_path"]) if data.get("source_path") else None,
        subject=data.get("subject", ""),
        sender=data.get("sender", ""),
        to=data.get("to", []),
        cc=data.get("cc", []),
        bcc=data.get("bcc", []),
        sent_at=sent_at_value,
        body_text=data.get("body_text"),
        body_html=data.get("body_html"),
        attachments=attachments,
    )
