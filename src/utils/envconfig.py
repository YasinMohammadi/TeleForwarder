"""
envconfig.py

Loads environment variables for admin bot token and Telethon user credentials.
"""

import os
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class EnvConfig:
    """
    Environment configuration from .env.
    
    Attributes:
        bot_token (str): Admin bot token from BotFather
        api_id (int): Telegram API ID for Telethon
        api_hash (str): Telegram API hash for Telethon
    """
    def __init__(self) -> None:
        logger.debug("Initializing EnvConfig...")

        self.bot_token: str = os.environ.get("TELEGRAM_BOT_TOKEN")

        try:
            self.api_id: int = int(os.environ.get("TELEGRAM_API_ID"))
        except ValueError:
            logger.error("TELEGRAM_API_ID must be an integer.")
            raise ValueError("TELEGRAM_API_ID must be an integer.")
        
        self.api_hash: str = os.environ.get("TELEGRAM_API_HASH")

        logger.debug(
            "EnvConfig loaded: bot_token=%s, api_id=%d, api_hash=%s",
            self.bot_token,
            self.api_id,
            self.api_hash
        )
