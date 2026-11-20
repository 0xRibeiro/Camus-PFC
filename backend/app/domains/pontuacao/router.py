from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.domains.pontuacao import service
from app.domains.pontuacao.schema import LancamentoRead, RankingItemRead, XpDiaRead, XpRead
from app.domains.usuario.model import Usuario
from app.domains.usuario.service import get_current_user

router = APIRouter(prefix="/pontuacao", tags=["pontuacao"])


@router.get("/xp", response_model=XpRead)
async def meu_xp(
    db: AsyncSession = Depends(get_async_session),
    usuario: Usuario = Depends(get_current_user),
) -> XpRead:
    return await service.meu_xp(db, usuario)


@router.get("/xp/dias", response_model=list[XpDiaRead])
async def meu_xp_por_dia(
    dias: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_async_session),
    usuario: Usuario = Depends(get_current_user),
) -> list[XpDiaRead]:
    return await service.meu_xp_por_dia(db, usuario, dias)


@router.get("/ranking", response_model=list[RankingItemRead])
async def ranking(
    db: AsyncSession = Depends(get_async_session),
    usuario: Usuario = Depends(get_current_user),
) -> list[RankingItemRead]:
    return await service.ranking(db)


@router.get("/extrato", response_model=list[LancamentoRead])
async def meu_extrato(
    db: AsyncSession = Depends(get_async_session),
    usuario: Usuario = Depends(get_current_user),
) -> list[LancamentoRead]:
    return await service.meu_extrato(db, usuario)
