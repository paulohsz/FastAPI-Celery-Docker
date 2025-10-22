from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Application
    APP_NAME: str = "FastAPI Celery App"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str
    DATABASE_URL_SYNC: str

    # RabbitMQ & Celery
    RABBITMQ_URL: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str


settings = Settings()
