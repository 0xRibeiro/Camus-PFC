from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.domains.denuncia import service
from app.domains.denuncia.model import Denuncia
from app.domains.denuncia.schema import (
    DenunciaAdminRead,
    DenunciaCreate,
    DenunciaRead,
    DenunciaUpdate,
    StatusDenuncia,
)
from app.domains.grupo.model import Grupo
from app.domains.grupo.service import grupo_membro
from app.domains.usuario.model import RoleUsuario, Usuario
from app.domains.usuario.service import exige_role, get_current_user

# quem denuncia é membro do grupo; o dono fica de fora
router = APIRouter(prefix="/grupos/{grupo_id}/denuncias", tags=["denuncias"])


# registra a denúncia e devolve 201. se não mandar id_conteudo, o alvo é o grupo.
@router.post("", response_model=DenunciaRead, status_code=status.HTTP_201_CREATED)
async def denunciar(
    data: DenunciaCreate,
    grupo: Grupo = Depends(grupo_membro),
    db: AsyncSession = Depends(get_async_session),
    usuario: Usuario = Depends(get_current_user),
) -> Denuncia:
    return await service.criar_denuncia(db, grupo, data, usuario)


### admin (quem analisa as denúncias)

# com dependencies=[] no router, todas as rotas daqui já exigem admin
admin_router = APIRouter(
    prefix="/admin/denuncias",
    tags=["admin"],
    dependencies=[Depends(exige_role(RoleUsuario.admin))],
)


# lista com as mais novas primeiro. dá pra filtrar com ?status=pendente.
@admin_router.get("", response_model=list[DenunciaAdminRead])
async def listar_denuncias(
    status: StatusDenuncia | None = None,
    db: AsyncSession = Depends(get_async_session),
) -> list[DenunciaAdminRead]:
    return await service.listar_denuncias(db, status)


# fecha a denúncia como resolvida ou rejeitada
@admin_router.patch("/{denuncia_id}", response_model=DenunciaRead)
async def resolver_denuncia(
    denuncia_id: int,
    data: DenunciaUpdate,
    db: AsyncSession = Depends(get_async_session),
) -> Denuncia:
    return await service.resolver_denuncia(db, denuncia_id, data)