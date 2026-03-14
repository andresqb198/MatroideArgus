"""Application configuration from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    app_name: str = "Meridian"
    debug: bool = False
    environment: str = "development"

    # PostgreSQL
    database_url: str = "postgresql+asyncpg://meridian:meridian@localhost:5432/meridian"

    # ClickHouse
    clickhouse_host: str = "localhost"
    clickhouse_port: int = 8123
    clickhouse_database: str = "meridian"

    # Auth0
    auth0_domain: str = ""
    auth0_api_audience: str = ""
    auth0_algorithms: list[str] = ["RS256"]

    # Security
    secret_key: str = "change-me-in-production"

    model_config = {"env_prefix": "MERIDIAN_", "env_file": ".env"}


settings = Settings()
