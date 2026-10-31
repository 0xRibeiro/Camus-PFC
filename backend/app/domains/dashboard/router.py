from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.domains.dashboard import service
from app.domains.dashboard.schema import DashboardRead
from app.domains.usuario.model import RoleUsuario
from app.domains.usuario.service import exige_role

# rotas da dashboard são apenas para o admin.
router = APIRouter(
    prefix="/admin/dashboard",
    tags=["admin"],
    dependencies=[Depends(exige_role(RoleUsuario.admin))],
)


# rota pra obter dados. vou tentar com limita de 90 por enquanto
@router.get("", response_model=DashboardRead)
async def obter_dashboard(dias: int = Query(default=30, ge=1, le=90),
    db: AsyncSession = Depends(get_async_session)) -> DashboardRead:
    return await service.obter_dashboard(db, dias)