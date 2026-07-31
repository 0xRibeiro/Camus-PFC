from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.exceptions import AcessoNegadoError, ConflitoError, NaoAutorizadoError, NaoEncontradoError
from app.core.security import decodificar_access_token, criar_hash, oauth2_scheme, verificar_password
from app.domains.usuario.model import Usuario
from app.domains.usuario.repository import UsuarioRepository
from app.domains.usuario.schema import UsuarioCreate, UsuarioUpdate


# Cadastra um usuário novo, com a senha já em hash.
async def criar_usuario(db: AsyncSession, data: UsuarioCreate) -> Usuario:
    repo = UsuarioRepository(db)
    if await repo.buscar_por_username(data.username) is not None:
        raise ConflitoError("username já existe")

    return await repo.criar(
        username=data.username,
        email=data.email,
        hashed_password=criar_hash(data.password),
        roles=[],
    )


# Confere username + senha, devolve o usuário
async def autenticar(db: AsyncSession, username: str, password: str) -> Usuario:
    repo = UsuarioRepository(db)
    user = await repo.buscar_por_username(username)

    if user is None:
        raise NaoAutorizadoError("credenciais inválidas")

    if not verificar_password(password, user.hashed_password):
        raise NaoAutorizadoError("credenciais inválidas")

    return user


# Busca usuário por id
async def buscar_usuario(db: AsyncSession, user_id: int) -> Usuario:
    user = await UsuarioRepository(db).buscar(user_id)
    if user is None:
        raise NaoEncontradoError("usuário não encontrado")
    return user


# Aplica mudanças parciais num usuário que já existe.
async def atualizar_usuario(
    db: AsyncSession,
    user: Usuario, 
    data: UsuarioUpdate
) -> Usuario:
    update_data = data.model_dump(exclude_unset=True)

    password = update_data.pop("password", None)
    if password:
        update_data["hashed_password"] = criar_hash(password)

    return await UsuarioRepository(db).atualizar(user, update_data)


# Remove um usuário do banco.
async def deletar_usuario(db: AsyncSession, user: Usuario) -> None:
    await UsuarioRepository(db).deletar(user)


# Descobre quem é o usuário dono do token da requisição.
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_session),
) -> Usuario:
    user_id = decodificar_access_token(token)
    if user_id is None:
        raise NaoAutorizadoError("credenciais inválidas")

    user = await UsuarioRepository(db).buscar(int(user_id))
    if user is None:
        raise NaoAutorizadoError("credenciais inválidas")

    return user


# Retorna o usuário logado, ou erro se ele estiver inativo.
def current_active_user(user: Usuario = Depends(get_current_user)) -> Usuario:
    if not user.is_active:
        raise NaoAutorizadoError("usuário inativo")
    return user


