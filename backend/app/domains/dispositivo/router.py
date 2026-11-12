from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.domains.dispositivo import service
from app.domains.dispositivo.model import Dispositivo
from app.domains.dispositivo.schema import (
    DispositivoRead,
    UsuarioVinculadoRead,
    VincularDispositivo,
)
from app.domains.usuario.model import Usuario
from app.domains.usuario.service import get_current_user

router = APIRouter(prefix="/dispositivos", tags=["dispositivos"])


@router.get("", response_model=list[DispositivoRead])
async def listar_dispositivos(db: AsyncSession = Depends(get_async_session),
    usuario: Usuario = Depends(get_current_user)) -> list[Dispositivo]:
    return await service.listar_dispositivos(db, usuario)


@router.post("/vincular", response_model=DispositivoRead, status_code=status.HTTP_201_CREATED)
async def vincular(data: VincularDispositivo, db: AsyncSession = Depends(get_async_session),
    usuario: Usuario = Depends(get_current_user)) -> Dispositivo:
    return await service.vincular(db, data, usuario)


@router.get("/{id_dispositivo}/usuarios", response_model=list[UsuarioVinculadoRead])
async def listar_usuarios(id_dispositivo: int, db: AsyncSession = Depends(get_async_session),
    usuario: Usuario = Depends(get_current_user)) -> list[UsuarioVinculadoRead]:
    return await service.listar_usuarios(db, id_dispositivo, usuario)


@router.delete("/{id_dispositivo}", status_code=status.HTTP_204_NO_CONTENT)
async def remover_da_conta(id_dispositivo: int, db: AsyncSession = Depends(get_async_session),
    usuario: Usuario = Depends(get_current_user)) -> None:
    await service.remover_da_conta(db, id_dispositivo, usuario)
