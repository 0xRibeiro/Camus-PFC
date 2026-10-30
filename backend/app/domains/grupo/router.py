from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.domains.grupo import service
from app.domains.grupo.model import Grupo
from app.domains.grupo.schema import ConviteRead, GrupoCreate, GrupoEntrar, GrupoRead
from app.domains.usuario.model import Usuario
from app.domains.usuario.service import get_current_user

router = APIRouter(prefix="/grupos", tags=["grupos"])

# 5 rotas iniciais


# rota 1 = cria os grupos, retornando 201 em caso de sucesso.
@router.post("", response_model=GrupoRead, status_code=status.HTTP_201_CREATED)
async def criar_grupo(data: GrupoCreate, db: AsyncSession = Depends(get_async_session),
    usuario: Usuario = Depends(get_current_user)) -> Grupo:
    return await service.criar_grupo(db, data, usuario)

# rota 2 = lista os grupos do atual usuário, retornando 200.
@router.get("", response_model=list[GrupoRead])
async def listar_grupos(db: AsyncSession = Depends(get_async_session),
    usuario: Usuario = Depends(get_current_user)) -> list[Grupo]:
    return await service.listar_grupos(db, usuario)

# rota 3 = entra no grupo utilizando um convite. retorna 200 também nos sucessos ou 400 quando é convite inválido.
@router.post("/entrar", response_model=GrupoRead)
async def entrar_grupo(
    data: GrupoEntrar, db: AsyncSession = Depends(get_async_session),
    usuario: Usuario = Depends(get_current_user),
) -> Grupo:
    return await service.entrar_grupo(db, data, usuario)

# rota 4 = busca um grupo pelo seu id, retornando ou 200 ou 404 quando não é encontrado.
@router.get("/{grupo_id}", response_model=GrupoRead)
async def buscar_grupo(grupo_id: int, db: AsyncSession = Depends(get_async_session),
    usuario: Usuario = Depends(get_current_user)) -> Grupo:
    return await service.buscar_grupo(db, grupo_id, usuario)

# rota 5 = gera um novo convite para o grupo, retornando 201. por padrão, só o dono pode gerar.
@router.post("/{grupo_id}/convites", response_model=ConviteRead, status_code=status.HTTP_201_CREATED)
async def gerar_convite(grupo_id: int, db: AsyncSession = Depends(get_async_session),
    usuario: Usuario = Depends(get_current_user)) -> ConviteRead:
    return await service.gerar_convite(db, grupo_id, usuario)
