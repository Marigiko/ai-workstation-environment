from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5433/workspace"
    redis_url: str = "redis://localhost:6379/0"
    qdrant_url: str = "http://localhost:6335"
    omniroute_url: str = "http://localhost:20128"
    secret_key: str = ""
    api_host: str = "0.0.0.0"
    api_port: int = 8080

    class Config:
        env_file = ".env"


settings = Settings()
