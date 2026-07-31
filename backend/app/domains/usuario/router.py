from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.security import criar_access_token
from app.domains.usuario.model import Usuario
from app.domains.usuario.schema import UsuarioRead, UsuarioCreate, UsuarioUpdate
from app.domains.usuario.service import criar_usuario, autenticar, current_active_user, atualizar_usuario, deletar_usuario, buscar_usuario, verificar_permissao

router = APIRouter()


### rotas auth

@router.post(
    "/auth/register",
    response_model=UsuarioRead,
    status_code=status.HTTP_201_CREATED,
    tags=["auth"],
)
async def register(
    data: UsuarioCreate,
    db: AsyncSession = Depends(get_async_session),
) -> Usuario:
    return await criar_usuario(db, data)


@router.post(
    "/auth/login",
    tags=["auth"],
)
async def login(
    credentials: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_session),
) -> dict:
    user = await autenticar(db, credentials.username, credentials.password)
    token = criar_access_token(str(user.id))
    return {"access_token": token, "token_type": "bearer"}


### rotas usuario

# rota /me: retorna o usuário logado, atualiza ou deleta ele mesmo.
@router.get(
    "/usuarios/me",
    response_model=UsuarioRead,
    tags=["usuarios"],
)
async def read_me(user: Usuario = Depends(current_active_user)) -> Usuario:
    return user


@router.patch(
    "/usuarios/me",
    response_model=UsuarioRead,
    tags=["usuarios"],
)
async def update_me(
    data: UsuarioUpdate,
    user: Usuario = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session),
) -> Usuario:
    return await atualizar_usuario(db, user, data)


@router.delete(
    "/usuarios/me",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["usuarios"],
)
async def delete_me(
    user: Usuario = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session),
) -> None:
    await deletar_usuario(db, user)

