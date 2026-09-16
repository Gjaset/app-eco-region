import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    # API Settings
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "EcoRegión App"
    APP_ENV: str = os.getenv("APP_ENV", "development")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://ecoregion:ecoregion_pass@localhost:5432/ecoregion_db")

    # Security — fail fast en producción si no hay secreto real
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-only-change-me")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "11520"))  # 8 days

    # Nvidia OpenAI-compatible API
    NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY", "")
    NVIDIA_API_URL: str = os.getenv(
        "NVIDIA_API_URL",
        "https://integrate.api.nvidia.com/v1/chat/completions",
    )
    NVIDIA_MODEL: str = os.getenv("NVIDIA_MODEL", "openai/gpt-oss-20b")

    # Paths
    DATA_PATH: str = os.getenv("DATA_PATH", "./data")
    TEMPLATES_PATH: str = os.getenv("TEMPLATES_PATH", "./templates")
    GENERATED_PATH: str = os.getenv("GENERATED_PATH", "./generated")
    CORS_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS", "http://localhost:5173"
        ).split(",")
        if origin.strip()
    ]

settings = Settings()

_INSECURE_DEFAULTS = {"dev-only-change-me", "replace-with-a-random-secret", ""}
if settings.APP_ENV.lower() in {"production", "prod"} and settings.SECRET_KEY in _INSECURE_DEFAULTS:
    raise RuntimeError(
        "SECRET_KEY inseguro en producción: define SECRET_KEY con un valor aleatorio largo."
    )