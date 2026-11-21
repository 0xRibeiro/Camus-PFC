import secrets
from datetime import datetime, timezone

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials
from fastcrud.exceptions.http_exceptions import (
    DuplicateValueException,
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_async_session
from app.core.email import enviar_email
from app.core.redis import redis_client
from app.core.security import (
    bearer_scheme,
    criar_access_token,
    criar_codigo_reset,
    criar_hash,
    criar_refresh_token,
    decodificar_access_token,
    revogar_codigo_reset,
    revogar_refresh_token,
    usuario_atual_id,
    validar_codigo_reset,
    validar_refresh_token,
    verificar_password,
)
from app.domains.auditoria.model import AcaoAuditoria, LogAuditoria
from app.domains.auditoria.repository import AuditoriaRepository
from app.domains.conquistas import service as conquistas_service
from app.domains.conquistas.model import Conquista
from app.domains.conquistas.repository import ConquistaRepository
from app.domains.conquistas.schema import ConquistaUsuarioRead
from app.domains.documento_legal import service as documento_legal_service
from app.domains.documento_legal.model import AceiteDocumentoLegal
from app.domains.usuario.avatares import (
    AVATARES,
    AVATARES_BLOQUEADOS,
    sortear_avatar,
    sortear_cor_fundo,
)
from app.domains.usuario.model import RoleUsuario, Usuario
from app.domains.usuario.repository import UsuarioRepository
from app.domains.usuario.schema import (
    AvatarRead,
    EmailReveladoRead,
    TokenPair,
    UsuarioAdminRead,
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
        hashed_password=criar_hash(data.password),
        role=RoleUsuario.aluno,
        avatar=sortear_avatar(),
        cor_fundo=sortear_cor_fundo(),
    )

    # aceita as versoes atuais
    for documento in await documento_legal_service.listar_atuais(db):
        user.aceites_documentos.append(AceiteDocumentoLegal(documento_id=documento.id))

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
        avatar=sortear_avatar(),
        cor_fundo=sortear_cor_fundo(),
    )
    return await repo.salvar(user)


###### login / tokens


# mesma msg pros dois erros pra n vazar se o user existe ou n
async def autenticar(db: AsyncSession, email: str, password: str) -> Usuario:
    user = await UsuarioRepository(db).buscar_por_email(email)
    if user is None or not verificar_password(password, user.hashed_password):
        raise UnauthorizedException("credenciais inválidas")
    await registrar_acesso(db, user)
    return user


# login e renovacao do token contam como acesso. conta desativada n conta
async def registrar_acesso(db: AsyncSession, user: Usuario) -> None:
    if not user.is_active:
        return
    await UsuarioRepository(db).registrar_acesso(user.id, datetime.now(timezone.utc))


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
    await registrar_acesso(db, user)
    return await emitir_tokens(user)


async def logout(refresh_token: str) -> None:
    await revogar_refresh_token(refresh_token)


###### recuperacao de senha


# nao revela se o email existe ou nao, so manda o codigo se existir
async def solicitar_reset_senha(db: AsyncSession, email: str) -> None:
    user = await UsuarioRepository(db).buscar_por_email(email)
    if user is None:
        return

    codigo = await criar_codigo_reset(email)
    await enviar_email(
        email,
        "Recuperação de senha - Camus",
        f"Seu código de recuperação é {codigo}. Ele expira em 15 minutos.",
    )


async def redefinir_senha(db: AsyncSession, email: str, codigo: str, nova_senha: str) -> None:
    if not await validar_codigo_reset(email, codigo):
        raise UnauthorizedException("código inválido ou expirado")

    user = await UsuarioRepository(db).buscar_por_email(email)
    if user is None:
        raise UnauthorizedException("código inválido ou expirado")

    user.hashed_password = criar_hash(nova_senha)
    await UsuarioRepository(db).salvar(user)
    await revogar_codigo_reset(email)


###### quem ta logado / RBAC


# dependency: le o token do header, devolve o usuario dono dele alem de marcar quem esta logado.
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_async_session),
) -> Usuario:
    subject = decodificar_access_token(credentials.credentials)
    if subject is None:
        raise UnauthorizedException("credenciais inválidas")

    # seta antes de qualquer query nessa sessao, pq a primeira query ja
    # comeca a transacao e dispara o after_begin que le essa contextvar
    usuario_atual_id.set(int(subject))

    user = await UsuarioRepository(db).buscar(int(subject))
    if user is None or not user.is_active:
        raise UnauthorizedException("credenciais inválidas")

    # marca presenca: chave some sozinha se o usuario ficar sem
    # fazer request pelo tempo de vida do access token
    await redis_client.set(f"online:{user.id}", "true", ex=settings.jwt_lifetime_seconds)
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


async def listar_usuarios(db: AsyncSession, busca: str | None = None) -> list[UsuarioAdminRead]:
    if busca is not None:
        busca = busca.strip()
    repo = UsuarioRepository(db)
    usuarios = await repo.listar(busca)

    ids = []
    for usuario in usuarios:
        ids.append(usuario.id)
    acessos = await repo.listar_acessos(ids)

    # o ultimo acesso fica em outra tabela, junta aqui
    lista = []
    for usuario in usuarios:
        item = UsuarioAdminRead.model_validate(usuario)
        item.ultimo_acesso_em = acessos.get(usuario.id)
        lista.append(item)
    return lista


