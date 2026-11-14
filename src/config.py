import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


def _csv(name, default):
    return [value.strip().upper() if name == "COUNTRIES" else value.strip()
            for value in os.getenv(name, default).split(",") if value.strip()]


@dataclass(frozen=True)
class Settings:
    countries: list
    search_terms: list
    max_pages_per_search: int
    schedule_hours: int
    database_path: str
    telegram_bot_token: str
    telegram_chat_id: str


settings = Settings(
    countries=_csv("COUNTRIES", "BR,US,GB,CA"),
    search_terms=_csv("SEARCH_TERMS", "data analyst,business intelligence,BI analyst"),
    max_pages_per_search=max(1, int(os.getenv("MAX_PAGES_PER_SEARCH", "2"))),
    schedule_hours=max(1, int(os.getenv("SCHEDULE_HOURS", "24"))),
    database_path=os.getenv("DATABASE_PATH", "data/jobs.db"),
    telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
    telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", ""),
)
