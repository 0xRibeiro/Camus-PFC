import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi.security import HTTPBearer
from pwdlib import PasswordHash

from app.core.config import settings
from app.core.redis import redis_client

# cria uma instância do hash de senha com o algoritmo recomendado. (argon2id é o atual)
password_hash = PasswordHash.recommended()


# cria uma instância do OAuth2PasswordBearer, que é usada para extrair o token JWT do cabeçalho Authorization das requisições.
bearer_scheme = HTTPBearer()


# função para gerar o hash da senha fornecida.
def criar_hash(password: str) -> str:
    return password_hash.hash(password)


# verifica se a senha fornecida corresponde ao hash armazenado.
def verificar_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


# o que vai dentro do "sub" do token, sempre vai ser o id do usuário
def criar_access_token(subject: str) -> str:

    expires_at = datetime.now(timezone.utc) + timedelta(
        seconds=settings.jwt_lifetime_seconds
    )

    payload = {"sub": subject, "exp": expires_at}

    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


# cria o refrash token com o id do usuario e tempo de expiracao automatioc vindo das settings
async def criar_refresh_token(subject: str) -> str:
    token = secrets.token_urlsafe(32)  # token string limpa para url
    await redis_client.set(
        f"refresh:{token}", subject, ex=settings.refresh_token_lifetime_seconds
    )
    return token


# busca o refresh token e retorna
async def validar_refresh_token(token: str) -> str | None:
    subject = await redis_client.get(f"refresh:{token}")
    if subject is None:
        return None
    assert isinstance(subject, str)
    return subject


async def revogar_refresh_token(token: str) -> None:
    await redis_client.delete(f"refresh:{token}")


# Retorna o "sub" (id do usuário como string) se o token for válido
def decodificar_access_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None
    return payload.get("sub")
