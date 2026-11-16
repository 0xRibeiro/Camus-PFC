from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.domains.dashboard import service
from app.domains.dashboard.schema import Agrupamento, DashboardRead
from app.domains.usuario.model import RoleUsuario
from app.domains.usuario.service import exige_role

# rotas da dashboard são apenas para o admin.
router = APIRouter(
    prefix="/admin/dashboard",
    tags=["admin"],
    dependencies=[Depends(exige_role(RoleUsuario.admin))],
)


# sem datas vai os ultimos 30 dias
@router.get("", response_model=DashboardRead)
async def obter_dashboard(inicio: date | None = None, fim: date | None = None,
    agrupamento: Agrupamento = Query(default="dia"),
    db: AsyncSession = Depends(get_async_session)) -> DashboardRead:
    return await service.obter_dashboard(db, inicio, fim, agrupamento)