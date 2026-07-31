from datetime import datetime, timedelta, timezone

import jwt
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

from app.core.config import settings

# Cria uma instância do hash de senha com o algoritmo recomendado. (argon2id é o atual)
password_hash = PasswordHash.recommended()


# Cria uma instância do OAuth2PasswordBearer, que é usada para extrair o token JWT do cabeçalho Authorization das requisições.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Função para gerar o hash da senha fornecida.
def criar_hash(password: str) -> str:
    return password_hash.hash(password)

# Verifica se a senha fornecida corresponde ao hash armazenado.
def verificar_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


# subject: o que vai dentro do "sub" do token, sempre vai ser o id do usuário.
def criar_access_token(subject: str) -> str:
    
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=settings.jwt_lifetime_seconds)
    
    payload = {
        "sub": subject, 
        "exp": expires_at
        }
    
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


# Retorna o "sub" (id do usuário como string) se o token for válido
def decodificar_access_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None
    return payload.get("sub")
