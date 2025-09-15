from __future__ import annotations
import os
import shutil
from pathlib import Path
from typing import Callable, Optional


def resolve_readpst_path(get_embedded: Callable[[], Optional[Path]]):
    """Return a usable readpst executable path or None if unavailable."""
    embedded = get_embedded()
    if embedded:
        embedded_path = Path(embedded)
        if embedded_path.exists():
            return str(embedded_path)

    env_path = os.environ.get("MSGSECURE_READPST")
    if env_path:
        candidate = Path(env_path)
        if candidate.exists():
            return str(candidate)

    system_path = shutil.which("readpst")
    if system_path:
        return system_path

    return None
