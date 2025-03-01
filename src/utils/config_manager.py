"""
config_manager.py
=================

Manages dynamic settings from config.json, including static fields (e.g. supergroups) 
and dynamic fields (like last_forwarded_id).

This module provides the ConfigManager class, which loads the configuration from a JSON 
file, creates a default configuration if none exists, and offers helper methods to update 
individual configuration keys.
"""

import os
import json
import logging
from typing import Dict, Any

CONFIG_FILE = "config.json"
logger = logging.getLogger(__name__)


class ConfigManager:
    """
    Manages dynamic settings stored in config.json, including the last forwarded message ID.

    Attributes:
        filename (str): The path to the configuration file.
        config (Dict[str, Any]): The configuration data loaded from the file.
    """

    def __init__(self, filename: str = CONFIG_FILE) -> None:
        """
        Initializes the ConfigManager and loads the configuration from the file.

        Args:
            filename (str): The path to the configuration file (default is "config.json").
        """
        self.filename: str = filename
        self.config: Dict[str, Any] = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """
        Loads the configuration from the JSON file. If the file does not exist, a default 
        configuration is created, saved, and returned.

        Returns:
            Dict[str, Any]: The loaded or default configuration data.
        """
        if not os.path.exists(self.filename):
            logger.warning("config.json not found, creating default configuration.")
            default_config = {
                "source_channel": "@somechannel",
                "supergroups": ["@group1"],
                "cron_schedule": "* * * * *",
                "forward_mode": "new",
                "forward_order": "one_by_one",
                "time_interval_enabled": True,
                "start_hour": 8,
                "end_hour": 22,
                "user_accounts": [],
                "last_forwarded_id": 0
            }
            self.save_config(default_config)
            return default_config

        logger.debug("Loading configuration from %s", self.filename)
        with open(self.filename, "r") as f:
            return json.load(f)

    def save_config(self, cfg: Dict[str, Any]) -> None:
        """
        Saves the given configuration data to the JSON file and updates the in-memory config.

        Args:
            cfg (Dict[str, Any]): The configuration data to save.
        """
        logger.debug("Saving configuration to %s", self.filename)
        with open(self.filename, "w") as f:
            json.dump(cfg, f, indent=4)
        self.config = cfg

    def update_config(self, key: str, value: Any) -> None:
        """
        Updates a specific configuration key with a new value and saves the updated config.

        Args:
            key (str): The configuration key to update.
            value (Any): The new value to assign to the key.
        """
        logger.info("Updating configuration key '%s' with value: %r", key, value)
        self.config[key] = value
        self.save_config(self.config)

    def get_last_forwarded_id(self) -> int:
        """
        Retrieves the last forwarded message ID from the configuration.

        Returns:
            int: The stored last forwarded message ID, or 0 if not set.
        """
        return int(self.config.get("last_forwarded_id", 0))

    def set_last_forwarded_id(self, msg_id: int) -> None:
        """
        Updates the last forwarded message ID in the configuration.

        Args:
            msg_id (int): The new last forwarded message ID.
        """
        logger.info("Setting last_forwarded_id to %d", msg_id)
        self.update_config("last_forwarded_id", msg_id)
