"""
admin_bot.py
============

This module implements the AdminBot class, which provides a Telegram-based 
administrative interface for dynamically managing configuration settings 
such as the source channel, target supergroups, forwarding mode, order, cron 
schedule, and time interval constraints.

The AdminBot uses the python-telegram-bot library (v21.10) to listen for 
commands from an administrator. Changes made via commands are stored in 
config.json using the ConfigManager.

Dependencies:
    - python-telegram-bot==21.10
    - Telethon
    - APScheduler
    - python-dotenv

Example:
    To start the admin bot, create an instance of AdminBot and call run_polling():
    
        env = EnvConfig()
        cfg_mgr = ConfigManager()
        forwarder = SingleUserForwarder(env, cfg_mgr)
        admin_bot = AdminBot(env, cfg_mgr, forwarder)
        admin_bot.run_polling()
"""

import logging
import json
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from .envconfig import EnvConfig
from .config_manager import ConfigManager
from .single_user_forwarder import SingleUserForwarder

logger = logging.getLogger(__name__)


class AdminBot:
    """
    A Telegram bot that handles administrative commands to update the forwarding 
    configuration. This bot does not send messages itself; it only listens for 
    commands and updates the configuration stored in config.json.

    Attributes:
        env (EnvConfig): Environment configuration (bot token).
        cfg_mgr (ConfigManager): Manager for dynamic configuration settings.
        forwarder (SingleUserForwarder): The forwarder instance that sends messages.
        app: The python-telegram-bot Application instance.
    """

    def __init__(self, env: EnvConfig, cfg_mgr: ConfigManager, forwarder: SingleUserForwarder) -> None:
        """
        Initializes the AdminBot with the provided environment configuration, 
        configuration manager, and forwarder.

        Args:
            env (EnvConfig): The environment configuration.
            cfg_mgr (ConfigManager): The configuration manager.
            forwarder (SingleUserForwarder): The forwarder instance.
        """
        self.env = env
        self.cfg_mgr = cfg_mgr
        self.forwarder = forwarder

        self.app = ApplicationBuilder().token(self.env.bot_token).build()
        self._add_handlers()

    def _add_handlers(self) -> None:
        """
        Registers the command handlers for the admin bot.
        """
        self.app.add_handler(CommandHandler("status", self.status))
        self.app.add_handler(CommandHandler("setchannel", self.setchannel))
        self.app.add_handler(CommandHandler("setgroups", self.setgroups))
        self.app.add_handler(CommandHandler("setmode", self.setmode))
        self.app.add_handler(CommandHandler("setorder", self.setorder))
        self.app.add_handler(CommandHandler("settimeinterval", self.settimeinterval))
        self.app.add_handler(CommandHandler("setcron", self.setcron))

    def run_polling(self) -> None:
        """
        Starts the bot in polling mode. This call blocks until the bot is stopped.
        """
        logger.info("AdminBot: Starting run_polling()...")
        self.app.run_polling()

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handles the /status command. Sends the current configuration in JSON format.

        Usage: /status
        """
        text = json.dumps(self.cfg_mgr.config, indent=4)
        await update.message.reply_text(f"Current config:\n{text}")

    async def setchannel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handles the /setchannel command. Updates the source channel in the configuration.

        Usage: /setchannel @channel_username
        """
        if context.args:
            channel = context.args[0].strip()
            self.cfg_mgr.update_config("source_channel", channel)
            await update.message.reply_text(f"Source channel updated: {channel}")
            logger.info("Source channel updated to %s", channel)
        else:
            await update.message.reply_text("Usage: /setchannel @channel_username")

    async def setgroups(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handles the /setgroups command. Overwrites the list of target supergroups.

        Usage: /setgroups @group1, @group2
        """
        if context.args:
            groups_str = " ".join(context.args)
            groups = [g.strip() for g in groups_str.split(",") if g.strip()]
            self.cfg_mgr.update_config("supergroups", groups)
            await update.message.reply_text(f"Supergroups updated: {groups}")
            logger.info("Supergroups updated to %r", groups)
        else:
            await update.message.reply_text("Usage: /setgroups @group1, @group2")

    async def setmode(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handles the /setmode command. Updates the forwarding mode.

        Usage: /setmode <today|new>

        - "today": Forward all messages from the start of the day each time.
        - "new": Only forward messages newer than the last forwarded message.
        """
        if context.args:
            mode = context.args[0].lower()
            if mode in ["today", "new"]:
                self.cfg_mgr.update_config("forward_mode", mode)
                await update.message.reply_text(f"Forward mode set to: {mode}")
                logger.info("Forward mode set to %s", mode)
            else:
                await update.message.reply_text("Invalid mode. Use 'today' or 'new'.")
        else:
            await update.message.reply_text("Usage: /setmode <today|new>")

    async def setorder(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handles the /setorder command. Updates the forwarding order.

        Usage: /setorder <batch|one_by_one>

        - "batch": Forwards all messages in one API call.
        - "one_by_one": Forwards messages individually.
        """
        if context.args:
            order = context.args[0].lower()
            if order in ["batch", "one_by_one"]:
                self.cfg_mgr.update_config("forward_order", order)
                await update.message.reply_text(f"Forward order set to: {order}")
                logger.info("Forward order set to %s", order)
            else:
                await update.message.reply_text("Invalid. Use 'batch' or 'one_by_one'.")
        else:
            await update.message.reply_text("Usage: /setorder <batch|one_by_one>")

    async def settimeinterval(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handles the /settimeinterval command. Enables or disables a daily time window 
        for forwarding messages.

        Usage:
            /settimeinterval always
            /settimeinterval <start> <end>

        - "always": Disables the time interval (messages can be forwarded any time).
        - Otherwise, sets the start and end hours.
        """
        if not context.args:
            await update.message.reply_text("Usage: /settimeinterval always OR /settimeinterval <start> <end>")
            return

        arg = context.args[0].lower()
        if arg == "always":
            self.cfg_mgr.update_config("time_interval_enabled", False)
            await update.message.reply_text("Time interval disabled.")
            logger.info("Time interval disabled.")
        elif len(context.args) == 2:
            try:
                st = int(context.args[0])
                ed = int(context.args[1])
                if 0 <= st < ed <= 24:
                    self.cfg_mgr.update_config("time_interval_enabled", True)
                    self.cfg_mgr.update_config("start_hour", st)
                    self.cfg_mgr.update_config("end_hour", ed)
                    await update.message.reply_text(f"Time interval set to {st}-{ed}")
                    logger.info("Time interval set to %d-%d", st, ed)
                else:
                    await update.message.reply_text("Invalid hours. Must be 0 <= start < end <= 24.")
            except ValueError:
                await update.message.reply_text("Please provide numeric hours.")
        else:
            await update.message.reply_text("Usage: /settimeinterval always OR <start> <end>")

    async def setcron(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handles the /setcron command. Updates the cron schedule for forwarding jobs.

        Usage: /setcron <cron_expr>
        Example: /setcron */5 * * * *
        """
        if context.args:
            cron_expr = " ".join(context.args)
            self.cfg_mgr.update_config("cron_schedule", cron_expr)
            await update.message.reply_text(f"Cron updated: {cron_expr}")
            logger.info("Cron schedule updated to %s", cron_expr)
        else:
            await update.message.reply_text("Usage: /setcron <cron_expr>")
