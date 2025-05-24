"""Time-zone helpers used by infrastructure / application layers."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo


def start_of_today(tz_name: str) -> datetime:
    """
    Return ``YYYY-MM-DD 00:00:00`` in *tz_name* as an offset-aware ``datetime``.

    Parameters
    ----------
    tz_name:
        IANA time-zone string (e.g. ``"Asia/Tehran"``).
    """
    now = datetime.now(ZoneInfo(tz_name))
    return now.replace(hour=0, minute=0, second=0, microsecond=0)
