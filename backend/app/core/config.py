from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ORACLE_DSN: str | None = None
    ORACLE_USER: str | None = None
    ORACLE_PASSWORD: str | None = None
    ORACLE_HOST: str | None = None
    ORACLE_PORT: str | None = None
    ORACLE_SERVICE_NAME: str | None = None
    ATTENDANCE_DAYS_REQUIRED: int = 3

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()