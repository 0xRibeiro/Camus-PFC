from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.domains.aviso import service
from app.domains.aviso.model import Aviso
from app.domains.aviso.schema import AvisoRead
from app.domains.usuario.model import Usuario
from app.domains.usuario.service import get_current_user

router = APIRouter(prefix="/avisos", tags=["avisos"])


# devolve os avisos do usuário logado que ainda não foram dispensados, com 200.
@router.get("", response_model=list[AvisoRead])
async def listar_avisos(
    db: AsyncSession = Depends(get_async_session),
    usuario: Usuario = Depends(get_current_user),
) -> list[Aviso]:
    return await service.listar_avisos(db, usuario)


# marca o aviso como lido (é o "entendi" do front), com 200 ou 404.
@router.patch("/{aviso_id}/lido", response_model=AvisoRead)
async def marcar_como_lido(
    aviso_id: int,
    db: AsyncSession = Depends(get_async_session),
    usuario: Usuario = Depends(get_current_user),
) -> Aviso:
    return await service.marcar_como_lido(db, aviso_id, usuario)