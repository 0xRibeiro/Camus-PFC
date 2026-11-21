import secrets
from contextvars import ContextVar
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi.security import HTTPBearer
from pwdlib import PasswordHash
from pydantic import StringConstraints

from app.core.config import settings
from app.core.redis import redis_client

# guarda o id do usuario logado por request.
usuario_atual_id: ContextVar[int | None] = ContextVar("usuario_atual_id", default=None)

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


# codigo numerico de 6 digitos pra recuperacao de senha, guardado no redis por email
###### codigos de 6 numeros
# todo codigo q a pessoa digita no sistema e assim: vinculo do iot, convite de
# aquario, convite de grupo e recuperar senha. um formato so pra tudo

# tipo pros schemas: so aceita 6 numeros (com espaco nas pontas tirado antes)
CodigoSeisDigitos = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=6, max_length=6, pattern=r"^\d{6}$")
]


# secrets em vez de random pq o codigo da acesso a coisa (aquario, grupo, conta)
def sortear_codigo() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


# guarda o valor no redis com um codigo q ainda n ta em uso naquele prefixo.
# nx: so grava se a chave n existir, ai dois convites validos nunca tem o msm codigo
async def gerar_codigo_unico(prefixo: str, valor: str, validade_segundos: int) -> str:
    while True:
        codigo = sortear_codigo()
        gravou = await redis_client.set(f"{prefixo}:{codigo}", valor, ex=validade_segundos, nx=True)
        if gravou:
            return codigo


async def criar_codigo_reset(email: str) -> str:
    codigo = sortear_codigo()
    await redis_client.set(f"reset:{email}", codigo, ex=900)  # 15 min
    return codigo


async def validar_codigo_reset(email: str, codigo: str) -> bool:
    valor = await redis_client.get(f"reset:{email}")
    return valor == codigo


async def revogar_codigo_reset(email: str) -> None:
    await redis_client.delete(f"reset:{email}")


# Retorna o "sub" (id do usuário como string) se o token for válido
def decodificar_access_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None
    return payload.get("sub")
