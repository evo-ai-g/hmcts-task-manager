from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables or .env."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "HMCTS Task Manager API"
    api_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./tasks.db"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]


settings = Settings()
