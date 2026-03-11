from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
import os
load_dotenv()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=("env.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    mongodb_uri: str = os.getenv("MONGODB_URI")
    mongodb_db: str = os.getenv("MONGODB_DB")

    # JWT
    jwt_secret: str = os.getenv("JWT_SECRET")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM")
    jwt_expires_minutes: int = os.getenv("JWT_EXPIRES_MINUTES")

    # SMS (Twilio)
    twilio_account_sid: str | None = os.getenv("TWILIO_ACCOUNT_SID")
    twilio_auth_token: str | None = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_from_number: str | None = os.getenv("TWILIO_FROM_NUMBER")

    # Email (SMTP)
    email_user: str = os.getenv("EMAIL_USER")
    email_pass: str = os.getenv("EMAIL_PASS")
    email_from_name: str = "ICU Early Warning System"
    smtp_host: str = os.getenv("SMTP_HOST")
    smtp_port: int = os.getenv("SMTP_PORT")

    # LangChain + Ollama
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL")
    ollama_model: str = os.getenv("OLLAMA_MODEL")

    # Web search/scrape
    search_results: int = os.getenv("SEARCH_RESULTS")
    scrape_timeout_seconds: int = os.getenv("SCRAPE_TIMEOUT_SECONDS")
    max_article_chars: int = os.getenv("MAX_ARTICLE_CHARS")

    # Monitoring
    monitor_interval_seconds: int = os.getenv("MONITOR_INTERVAL_SECONDS")
    sustained_alert_points: int = int(os.getenv("SUSTAINED_ALERT_POINTS", "3"))
    sustained_alert_cooldown_minutes: int = int(os.getenv("SUSTAINED_ALERT_COOLDOWN_MINUTES", "15"))

    # CORS
    cors_origins: str = os.getenv("CORS_ORIGINS")

    def parsed_cors_origins(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()

