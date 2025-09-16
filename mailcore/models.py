"""Dataclasses describing email entities shared across tooling."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Sequence


@dataclass
class HashInfo:
    algorithm: str
    value: str


@dataclass
class Attachment:
    id: str
    filename: str
    size: Optional[int] = None
    content_type: Optional[str] = None
    sha256: Optional[str] = None
    source_path: Optional[Path] = None


@dataclass
class BodyPart:
    content_type: str
    content: str
    charset: Optional[str] = None


@dataclass
class Message:
    id: str
    source: str
    source_path: Optional[Path] = None
    subject: str = ""
    sender: str = ""
    to: Sequence[str] = field(default_factory=list)
    cc: Sequence[str] = field(default_factory=list)
    bcc: Sequence[str] = field(default_factory=list)
    sent_at: Optional[datetime] = None
    body_text: Optional[str] = None
    body_html: Optional[str] = None
    body_parts: List[BodyPart] = field(default_factory=list)
    attachments: List[Attachment] = field(default_factory=list)
    headers: Dict[str, str] = field(default_factory=dict)
    hashes: List[HashInfo] = field(default_factory=list)


@dataclass
class Folder:
    id: str
    name: str
    path: str
    messages: List[Message] = field(default_factory=list)
    subfolders: List["Folder"] = field(default_factory=list)


@dataclass
class Mailbox:
    source_path: Path
    display_name: str
    folders: List[Folder] = field(default_factory=list)

    def all_messages(self) -> List[Message]:
        stack = list(self.folders)
        collected: List[Message] = []
        while stack:
            folder = stack.pop()
            collected.extend(folder.messages)
            stack.extend(folder.subfolders)
        return collected
