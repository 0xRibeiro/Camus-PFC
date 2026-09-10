from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.domains.trilha.router import (
    alternativa_router,
    conteudo_router,
    modulo_router,
    questao_router,
    trilha_router,
)
from app.domains.usuario.router import router as usuario_router

app = FastAPI(title="Gardiencor Hub API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(usuario_router)
app.include_router(trilha_router)
app.include_router(modulo_router)
app.include_router(conteudo_router)
app.include_router(questao_router)
app.include_router(alternativa_router)
register_exception_handlers(app)
add_pagination(app)


@app.get("/health")
async def health():
    return {"status": "ok"}
