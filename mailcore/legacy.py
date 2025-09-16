"""Utilities for converting mailcore models to legacy dict records."""

from __future__ import annotations

from typing import Dict

from .models import Message


def message_to_record(message: Message) -> Dict[str, object]:
    """Convert a :class:`Message` into the legacy dict format expected by writer/exporters."""
    to_line = ", ".join(message.to)
    cc_line = ", ".join(message.cc)
    bcc_line = ", ".join(message.bcc)
    sent = message.sent_at.isoformat() if message.sent_at else ""

    attachments = [
        {
            "id": att.id,
            "filename": att.filename,
            "size": att.size,
            "sha256": att.sha256,
            "content_type": att.content_type,
            "content_base64": att.data_base64,
        }
        for att in message.attachments
    ]

    sha256_hash = next((h.value for h in message.hashes if h.algorithm.lower() == "sha256"), None)

    body = message.body_text or ""

    return {
        "file": message.source_path.name if message.source_path else message.id,
        "source": message.source,
        "date": sent,
        "from": message.sender,
        "to": to_line,
        "cc": cc_line,
        "bcc": bcc_line,
        "subject": message.subject,
        "message_id": message.id,
        "body": body,
        "body_html": message.body_html,
        "attachments": attachments,
        "source_sha256": sha256_hash,
    }

