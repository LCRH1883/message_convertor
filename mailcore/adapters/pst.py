"""PST adapter using existing readpst pipeline."""
from __future__ import annotations

import tempfile
from pathlib import Path
from typing import List

from mailcombine.extractors import extract_from_eml, iter_eml_paths_from_pst

from ._common import record_to_message
from ..models import Folder, Mailbox, Message


def load_pst_mailbox(path: Path) -> Mailbox:
    messages: List[Message] = []
    with tempfile.TemporaryDirectory(prefix="mailcore_pst_") as tdir:
        temp_root = Path(tdir)
        for eml_path in iter_eml_paths_from_pst(path, temp_root):
            record = extract_from_eml(eml_path)
            messages.append(record_to_message(record))
    root_folder = Folder(id=path.stem or str(path), name=path.stem or path.name, path="/", messages=messages)
    return Mailbox(source_path=path, display_name=path.name, folders=[root_folder])
