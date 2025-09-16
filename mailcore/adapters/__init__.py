"""Adapters bridging existing extractors into mailcore models."""

from .eml import load_eml_message
from .msg import load_msg_message
from .pst import load_pst_mailbox

__all__ = [
    "load_eml_message",
    "load_msg_message",
    "load_pst_mailbox",
]
