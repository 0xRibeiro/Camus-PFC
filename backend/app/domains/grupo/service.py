import secrets
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from fastapi import Depends, Request
from fastcrud.exceptions.http_exceptions import (
    DuplicateValueException,
    ForbiddenException,
    NotFoundException,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.redis import redis_client
from app.domains.grupo.model import Grupo
from app.domains.grupo.repository import GrupoRepository
from app.domains.grupo.schema import (
    ConviteRead,
    GrupoCreate,
    GrupoEntrar,
    MembroGrupoRead,
)
from app.domains.usuario.model import RoleUsuario, Usuario
from app.domains.usuario.service import get_current_user

# está com esse tempo por enquanto.
CONVITE_VALIDADE_SEGUNDOS = 900

# a data do fim da suspensão é mostrada pro usuário no horário de Brasília
FUSO = ZoneInfo("America/Sao_Paulo")


# o grupo fica bloqueado se foi inabilitado ou se a suspensão ainda está valendo.
# ela acaba sozinha, basta comparar a data de fim com a hora de agora.
def grupo_suspenso(grupo: Grupo) -> bool:
    if grupo.inabilitado:
        return True

    return grupo.suspenso_ate is not None and grupo.suspenso_ate > datetime.now(UTC)


def mensagem_suspensao(grupo: Grupo) -> str:
    if grupo.inabilitado:
        return "Este grupo foi inabilitado pela administração."

    fim = grupo.suspenso_ate.astimezone(FUSO)
    return f"Este grupo está suspenso até {fim:%d/%m/%Y %H:%M}."


async def criar_grupo(db: AsyncSession, data: GrupoCreate, usuario: Usuario) -> Grupo:
    grupo = Grupo(nome=data.nome, id_dono=usuario.id)
    return await GrupoRepository(db).criar(grupo)


async def listar_grupos(db: AsyncSession, usuario: Usuario) -> list[Grupo]:
    return await GrupoRepository(db).listar_do_usuario(usuario.id)


async def buscar_grupo(db: AsyncSession, grupo_id: int, usuario: Usuario) -> Grupo:
    repo = GrupoRepository(db)
    grupo = await repo.buscar(grupo_id)

    if grupo is None:
        raise NotFoundException("Grupo não encontrado. Verifique se foi digitado corretamente")

    # o admin abre qualquer grupo pra poder moderar. que ele só lê e nunca altera
    # é checado lá no grupo_membro.
    if usuario.role == RoleUsuario.admin:
        return grupo

    participacao = await repo.buscar_participacao(grupo.id, usuario.id)

    if participacao is None:
        raise ForbiddenException("Você não participa deste grupo.")

    return grupo


# retorna o grupo e guarda o id dele na sessão.
async def grupo_membro(
    request: Request,
    grupo_id: int,
    db: AsyncSession = Depends(get_async_session),
    usuario: Usuario = Depends(get_current_user),
) -> Grupo:
    grupo = await buscar_grupo(db, grupo_id, usuario)

    # nos casos abaixo, só requisição de leitura (GET) passa
    somente_leitura = request.method in ("GET", "HEAD")

    if usuario.role == RoleUsuario.admin and not somente_leitura:
        raise ForbiddenException("O admin só pode visualizar o conteúdo do grupo.")

    # com o grupo suspenso, o dono ainda consegue ver mas não muda nada, e o membro
    # perde o acesso. a suspensão não vale pro admin.
    if usuario.role != RoleUsuario.admin and grupo_suspenso(grupo):
        if grupo.id_dono != usuario.id or not somente_leitura:
            raise ForbiddenException(mensagem_suspensao(grupo))

    # esse escopo vale só durante a sessão da requisição.
    db.info["grupo_id"] = grupo.id
    return grupo

# confere se o usuário é o dono do grupo e levanta erro se não for. devolve o id do grupo.
# o admin passa só pra ler, já que o grupo_membro barra qualquer escrita dele.
async def grupo_dono(grupo: Grupo = Depends(grupo_membro), usuario: Usuario = Depends(get_current_user)) -> int:
    if grupo.id_dono != usuario.id and usuario.role != RoleUsuario.admin:
        raise ForbiddenException("Apenas o dono pode gerenciar as trilhas do grupo.")

    return grupo.id


async def gerar_convite(db: AsyncSession, grupo_id: int, usuario: Usuario) -> ConviteRead:
    grupo = await buscar_grupo(db, grupo_id, usuario)

    # achei interessante colocar que apenas o dono pode gerar convites, assim o professor
    # pode controlar melhor quem entra e quem sai. podemos mudar para o dono permitir que todos compartilhem
    # depois.
    if grupo.id_dono != usuario.id:
        raise ForbiddenException("Apenas o dono pode gerar convites")
    
    if grupo_suspenso(grupo):
        raise ForbiddenException(mensagem_suspensao(grupo))

    while True:
        convite = secrets.token_urlsafe(9)

        # evita sobrescrever outro convite que ainda esteja válido
        criado = await redis_client.set(f"grupo:convite:{convite}", str(grupo.id), ex=CONVITE_VALIDADE_SEGUNDOS, nx=True,)

        if criado:
            return ConviteRead(convite=convite, expira_em_segundos=CONVITE_VALIDADE_SEGUNDOS)


# as checagens desse metodo garantem a validade do convite e a não participação do usuário
# tentando entrar. com sorte esses bloqueios evitam os principais erros
async def entrar_grupo(db: AsyncSession, data: GrupoEntrar, usuario: Usuario) -> Grupo:
    grupo_id = await redis_client.get(f"grupo:convite:{data.convite}")

    if grupo_id is None:
        raise NotFoundException("Convite inválido ou expirou")

    repo = GrupoRepository(db)
    grupo = await repo.buscar(int(grupo_id))

    if grupo is None:
        raise NotFoundException("Grupo não encontrado")

    if grupo_suspenso(grupo):
        raise ForbiddenException("Não é possível entrar: este grupo está suspenso.")

    participacao = await repo.buscar_participacao(grupo.id, usuario.id)

    if participacao is not None:
        raise DuplicateValueException("Você já participa desse grupo")

    await repo.adicionar_participante(grupo.id, usuario.id)
    return grupo


async def listar_membros(db: AsyncSession, grupo_id: int, usuario: Usuario) -> list[MembroGrupoRead]:
    # verifica a participação antes de permitir consultar os membros
    grupo = await buscar_grupo(db, grupo_id, usuario)
    membros = await GrupoRepository(db).listar_membros(grupo.id)

    return [
        MembroGrupoRead(id=membro.id, username=membro.username, papel="dono" if membro.id == grupo.id_dono else "membro")
        for membro in membros
    ]