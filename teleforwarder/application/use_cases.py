# teleforwarder\application\use_cases.py

"""
Use-case orchestration (no framework code).
"""

from __future__ import annotations

import asyncio
from typing import List
from datetime import datetime
from zoneinfo import ZoneInfo
from telethon import events

from loguru import logger

from ..config import settings
from ..domain.model import TextMessage
from ..domain.services import round_robin
from ..infrastructure.telegram_gateway import TelegramGateway


class ForwardDailyTexts:
    """
    Use-case: endlessly forward today's text messages in round-robin order.
    """

    def __init__(self, gateway: TelegramGateway) -> None:
        self._gw = gateway
        self._messages: List[TextMessage] = []
        self._idx: int = 0

    # ---------- helpers -----------------
    async def _load_targets(self) -> List[str]:
        if settings.forward_to == "all":
            return await self._gw.list_public_groups()
        return settings.target_groups

    async def _refresh_messages(self) -> None:
        self._messages = await self._gw.fetch_today_texts(
            settings.source_channel, settings.timezone
        )
        self._idx = 0

    def _in_allowed_window(self) -> bool:
        """
        Check if current local time (in settings.timezone) is within
        [start_hour, end_hour).
        """
        now_local = datetime.now(ZoneInfo(settings.timezone))
        return settings.start_hour <= now_local.hour < settings.end_hour

    # ---------- public API ---------------
    async def daily_refresh(self) -> None:
        await self._refresh_messages()

    async def run_forever(self) -> None:        

        while True:
            if not self._in_allowed_window():
                logger.debug(
                    f"Outside allowed window {settings.start_hour}:00-{settings.end_hour}:00 ({settings.timezone}); sleeping {settings.sleep_between_messages}s."
                )
                await asyncio.sleep(settings.sleep_between_messages)
                continue
            await self._refresh_messages()
            targets = await self._load_targets()
            if not targets:
                logger.error("No groups configured; stopping forwarder loop.")
                return
            if not self._messages:
                await asyncio.sleep(settings.sleep_between_messages)
                continue

            for self._idx, msg in round_robin(self._messages, self._idx):
                logger.info(f"Forwarding msg {msg.message_id} (idx {self._idx})")
                await self._gw.forward_text(
                    targets, msg, delay=1  # delay between SAME msg / next group
                )
                await asyncio.sleep(settings.sleep_between_messages)




class ForwardOnNew:
    """
    Subscribe to NewMessage events on the source channel and forward each
    new *text-only* message immediately, one-by-one to the configured targets.
    """

    def __init__(self, gateway: TelegramGateway) -> None:
        self._gw = gateway

    async def start(self) -> None:
        client = self._gw.client
        channel = settings.source_channel

        @client.on(events.NewMessage(chats=channel))
        async def handler(ev: events.NewMessage.Event) -> None:
            m = ev.message
            # skip anything without plain text
            if not m.text:
                return

            tm = TextMessage(
                message_id=m.id,
                date=m.date,
                content=m.text,
                raw=m,
            )

            # decide targets just like daily mode
            if settings.forward_to == "all":
                targets = await self._gw.list_public_groups()
            else:
                targets = settings.target_groups

            if not targets:
                logger.error(f"No targets in listen mode; dropping msg {m.id}")
                return

            # forward one by one with 1s gap per group
            await self._gw.forward_text(targets, tm, delay=1)
            logger.info(f"Listen-mode forwarded msg {m.id} to {len(targets)} targets")

        # connect & run until Ctrl+C
        await client.run_until_disconnected()
