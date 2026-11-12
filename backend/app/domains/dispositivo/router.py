from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.domains.dispositivo import service
from app.domains.dispositivo.model import Dispositivo
from app.domains.dispositivo.schema import DispositivoRead, VincularDispositivo
from app.domains.usuario.model import Usuario
from app.domains.usuario.service import get_current_user

router = APIRouter(prefix="/dispositivos", tags=["dispositivos"])


@router.post("/vincular", response_model=DispositivoRead, status_code=status.HTTP_201_CREATED)
async def vincular(data: VincularDispositivo, db: AsyncSession = Depends(get_async_session),
    usuario: Usuario = Depends(get_current_user)) -> Dispositivo:
    return await service.vincular(db, data, usuario)
