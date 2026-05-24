from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://quiz_user:quiz_pass@db:5432/quiz_db"
    DATABASE_URL_SYNC: str = "postgresql+psycopg2://quiz_user:quiz_pass@db:5432/quiz_db"
    SECRET_KEY: str = "supersecretkeyforjwt1234567890"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
