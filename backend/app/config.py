
"""
Application configuration module.
"""

from pathlib import Path
from pydantic_settings import BaseSettings
from typing import List

# Always locate .env inside the backend directory
BACKEND_ENV_FILE = Path(__file__).resolve().parents[1] / ".env"


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/smart_irrigation"
    OPENWEATHERMAP_API_KEY: str = ""
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8001
    APP_ENV: str = "development"
    CORS_ORIGINS: str = "http://localhost:3001,http://127.0.0.1:3001"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    model_config = {
        "env_file": str(BACKEND_ENV_FILE),
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


settings = Settings()
