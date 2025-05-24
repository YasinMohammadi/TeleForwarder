# teleforwarder\domain\services.py

"""
Pure-domain services (no IO).
"""

from __future__ import annotations

from typing import Iterable, List


def round_robin(messages: List, index: int) -> Iterable[tuple[int, object]]:
    """
    Infinite generator that yields (next_index, message) tuples in round-robin
    order. Caller keeps the `index` cursor.

    Usage
    -----
    >>> idx = 0
    >>> for idx, msg in round_robin(msgs, idx):
    ...     process(msg); time.sleep(...)
    """
    if not messages:
        return
    length = len(messages)
    i = index
    for _ in range(length):
        yield i, messages[i]
        i = (i + 1) % length
