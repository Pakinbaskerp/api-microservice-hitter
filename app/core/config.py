from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Python API Gateway"
    APP_VERSION: str = "1.0"

    # CORS (matches your monolith defaults)
    CORS_ALLOW_ORIGINS: list[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]

    # HTTPX
    HTTPX_TIMEOUT_SECONDS: float = 60.0

    # Optional external Gateway base URL (absolute http/https)
    API_GW_BASE: str | None = None

    # services.json at repo root
    SERVICES_FILE: Path = Path(__file__).resolve().parents[2] / "services.json"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
