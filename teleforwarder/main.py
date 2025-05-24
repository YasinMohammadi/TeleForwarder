"""
Framework glue code and bootstrap.
"""

import asyncio
from loguru import logger
from dotenv import load_dotenv

from .config import settings
from .infrastructure.logger_setup import logger as _ 
from .infrastructure.telegram_gateway import TelegramGateway
from .application.use_cases import ForwardDailyTexts, ForwardOnNew


load_dotenv()



async def bootstrap() -> None:
    gw = TelegramGateway(
        session=settings.session_name,
        api_id=settings.api_id,
        api_hash=settings.api_hash
    )
    await gw.connect()

    if settings.forward_mode == "listen":
        logger.info("Starting real-time listen mode…")
        usecase = ForwardOnNew(gw)
        await usecase.start()

    else:  # default to daily
        logger.info("Starting daily forward mode…")
        usecase = ForwardDailyTexts(gw)
        # schedule daily fetch at midnight (or your cron)
        await usecase.run_forever()

def main() -> None:
    try:
        asyncio.run(bootstrap())
    except KeyboardInterrupt:
        logger.warning("Shutting down on user interrupt")

if __name__ == "__main__":
    main()