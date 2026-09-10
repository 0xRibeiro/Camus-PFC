from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials
from fastcrud.exceptions.http_exceptions import (
    DuplicateValueException,
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.security import (
    bearer_scheme,
    criar_access_token,
    criar_hash,
    criar_refresh_token,
    decodificar_access_token,
    revogar_refresh_token,
    validar_refresh_token,
    verificar_password,
)
from app.domains.usuario.model import RoleUsuario, Usuario
from app.domains.usuario.repository import UsuarioRepository
from app.domains.usuario.schema import (
    TokenPair,
    UsuarioAdminUpdate,
    UsuarioCreate,
    UsuarioStaffCreate,
    UsuarioUpdate,
)

###### cadastro


# auto-cadastro publico. role sempre aluno, o cliente n escolhe
async def criar_aluno(db: AsyncSession, data: UsuarioCreate) -> Usuario:
    repo = UsuarioRepository(db)
    if await repo.buscar_por_username(data.username) is not None:
        raise DuplicateValueException("username já existe")
    if await repo.buscar_por_email(data.email) is not None:
        raise DuplicateValueException("email já existe")

    user = Usuario(
        username=data.username,
        email=data.email,
        hashed_password=criar_hash(data.password),  # nunca guarda senha crua
        role=RoleUsuario.aluno,
    )
    return await repo.salvar(user)


# staff (author/admin) so criado por um admin. mesma logica, role vem do body
async def criar_staff(db: AsyncSession, data: UsuarioStaffCreate) -> Usuario:
    repo = UsuarioRepository(db)
    if await repo.buscar_por_username(data.username) is not None:
        raise DuplicateValueException("username já existe")
    if await repo.buscar_por_email(data.email) is not None:
        raise DuplicateValueException("email já existe")

    user = Usuario(
        username=data.username,
        email=data.email,
        hashed_password=criar_hash(data.password),
        role=data.role,
    )
    return await repo.salvar(user)


###### login / tokens


# mesma msg pros dois erros pra n vazar se o user existe ou n
async def autenticar(db: AsyncSession, email: str, password: str) -> Usuario:
    user = await UsuarioRepository(db).buscar_por_email(email)
    if user is None or not verificar_password(password, user.hashed_password):
        raise UnauthorizedException("credenciais inválidas")
    return user


# o "subject" do token é sempre o id do usuario
async def emitir_tokens(user: Usuario) -> TokenPair:
    return TokenPair(
        access_token=criar_access_token(str(user.id)),
        refresh_token=await criar_refresh_token(str(user.id)),
    )


# rotacao: valida o refresh no redis, revoga ele e emite um par novo.
# reusar o refresh antigo depois disso da 401 (detecta roubo de token)
async def renovar_tokens(db: AsyncSession, refresh_token: str) -> TokenPair:
    subject = await validar_refresh_token(refresh_token)
    if subject is None:
        raise UnauthorizedException("refresh token inválido")

    user = await UsuarioRepository(db).buscar(int(subject))
    if user is None:
        raise UnauthorizedException("refresh token inválido")

    await revogar_refresh_token(refresh_token)
    return await emitir_tokens(user)


async def logout(refresh_token: str) -> None:
    await revogar_refresh_token(refresh_token)


###### quem ta logado / RBAC


# dependency: le o token do header, devolve o usuario dono dele
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_async_session),
) -> Usuario:
    subject = decodificar_access_token(credentials.credentials)
    if subject is None:
        raise UnauthorizedException("credenciais inválidas")

    user = await UsuarioRepository(db).buscar(int(subject))
    if user is None or not user.is_active:
        raise UnauthorizedException("credenciais inválidas")
    return user


# fabrica de dependency para barrar acesso
def exige_role(*roles: RoleUsuario):
    async def dep(user: Usuario = Depends(get_current_user)) -> Usuario:
        if user.role not in roles:
            raise ForbiddenException("acesso negado")
        return user

    return dep


async def buscar_usuario(db: AsyncSession, user_id: int) -> Usuario:
    user = await UsuarioRepository(db).buscar(user_id)
    if user is None:
        raise NotFoundException("usuário não encontrado")
    return user


async def listar_usuarios(db: AsyncSession) -> list[Usuario]:
    return await UsuarioRepository(db).listar()


###### edicao


# edicao do proprio usuario (/usuarios/me). n mexe em role nem is_active
async def atualizar_usuario(
    db: AsyncSession, user: Usuario, data: UsuarioUpdate
) -> Usuario:
    if data.username is not None:
        user.username = data.username
    if data.email is not None:
        user.email = data.email
    if data.password is not None:
        user.hashed_password = criar_hash(data.password)
    return await UsuarioRepository(db).salvar(user)


# edicao feita pelo admin: pode mudar role e is_active tbm
async def atualizar_usuario_admin(
    db: AsyncSession, user_id: int, data: UsuarioAdminUpdate
) -> Usuario:
    user = await buscar_usuario(db, user_id)
    if data.username is not None:
        user.username = data.username
    if data.email is not None:
        user.email = data.email
    if data.password is not None:
        user.hashed_password = criar_hash(data.password)
    if data.role is not None:
        user.role = data.role
    if data.is_active is not None:
        user.is_active = data.is_active
    return await UsuarioRepository(db).salvar(user)


async def deletar_usuario(db: AsyncSession, user: Usuario) -> None:
    await UsuarioRepository(db).deletar(user)
