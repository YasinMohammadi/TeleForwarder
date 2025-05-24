# teleforwarder\application\use_cases.py

"""
Domain entities and value objects.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class TextMessage:
    """Immutable value object representing a **text-only** Telegram message."""

    message_id: int
    date:       datetime
    content:    str
    raw:        Any            # original Telethon object (optional)
