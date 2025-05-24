# teleforwarder\infrastructure\telegram_gateway.py

"""
Telegram gateway - the *only* Telethon-aware class.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Iterable, List

from loguru import logger
from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.tl.custom.message import Message
from telethon.tl.types import Dialog

from teleforwarder.domain.model import TextMessage
from teleforwarder.infrastructure.time_utils import start_of_today

class TelegramGateway:
    """IO-Port used by application layer."""

    def __init__(self, session: str, api_id: int, api_hash: str) -> None:
        self._client = TelegramClient(session, api_id, api_hash)

    @property
    def client(self) -> TelegramClient:
        """Expose the underlying Telethon client for event subscription."""
        return self._client

    async def connect(self) -> None:
        await self._client.start()
        logger.success(f"Logged in successfully")

    # ---------- Queries --------------------------------------------------

    async def fetch_today_texts(
        self, channel: str, tz: str
    ) -> List[TextMessage]:
        day_start = start_of_today(tz)
        msgs: list[TextMessage] = []
        offset = 0
        while True:
            chunk: Iterable[Message] = await self._client.get_messages(
                channel, limit=100, offset_id=offset
            )
            if not chunk:
                break
            for m in chunk:
                if m.date.replace(tzinfo=None) < day_start.replace(tzinfo=None):
                    break
                if m.message and m.media is None:
                    msgs.append(
                        TextMessage(
                            message_id=m.id,
                            date=m.date,
                            content=m.message,
                            raw=m,
                        )
                    )
            offset = chunk[-1].id
            if chunk[-1].date.replace(tzinfo=None) < day_start.replace(tzinfo=None):
                break
        msgs.reverse()
        logger.info(f"Fetched {len(msgs)} text messages from today.")
        return msgs

    async def list_public_groups(self) -> List[str]:
        """
        Retrieve all **public** groups/supergroups the logged-in user belongs to.
        """
        results: list[str] = []
        # async for over the iterator
        async for dialog in self._client.iter_dialogs():
            # Identify normal groups or megagroups
            is_group = dialog.is_group or getattr(dialog.entity, "megagroup", False)
            username = getattr(dialog.entity, "username", None)
            if is_group and username:
                handle = username if username.startswith("@") else f"@{username}"
                results.append(handle)

        logger.info("Found {} public groups.", len(results))
        return results

    # ---------- Commands -------------------------------------------------

    async def forward_text(
        self,
        targets: Iterable[str],
        message: TextMessage,
        delay: float,
    ) -> None:
        if not message.raw:
            logger.debug(f"Skipping empty text for msg_id={message.message_id}")
            return
        for tg in targets:
            try:
                await self._client.forward_messages(tg, message.raw)
                await asyncio.sleep(delay)
            except FloodWaitError as fwe:
                logger.warning("Flood-wait {fwe.seconds} s while sending to {tg}")
                await asyncio.sleep(fwe.seconds)
            except Exception as exc:  # noqa: BLE001
                logger.error(f"Cannot forward to {tg}: {exc}")
