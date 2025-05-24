"""
Loguru configuration used by the whole app.
"""

from loguru import logger

logger.add("forwarder.log", rotation="10 MB", retention="10 days")
