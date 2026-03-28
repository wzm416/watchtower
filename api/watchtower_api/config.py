from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str | None = None
    cors_origins: str = "http://localhost:5173"
    # Comma-separated Google OAuth 2.0 client IDs (e.g. web client for GIS)
    google_client_ids: str = ""
    # Shared secret for Cloud Scheduler / internal cron (Bearer token value)
    cron_bearer_token: str | None = None

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def google_audience_list(self) -> list[str]:
        return [x.strip() for x in self.google_client_ids.split(",") if x.strip()]


def get_settings() -> Settings:
    return Settings()
