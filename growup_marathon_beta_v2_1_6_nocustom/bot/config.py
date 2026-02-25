import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    bot_token: str
    admin_ids: set[int]
    moderator_ids: set[int]
    tz: str
    deadline_hour: int
    deadline_minute: int
    beta_days: int
    paid_days: int
    required_channel: str
    channel_announce_id: str
    app_name: str = "Grow Up Marathon Beta"


def _parse_int_set(value: str) -> set[int]:
    value = (value or "").strip()
    out: set[int] = set()
    if not value:
        return out
    for x in value.split(","):
        x = x.strip()
        if x.isdigit():
            out.add(int(x))
    return out


def load_settings() -> Settings:
    return Settings(
        bot_token=os.getenv("BOT_TOKEN", "").strip(),
        admin_ids=_parse_int_set(os.getenv("ADMIN_IDS", "")),
        moderator_ids=_parse_int_set(os.getenv("MODERATOR_IDS", "")),
        tz=os.getenv("TZ", "Asia/Tashkent").strip() or "Asia/Tashkent",
        deadline_hour=int(os.getenv("DEADLINE_HOUR", "23")),
        deadline_minute=int(os.getenv("DEADLINE_MINUTE", "0")),
        beta_days=int(os.getenv("BETA_DAYS", "7")),
        paid_days=int(os.getenv("PAID_DAYS", "14")),
        required_channel=os.getenv("REQUIRED_CHANNEL", "").strip(),
        channel_announce_id=os.getenv("CHANNEL_ANNOUNCE_ID", "").strip(),
        app_name=os.getenv("APP_NAME", "Grow Up Marathon Beta").strip() or "Grow Up Marathon Beta",
    )
