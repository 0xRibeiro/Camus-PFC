from fastapi import FastAPI
from fastapi_pagination import add_pagination

from app.core.exceptions import register_exception_handlers
from app.domains.usuario.router import router as usuario_router

app = FastAPI(title="Gardiencor Hub API")

app.include_router(usuario_router)
register_exception_handlers(app)
add_pagination(app)


@app.get("/health")
async def health():
    return {"status": "ok"}