# cada clique no olhinho vira uma linha na auditoria: quem viu, de quem e quando
async def revelar_email(db: AsyncSession, admin: Usuario, user_id: int) -> EmailReveladoRead:
    user = await buscar_usuario(db, user_id)
    email = user.email

    await AuditoriaRepository(db).registrar(LogAuditoria(
        usuario_id=admin.id,
        acao=AcaoAuditoria.view,
        entidade="usuarios",
        entidade_id=user.id,
        alteracoes={"campo": "email"},
    ))
    return EmailReveladoRead(email=email)


# varre as chaves online:<id> no redis sem travar ele (scan_iter em vez de keys)
async def ids_usuarios_online() -> list[int]:
    ids = []
    async for chave in redis_client.scan_iter(match="online:*"):
        id_usuario = chave.split(":")[1]
        ids.append(int(id_usuario))

    return ids


async def listar_usuarios_online(db: AsyncSession) -> list[Usuario]:
    ids = await ids_usuarios_online()
    return await UsuarioRepository(db).buscar_varios(ids)


async def listar_conquistas_usuario(db: AsyncSession, user_id: int) -> list[ConquistaUsuarioRead]:
    linhas = await UsuarioRepository(db).listar_conquistas(user_id)
    conquistas = []
    for conquista, desbloqueada_em in linhas:
        item = ConquistaUsuarioRead.model_validate(conquista)
        item.desbloqueada_em = desbloqueada_em
        conquistas.append(item)
    return conquistas

# metodo faz algumas checagens para não dar conquistas não existentes
# ou duplicadas
async def conceder_conquista(db: AsyncSession, user_id: int, conquista_id: int) -> Conquista | None:
    return await conquistas_service.conceder_conquista(db, user_id, conquista_id)


###### edicao


# monta a lista de avatares mostrando quais o usuário já pode usar.
# os bloqueados levam junto a conquista que libera cada um
async def listar_avatares_usuario(db: AsyncSession, user: Usuario) -> list[AvatarRead]:
    repo = ConquistaRepository(db)
    avatares = [AvatarRead(chave=chave, liberado=True) for chave in AVATARES]

    for chave, conquista_id in AVATARES_BLOQUEADOS.items():
        conquista = await repo.buscar(conquista_id)
        avatares.append(
            AvatarRead(
                chave=chave,
                # se já está usando esse avatar, ele continua liberado
                liberado=user.avatar == chave or await repo.usuario_tem(user.id, conquista_id),
                conquista_id=conquista_id,
                conquista=conquista.titulo if conquista else None,
            )
        )

    return avatares


# edicao do proprio usuario (/usuarios/me). n mexe em role nem is_active
async def atualizar_usuario(
    db: AsyncSession, user: Usuario, data: UsuarioUpdate
) -> Usuario:
    repo = UsuarioRepository(db)
    if data.username is not None and data.username != user.username:
        if await repo.buscar_por_username(data.username) is not None:
            raise DuplicateValueException("username já existe")
        user.username = data.username
    if data.email is not None:
        user.email = data.email
    if data.password is not None:
        user.hashed_password = criar_hash(data.password)
    if data.avatar is not None:
        # esses avatares só saem se o usuário já tiver a conquista deles.
        # quem já está usando um pode mandar o mesmo de novo, sem erro
        conquista_id = AVATARES_BLOQUEADOS.get(data.avatar)
        if (
            conquista_id is not None
            and data.avatar != user.avatar
            and not await ConquistaRepository(db).usuario_tem(user.id, conquista_id)
        ):
            raise ForbiddenException("Avatar bloqueado: ganhe a conquista para liberar")
        user.avatar = data.avatar
    if data.cor_fundo is not None:
        user.cor_fundo = data.cor_fundo
    return await UsuarioRepository(db).salvar(user)


# edicao feita pelo admin: pode mudar is_active tbm, o papel nunca muda
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
    if data.is_active is not None:
        user.is_active = data.is_active
    return await UsuarioRepository(db).salvar(user)


# pelo perfil so o aluno exclui a propria conta. author e admin passam pelo admin
async def deletar_propria_conta(db: AsyncSession, user: Usuario) -> None:
    if user.role != RoleUsuario.aluno:
        raise ForbiddenException("Só alunos podem excluir a própria conta")
    await deletar_usuario(db, user)


# soft delete: em vez de apagar a linha, sobrescreve os dados pessoais e marca
# deletado_em. a conta fica inutilizavel (senha trocada por uma aleatoria que
# ninguem sabe, is_active false) mas o registro continua no banco. o trigger
# de auditoria pega isso como UPDATE e guarda o antes/depois no logs_auditoria,
# entao fica provado que a conta existiu e quando foi encerrada
async def deletar_usuario(db: AsyncSession, user: Usuario) -> None:
    if user.role == RoleUsuario.admin:
        raise ForbiddenException("contas de administrador não podem ser excluídas")
    if user.deletado_em is not None:
        return  # ja tava deletado, n faz nada

    user.username = f"usuario-excluido-{user.id}"
    user.username = f"usuario-excluido-{user.id}"
    user.email = f"usuario-excluido-{user.id}@removido.camus"
    user.hashed_password = criar_hash(secrets.token_urlsafe(32))
    user.is_active = False
    user.deletado_em = datetime.now(timezone.utc)

    await UsuarioRepository(db).salvar(user)