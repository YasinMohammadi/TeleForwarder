import asyncio
import logging
from datetime import datetime, timezone
from telethon import TelegramClient
from .config_manager import ConfigManager
from .envconfig import EnvConfig
from .fetch_messages import fetch_all_today_messages

logger = logging.getLogger(__name__)


class SingleUserForwarder:
    """
    Forwards messages from a source Telegram channel to target supergroups
    using a single user account. The forwarding behavior depends on the
    configured mode ("today" or "new").

    Attributes:
        env (EnvConfig): Environment configuration (API credentials).
        cfg_mgr (ConfigManager): Manager for dynamic configuration.
        client (TelegramClient): Telethon client instance for the user account.
    """

    def __init__(self, env: EnvConfig, cfg_mgr: ConfigManager) -> None:
        """
        Initializes the forwarder with the given environment configuration and
        configuration manager. A Telethon client is created with a fixed session name.

        Args:
            env (EnvConfig): Environment configuration.
            cfg_mgr (ConfigManager): Configuration manager.
        """
        self.env = env
        self.cfg_mgr = cfg_mgr
        self.client = TelegramClient("user_session", env.api_id, env.api_hash)

    async def start_async(self) -> None:
        """
        Asynchronously logs in the user account. If no session file exists,
        Telethon will prompt for phone, code, and password as necessary.
        """
        logger.info("Logging in with Telethon user session...")
        await self.client.start()

    async def forward_messages_async(self) -> None:
        """
        Asynchronously fetches messages from the configured source channel and forwards
        them to the target supergroups. In "today" mode, all messages from the start
        of the day are fetched using a chunked approach. In "new" mode, only messages
        with an ID greater than the stored last_forwarded_id are forwarded.
        
        In "new" mode, the last_forwarded_id is updated after forwarding.
        """
        cfg = self.cfg_mgr.config
        now = datetime.now(timezone.utc)

        if cfg.get("time_interval_enabled", True):
            start_hour = cfg.get("start_hour", 8)
            end_hour = cfg.get("end_hour", 22)
            if not (start_hour <= now.hour < end_hour):
                logger.debug("Outside time window %d-%d, skipping forward.", start_hour, end_hour)
                return

        source_channel = cfg.get("source_channel", "@somechannel")
        try:
            channel_entity = await self.client.get_entity(source_channel)
        except Exception as e:
            logger.error("Failed to get entity for source channel %s: %s", source_channel, e)
            return

        forward_mode = cfg.get("forward_mode", "new")
        if forward_mode == "today":
            messages_to_forward = await fetch_all_today_messages(self.client, channel_entity)
        else:
            last_id = self.cfg_mgr.get_last_forwarded_id()
            msgs_chunk = await self.client.get_messages(channel_entity, limit=100, min_id=last_id)
            messages_to_forward = list(msgs_chunk)
            messages_to_forward.sort(key=lambda m: m.date)

        if not messages_to_forward:
            logger.debug("No messages to forward in %s mode.", forward_mode)
            return

        supergroups = cfg.get("supergroups", [])
        forward_order = cfg.get("forward_order", "one_by_one")
        for sg in supergroups:
            try:
                sg_entity = await self.client.get_entity(sg)
                if forward_order == "batch":
                    await self.client.forward_messages(sg_entity, messages_to_forward)
                    logger.info("Batch-forwarded %d messages to %s in %s mode", len(messages_to_forward), sg, forward_mode)
                else:
                    for msg in messages_to_forward:
                        await self.client.forward_messages(sg_entity, msg)
                        logger.debug("Forwarded message %d to %s", msg.id, sg)
                        await asyncio.sleep(1)
            except Exception as e:
                logger.error("Error forwarding to %s: %s", sg, e)

        if forward_mode == "new" and messages_to_forward:
            max_id = max(m.id for m in messages_to_forward)
            self.cfg_mgr.set_last_forwarded_id(max_id)

        logger.info("Forward operation complete in %s mode.", forward_mode)
