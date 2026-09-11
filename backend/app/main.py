from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.domains.trilha.router import (
    alternativa_router,
    conteudo_router,
    modulo_router,
    questao_router,
    trilha_router,
)
from app.domains.usuario.router import admin_router as usuario_admin_router
from app.domains.usuario.router import router as usuario_router
from app.seed import seed_admin


# lifespan roda no startup, aqui só usamos pra seed admin
@asynccontextmanager
async def lifespan(app: FastAPI):
    await seed_admin()
    yield


app = FastAPI(title="Projeto Camus - API", lifespan=lifespan)

# libera o front pra chamar a api (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,  # deixa mandar o header Authorization / cookie
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(usuario_router)
app.include_router(usuario_admin_router)
app.include_router(trilha_router)
app.include_router(modulo_router)
app.include_router(conteudo_router)
app.include_router(questao_router)
app.include_router(alternativa_router)
register_exception_handlers(app)


@app.get("/health")
async def health():
    return {"status": "ok"}
