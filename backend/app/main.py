from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.mqtt import mqtt
from app.domains.auditoria.router import router as auditoria_router
from app.domains.conquistas.router import conquista_router
from app.domains.dashboard.router import router as dashboard_router
from app.domains.dispositivo import mqtt as dispositivo_mqtt
from app.domains.dispositivo.router import router as dispositivo_router
from app.domains.grupo.router import router as grupo_router
from app.domains.pontuacao.router import router as pontuacao_router
from app.domains.progresso.router import router as progresso_router
from app.domains.trilha.router import (
    alternativa_router,
    conteudo_router,
    modulo_router,
    
    questao_router,
    trilha_router,
)
from app.domains.upload.router import router as upload_router
from app.domains.usuario.router import admin_router as usuario_admin_router
from app.domains.usuario.router import router as usuario_router
from app.seed import seed_admin, seed_conquistas


# lifespan roda no startup, aqui só usamos pra seed admin
@asynccontextmanager
async def lifespan(app: FastAPI):
    await seed_admin()
    # testando a criação de conquistas
    await seed_conquistas()
    # conecta no broker e roda em paralelo com a api
    await mqtt.mqtt_startup()
    yield
    await mqtt.mqtt_shutdown()


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
app.include_router(conquista_router)
app.include_router(conteudo_router)
app.include_router(questao_router)
app.include_router(dashboard_router)
app.include_router(alternativa_router)
app.include_router(auditoria_router)
app.include_router(grupo_router)
app.include_router(pontuacao_router)
app.include_router(progresso_router)
app.include_router(upload_router)
app.include_router(dispositivo_router)

# serve as imagens enviadas em /uploads/<nome>
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")
register_exception_handlers(app)


@app.get("/health")
async def health():
    return {"status": "ok"}
