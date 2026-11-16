from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.domains.dashboard import service
from app.domains.dashboard.schema import (
    Agrupamento,
    DashboardConteudoRead,
    DashboardRead,
    DashboardTrilhaRead,
)
from app.domains.trilha.model import Conteudo, Trilha
from app.domains.trilha.router import gerenciar_trilhas, validar_item
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


# msm regra de quem edita a trilha, no grupo o main poe o prefixo com o dono
trilha_router = APIRouter(tags=["trilhas"])


@trilha_router.get("/trilhas/{id}/dashboard", response_model=DashboardTrilhaRead,
    dependencies=[Depends(gerenciar_trilhas), Depends(validar_item(Trilha))])
async def obter_dashboard_trilha(id: int, inicio: date | None = None, fim: date | None = None,
    agrupamento: Agrupamento = Query(default="dia"),
    db: AsyncSession = Depends(get_async_session)) -> DashboardTrilhaRead:
    return await service.obter_dashboard_trilha(db, id, inicio, fim, agrupamento)


@trilha_router.get("/conteudos/{id}/dashboard", response_model=DashboardConteudoRead,
    dependencies=[Depends(gerenciar_trilhas), Depends(validar_item(Conteudo))])
async def obter_dashboard_conteudo(id: int, inicio: date | None = None, fim: date | None = None,
    agrupamento: Agrupamento = Query(default="dia"),
    db: AsyncSession = Depends(get_async_session)) -> DashboardConteudoRead:
    return await service.obter_dashboard_conteudo(db, id, inicio, fim, agrupamento)