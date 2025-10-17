import os
from dataclasses import dataclass

@dataclass
class Cfg:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me")
    TZ: str = os.getenv("TZ", "Europe/Istanbul")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data.sqlite3")
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "*")
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_ADMIN_CHAT_ID: str = os.getenv("TELEGRAM_ADMIN_CHAT_ID", "")
    TELEGRAM_WEBHOOK_URL: str = os.getenv("TELEGRAM_WEBHOOK_URL", "")
    REQUIRE_ROOM_KEY: bool = os.getenv("REQUIRE_ROOM_KEY", "false").lower() == "true"
    MAX_ROOM_MEMBERS: int = int(os.getenv("MAX_ROOM_MEMBERS", "10"))
    ENABLE_CALLS: bool = os.getenv("ENABLE_CALLS", "true").lower() == "true"
    TURN_URL: str = os.getenv("TURN_URL", "")
    TURN_USERNAME: str = os.getenv("TURN_USERNAME", "")
    TURN_CREDENTIAL: str = os.getenv("TURN_CREDENTIAL", "")
    RATE_LIMIT_HOURLY: int = int(os.getenv("RATE_LIMIT_HOURLY", "300"))
    RATE_LIMIT_DAILY: int = int(os.getenv("RATE_LIMIT_DAILY", "2000"))

cfg = Cfg()
