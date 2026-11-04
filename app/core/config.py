from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr
from sqlalchemy import URL


class Settings(BaseSettings):
    APP_NAME: str = "ErrorLog Management"
    APP_VERSION: str = "1.0.0"
    DATABASE_NAME: str
    DATABASE_USER: str
    DATABASE_PASSWORD: SecretStr
    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_DRIVER: str = "postgresql+asyncpg"
    JWT_SECRET_KEY: SecretStr = Field(
        default="None", min_length=32, description="Secret key for JWT token generation"
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ADMIN_USERNAME: str | None = None
    ADMIN_EMAIL: str | None = None
    ADMIN_PASSWORD: SecretStr | None = None
    MANAGER_USERNAME: str | None = None
    MANAGER_EMAIL: str | None = None
    MANAGER_PASSWORD: SecretStr | None = None
    MAILJET_API_KEY: str | None = None
    MAILJET_API_SECRET: SecretStr | None = None
    MAIL_FROM: str | None = None
    MAILJET_FROM: str | None = None
    MAILJET_APPROVAL_FROM: str | None = None
    MAIL_FROM_NAME: str = "ErrorLog Management"

    @property
    def database_url(self) -> str:
        return URL.create(
            drivername=self.DATABASE_DRIVER,
            username=self.DATABASE_USER,
            password=self.DATABASE_PASSWORD.get_secret_value(),
            host=self.DATABASE_HOST,
            port=self.DATABASE_PORT,
            database=self.DATABASE_NAME,
        ).render_as_string(hide_password=False)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
