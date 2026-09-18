from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    # Application
    PROJECT_NAME: str = "SmartMail AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # CORS
    CORS_ORIGINS: str = (
        "http://localhost:5173"
    )

    # Database
    DATABASE_HOST: str
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # AI
    AI_PRIMARY_PROVIDER: str = "gemini"
    AI_FALLBACK_PROVIDER: str = "groq"

    GEMINI_API_KEY: str
    GEMINI_MODEL: str

    GROQ_API_KEY: str
    GROQ_MODEL: str

    # Email
    EMAIL_PROVIDER: str = "brevo"

    BREVO_API_KEY: str
    BREVO_SENDER_NAME: str
    BREVO_SENDER_EMAIL: str
    EMAIL_TEST_RECIPIENT: str
    BREVO_WEBHOOK_TOKEN: str

    # Redis / Celery
    REDIS_URL: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://"
            f"{self.DATABASE_USER}:"
            f"{self.DATABASE_PASSWORD}@"
            f"{self.DATABASE_HOST}:"
            f"{self.DATABASE_PORT}/"
            f"{self.DATABASE_NAME}"
        )

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.CORS_ORIGINS.split(
                ","
            )
            if origin.strip()
        ]


settings = Settings()