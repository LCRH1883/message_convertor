"""Public API surface for the mailcore shared library."""
from __future__ import annotations

from pathlib import Path
from typing import List, Sequence

from .adapters import load_eml_message, load_msg_message, load_pst_mailbox
from .models import Folder, Mailbox, Message

_MESSAGE_EXTS = {".msg", ".eml"}
_MAILBOX_EXTS = {".pst", ".ost"}


def load_single_message(path: Path) -> Message:
    """Load a single message file (.msg / .eml)."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    ext = path.suffix.lower()
    if ext == ".msg":
        return load_msg_message(path)
    if ext == ".eml":
        return load_eml_message(path)
    raise ValueError(f"Unsupported message extension: {path.suffix}")


def load_messages_from_files(paths: Sequence[Path]) -> List[Message]:
    messages: List[Message] = []
    for raw in paths:
        path = Path(raw)
        if path.is_dir():
            for child in sorted(path.rglob("*")):
                if child.suffix.lower() in _MESSAGE_EXTS:
                    messages.append(load_single_message(child))
        else:
            messages.append(load_single_message(path))
    return messages


def load_mailbox(path: Path) -> Mailbox:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    ext = path.suffix.lower()
    if path.is_dir():
        candidates = [p for p in path.rglob('*') if p.is_file() and p.suffix.lower() in _MESSAGE_EXTS]
        messages = load_messages_from_files(candidates)
        folder = Folder(id=path.name, name=path.name, path='/', messages=messages)
        return Mailbox(source_path=path, display_name=path.name, folders=[folder])
    if ext in _MAILBOX_EXTS:
        return load_pst_mailbox(path)
    if ext in _MESSAGE_EXTS:
        message = load_single_message(path)
        folder = Folder(id=path.stem or path.name, name=path.stem or path.name, path="/", messages=[message])
        return Mailbox(source_path=path, display_name=path.name, folders=[folder])
    raise ValueError(f"Unsupported mailbox source: {path}")
