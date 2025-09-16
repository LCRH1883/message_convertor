"""EML adapter bridging legacy extractor output into mailcore models."""
from __future__ import annotations

from pathlib import Path

from mailcombine.extractors import extract_from_eml

from ._common import record_to_message
from ..models import Message


def load_eml_message(path: Path) -> Message:
    record = extract_from_eml(path)
    return record_to_message(record)
