import secrets

from fastcrud.exceptions.http_exceptions import (
    DuplicateValueException,
    ForbiddenException,
    NotFoundException,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis import redis_client
from app.domains.grupo.model import Grupo
from app.domains.grupo.repository import GrupoRepository
from app.domains.grupo.schema import (
    ConviteRead,
    GrupoCreate,
    GrupoEntrar,
    MembroGrupoRead,
)
from app.domains.usuario.model import Usuario

# está com esse tempo por enquanto.
CONVITE_VALIDADE_SEGUNDOS = 900


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

    participacao = await repo.buscar_participacao(grupo.id, usuario.id)

    if participacao is None:
        raise ForbiddenException("Você não participa deste grupo.")

    return grupo


async def gerar_convite(db: AsyncSession, grupo_id: int, usuario: Usuario) -> ConviteRead:
    grupo = await buscar_grupo(db, grupo_id, usuario)

    # achei interessante colocar que apenas o dono pode gerar convites, assim o professor
    # pode controlar melhor quem entra e quem sai. podemos mudar para o dono permitir que todos compartilhem
    # depois.
    if grupo.id_dono != usuario.id:
        raise ForbiddenException("Apenas o dono pode gerar convites")

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