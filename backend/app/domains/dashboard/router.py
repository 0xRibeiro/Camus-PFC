from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.domains.dashboard import service
from app.domains.dashboard.schema import (
    Agrupamento,
    AlunoDetalheRead,
    AlunoQuizRead,
    AlunoTrilhaRead,
    DashboardConteudoRead,
    DashboardRead,
    DashboardTrilhaRead,
    ResumoConteudoRead,
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


# numeros q aparecem do lado de cada quiz na tela de gerenciar a trilha
@trilha_router.get("/trilhas/{id}/resumo-conteudos", response_model=list[ResumoConteudoRead],
    dependencies=[Depends(gerenciar_trilhas), Depends(validar_item(Trilha))])
async def resumir_conteudos(id: int, db: AsyncSession = Depends(get_async_session)) -> list[ResumoConteudoRead]:
    return await service.resumir_conteudos(db, id)


# so trilha de grupo, o dono ve cada membro
@trilha_router.get("/trilhas/{id}/alunos", response_model=list[AlunoTrilhaRead],
    dependencies=[Depends(gerenciar_trilhas), Depends(validar_item(Trilha))])
async def listar_alunos_da_trilha(id: int, db: AsyncSession = Depends(get_async_session)) -> list[AlunoTrilhaRead]:
    return await service.listar_alunos_da_trilha(db, id)


@trilha_router.get("/trilhas/{id}/alunos/{usuario_id}", response_model=AlunoDetalheRead,
    dependencies=[Depends(gerenciar_trilhas), Depends(validar_item(Trilha))])
async def obter_aluno_da_trilha(id: int, usuario_id: int,
    db: AsyncSession = Depends(get_async_session)) -> AlunoDetalheRead:
    return await service.obter_aluno_da_trilha(db, id, usuario_id)


@trilha_router.get("/conteudos/{id}/dashboard", response_model=DashboardConteudoRead,
    dependencies=[Depends(gerenciar_trilhas), Depends(validar_item(Conteudo))])
async def obter_dashboard_conteudo(id: int, inicio: date | None = None, fim: date | None = None,
    agrupamento: Agrupamento = Query(default="dia"),
    db: AsyncSession = Depends(get_async_session)) -> DashboardConteudoRead:
    return await service.obter_dashboard_conteudo(db, id, inicio, fim, agrupamento)


# so quiz de trilha de grupo, o dono ve a nota de cada membro
@trilha_router.get("/conteudos/{id}/alunos", response_model=list[AlunoQuizRead],
    dependencies=[Depends(gerenciar_trilhas), Depends(validar_item(Conteudo))])
async def listar_alunos_do_quiz(id: int, db: AsyncSession = Depends(get_async_session)) -> list[AlunoQuizRead]:
    return await service.listar_alunos_do_quiz(db, id)