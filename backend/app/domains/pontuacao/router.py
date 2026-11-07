from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.domains.pontuacao import service
from app.domains.pontuacao.schema import LancamentoRead, XpRead
from app.domains.usuario.model import Usuario
from app.domains.usuario.service import get_current_user

router = APIRouter(prefix="/pontuacao", tags=["pontuacao"])


@router.get("/xp", response_model=XpRead)
async def meu_xp(
    db: AsyncSession = Depends(get_async_session),
    usuario: Usuario = Depends(get_current_user),
) -> XpRead:
    return await service.meu_xp(db, usuario)


@router.get("/extrato", response_model=list[LancamentoRead])
async def meu_extrato(
    db: AsyncSession = Depends(get_async_session),
    usuario: Usuario = Depends(get_current_user),
) -> list[LancamentoRead]:
    return await service.meu_extrato(db, usuario)
