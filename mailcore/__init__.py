"""Shared mailcore package exposing neutral email data models."""

from .models import Mailbox, Folder, Message, Attachment, BodyPart, HashInfo
from .api import (
    load_messages_from_files,
    load_mailbox,
    load_single_message,
)

__all__ = [
    "Mailbox",
    "Folder",
    "Message",
    "Attachment",
    "BodyPart",
    "HashInfo",
    "load_messages_from_files",
    "load_mailbox",
    "load_single_message",
]
