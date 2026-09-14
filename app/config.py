from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения. Значения читаются из переменных окружения / .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Общие
    APP_NAME: str = "User Service"
    DEBUG: bool = False
    TESTING: bool = False

    # База данных
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "user_service"
    DATABASE_URL: str | None = None

    # Аутентификация / cookie-сессия
    SESSION_COOKIE_NAME: str = "session_id"
    SESSION_TTL_SECONDS: int = 60 * 60 * 24  # 24 часа
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "lax"

    @property
    def DB_DSN(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgres://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


settings = Settings()
