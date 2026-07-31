from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Lê essas variáveis do arquivo .env pelo nome.
    model_config =  {"env_file": ".env"} 

    database_url: str
    jwt_secret: str
    jwt_lifetime_seconds: int = 3600
    debug: bool = False


settings = Settings()
