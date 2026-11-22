from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.core.config import settings

# ------- rate limit por ip, os contadores ficam no redis

# vale pra todas as rotas
LIMITE_GERAL = "300/minute"

# login e rotas com codigo de 6 numeros
LIMITE_TENTATIVAS = "10/15minutes"
LIMITE_CADASTRO = "10/hour"
# esqueci a senha, cada pedido manda um email
LIMITE_EMAIL_SENHA = "5/15minutes"

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[LIMITE_GERAL],
    storage_uri=settings.redis_url,
)


# resposta quando estoura o limite
async def limite_estourado(request: Request, erro: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={"detail": "Muitas tentativas. Espere alguns minutos e tente de novo."},
    )
