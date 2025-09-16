"""MSG adapter bridging legacy extractor output into mailcore models."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from mailcombine.extractors import extract_from_msg

from ._common import record_to_message
from ..models import Message


def load_msg_message(path: Path) -> Message:
    """Load a single .msg file into a :class:`Message`."""
    record = extract_from_msg(path)
    return record_to_message(record)
