from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Lê essas variáveis do arquivo .env pelo nome.
    model_config = {"env_file": ".env"}

    database_url: str
    redis_url: str
    jwt_secret: str
    jwt_lifetime_seconds: int = 900  # access token, 15 min
    refresh_token_lifetime_seconds: int = 604800  # refresh, 7 dias
    cors_origins: list[str] = ["http://localhost:3000"]
    # dados do admin semeado no boot. sem email+senha o seed n roda
    admin_username: str = "admin"
    admin_email: str | None = None
    admin_password: str | None = None
    debug: bool = False

    # smtp do gmail
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str
    smtp_password: str  # senha de app

    # upload de imagem generico (artigo, foto de trilha...)
    api_url: str = "http://localhost:8000"  # monta a url completa q volta pro front
    upload_dir: str = "uploads"
    upload_max_bytes: int = 10 * 1024 * 1024  # 10 MB

    # broker mqtt do iot
    mqtt_host: str = "localhost"
    mqtt_port: int = 1883

    # influxdb das leituras do iot
    influx_url: str = "http://localhost:8086"
    influx_token: str = ""
    influx_org: str = "camus"
    influx_bucket: str = "leituras"


settings = Settings()
