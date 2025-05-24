


from __future__ import annotations

from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment or `.env`.
    """

    api_id: int = Field(..., alias="TELEGRAM_API_ID")
    api_hash: str = Field(..., alias="TELEGRAM_API_HASH")
    session_name: str = Field("user_session", alias="TELEGRAM_SESSION")

    source_channel: str = Field(..., alias="SOURCE_CHANNEL")

    forward_to: str = Field("list", alias="FORWARD_TO")  # "list" | "all"
    target_groups: List[str] = Field(..., alias="TARGET_GROUPS")

    timezone: str = Field("Asia/Tehran", alias="TIMEZONE")
    start_hour: int = Field(8, ge=0, le=23, alias="START_HOUR")
    end_hour: int = Field(22, ge=1, le=24, alias="END_HOUR")

    forward_mode: str = Field("daily", alias="FORWARD_MODE")

    sleep_between_messages: int = Field(60, ge=1, alias="SLEEP_BETWEEN_MESSAGES")

    model_config = SettingsConfigDict(
        env_file = str(Path(__file__).parent.parent / ".env"), 
        extra="ignore"
    )


settings = Settings()
