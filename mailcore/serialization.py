"""Serialization helpers mapping mailcore models to viewer-friendly dictionaries."""
from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from .models import Attachment, BodyPart, HashInfo, Mailbox, Message


def _iso(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    try:
        return dt.isoformat()
    except Exception:
        return None


def mailbox_to_dict(mailbox: Mailbox) -> Dict[str, Any]:
    return {
        "SourcePath": str(mailbox.source_path),
        "DisplayName": mailbox.display_name,
        "Folders": [_folder_to_dict(f) for f in mailbox.folders],
    }


def _folder_to_dict(folder) -> Dict[str, Any]:
    return {
        "Id": folder.id,
        "Name": folder.name,
        "Path": folder.path,
        "Messages": [_message_to_dict(m) for m in folder.messages],
        "Subfolders": [_folder_to_dict(sub) for sub in folder.subfolders],
    }


def message_to_dict(message: Message) -> Dict[str, Any]:
    return {
        "Id": message.id,
        "Source": message.source,
        "SourcePath": str(message.source_path) if message.source_path else None,
        "Subject": message.subject,
        "Sender": message.sender,
        "To": list(message.to),
        "Cc": list(message.cc),
        "Bcc": list(message.bcc),
        "SentAt": _iso(message.sent_at),
        "BodyText": message.body_text,
        "BodyHtml": message.body_html,
        "Attachments": [
            {
                "Id": att.id,
                "Filename": att.filename,
                "Size": att.size,
                "Sha256": att.sha256,
            }
            for att in message.attachments
        ],
    }


def dict_to_message(data: Dict[str, Any]) -> Message:
    attachments = [
        Attachment(
            id=att.get("Id", ""),
            filename=att.get("Filename", ""),
            size=att.get("Size"),
            sha256=att.get("Sha256"),
        )
        for att in data.get("Attachments", [])
    ]
    sent_at_raw = data.get("SentAt")
    sent_at_value = None
    if isinstance(sent_at_raw, str) and sent_at_raw:
        try:
            sent_at_value = datetime.fromisoformat(sent_at_raw)
        except ValueError:
            sent_at_value = None

    return Message(
        id=data.get("Id", ""),
        source=data.get("Source", ""),
        source_path=Path(data["SourcePath"]) if data.get("SourcePath") else None,
        subject=data.get("Subject", ""),
        sender=data.get("Sender", ""),
        to=data.get("To", []),
        cc=data.get("Cc", []),
        bcc=data.get("Bcc", []),
        sent_at=sent_at_value,
        body_text=data.get("BodyText"),
        body_html=data.get("BodyHtml"),
        attachments=attachments,
    )
