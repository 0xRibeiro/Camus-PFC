from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.domains.dispositivo import service
from app.domains.dispositivo.schema import CadastroDispositivo, CredencialDispositivo
from app.domains.usuario.model import RoleUsuario
from app.domains.usuario.service import exige_role

# usado pelo script de gravacao
admin_router = APIRouter(
    prefix="/admin/dispositivos",
    tags=["admin"],
    dependencies=[Depends(exige_role(RoleUsuario.admin))],
)


@admin_router.post("", response_model=CredencialDispositivo, status_code=status.HTTP_201_CREATED)
async def cadastrar_dispositivo(data: CadastroDispositivo, db: AsyncSession = Depends(get_async_session)) -> CredencialDispositivo:
    return await service.cadastrar(db, data)
