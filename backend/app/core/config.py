from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Lê essas variáveis do arquivo .env pelo nome.
    model_config = {"env_file": ".env"}

    database_url: str
    redis_url: str
    jwt_secret: str
    jwt_lifetime_seconds: int = 900  # access token, 15 min
    refresh_token_lifetime_seconds: int = 604800  # refresh, 7 dias
    cors_origins: list[str] = ["http://localhost:3000"]  # origins liberados no CORS
    # dados do admin semeado no boot. sem email+senha o seed n roda
    admin_username: str = "admin"
    admin_email: str | None = None
    admin_password: str | None = None
    debug: bool = False


settings = Settings()
