from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Lê essas variáveis do arquivo .env pelo nome.
    model_config = {"env_file": ".env"}

    database_url: str
    redis_url: str
    jwt_secret: str
    jwt_lifetime_seconds: int = 900
    refresh_token_lifetime_seconds: int = 604800
    cors_origins: list[str] = ["http://localhost:3000"]
    debug: bool = False


settings = Settings()
