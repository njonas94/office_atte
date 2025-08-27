from pydantic import BaseSettings

class Settings(BaseSettings):
    ORACLE_DSN: str | None = None
    ORACLE_USER: str | None = None
    ORACLE_PASSWORD: str | None = None
    ATTENDANCE_DAYS_REQUIRED: int = 3

    class Config:
        env_file = ".env"

settings = Settings()