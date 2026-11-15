from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.domains.grupo.model import Grupo
from app.domains.grupo.schema import GrupoRead
from app.domains.moderacao import service
from app.domains.moderacao.schema import MotivoCreate, SuspensaoCreate
from app.domains.usuario.model import RoleUsuario
from app.domains.usuario.service import exige_role

# rotas do admin pra moderar grupos. só o admin entra, e toda ação manda um aviso pro dono.
router = APIRouter(
    prefix="/admin/grupos",
    tags=["admin"],
    dependencies=[Depends(exige_role(RoleUsuario.admin))],
)


# suspende o grupo por 14 ou 30 dias e devolve o grupo com a data do fim.
@router.post("/{grupo_id}/suspensao", response_model=GrupoRead)
async def suspender_grupo(
    grupo_id: int,
    data: SuspensaoCreate,
    db: AsyncSession = Depends(get_async_session),
) -> Grupo:
    return await service.suspender_grupo(db, grupo_id, data)


# exclui o grupo com tudo que pertence a ele, devolvendo 204.
@router.delete("/{grupo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def excluir_grupo(
    grupo_id: int,
    data: MotivoCreate,
    db: AsyncSession = Depends(get_async_session),
) -> None:
    await service.excluir_grupo(db, grupo_id, data)


# apaga só um conteúdo do grupo, devolvendo 204.
@router.delete("/{grupo_id}/conteudos/{conteudo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def excluir_conteudo(
    grupo_id: int,
    conteudo_id: int,
    data: MotivoCreate,
    db: AsyncSession = Depends(get_async_session),
) -> None:
    await service.excluir_conteudo(db, grupo_id, conteudo_id, data)