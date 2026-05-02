from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://edutrack:password@localhost:5432/edutrack_db"
    SECRET_KEY: str = "change-this-secret-key-in-production-at-least-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    INITIAL_SKILL_COINS: float = 100.0
    LESSON_CREATE_REWARD: float = 20.0

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
