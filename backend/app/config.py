"""Application configuration loaded from environment variables."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Read from a local `.env` file when present; real env vars still win.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://postgres:postgres@localhost:5432/study_scheduler"
    secret_key: str = "change-me-to-a-long-random-string"
    access_token_expire_minutes: int = 1440
    # Comma-separated origins; parsed into a list by `cors_origin_list`.
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    # Secret required to call POST /admin/seed on a hosted deployment. Empty
    # disables the endpoint. Set SEED_TOKEN in the host's env vars.
    seed_token: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
