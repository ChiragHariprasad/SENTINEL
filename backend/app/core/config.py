from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "SENTINEL"
    DATABASE_URL: str = "postgresql+asyncpg://sentinel:sentinel@localhost:5432/sentinel"
    REDIS_URL: str = "redis://localhost:6379/0"
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_HOURS: int = 24
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "mistral-small-latest"
    LLM_BASE_URL: str = "https://api.mistral.ai/v1"
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"


settings = Settings()
