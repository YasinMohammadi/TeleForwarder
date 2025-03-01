import logging
import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from utils.envconfig import EnvConfig
from utils.config_manager import ConfigManager
from utils.single_user_forwarder import SingleUserForwarder
from utils.admin_bot import AdminBot


def main() -> None:
    """
    Main entry point for the Single-User Telegram Forwarder.

    This function performs the following steps:
        1. Loads environment variables for Telethon credentials and the admin bot token.
        2. Loads dynamic configuration from config.json, including last_forwarded_id.
        3. Starts the Telethon user account for message forwarding.
        4. Initializes a BackgroundScheduler to execute the forwarding job based on a cron schedule.
        5. Starts the admin bot (via run_polling) to handle dynamic configuration commands.
    
    The forwarding job is scheduled as an asyncio task to run without blocking the main event loop.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting main...")

    env_cfg = EnvConfig()
    cfg_mgr = ConfigManager()

    forwarder = SingleUserForwarder(env_cfg, cfg_mgr)

    loop = asyncio.get_event_loop()
    logger.info("Logging in user account via Telethon.")
    loop.run_until_complete(forwarder.start_async())

    scheduler = BackgroundScheduler()
    scheduler.start()

    cron_expr = cfg_mgr.config.get("cron_schedule", "* * * * *")
    parts = cron_expr.split()
    if len(parts) != 5:
        logger.warning("Invalid cron expression, defaulting to '* * * * *'")
        parts = ["*", "*", "*", "*", "*"]
    trigger = CronTrigger(
        minute=parts[0],
        hour=parts[1],
        day=parts[2],
        month=parts[3],
        day_of_week=parts[4]
    )

    def forwarding_job() -> None:
        """
        Schedules the asynchronous forwarding job as an asyncio task.
        """
        logger.info("Forwarding job started.")
        loop.create_task(forwarder.forward_messages_async())

    scheduler.add_job(forwarding_job, trigger)
    logger.info("Forward job scheduled with cron: %s", cron_expr)

    admin_bot = AdminBot(env_cfg, cfg_mgr, forwarder)
    logger.info("Admin bot is starting run_polling...")
    admin_bot.run_polling()

    logger.info("Bot stopped. Shutting down scheduler...")
    scheduler.shutdown()
    logger.info("Scheduler shut down. Exiting.")


if __name__ == "__main__":
    main()
