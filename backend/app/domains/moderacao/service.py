from datetime import UTC, datetime, timedelta

from fastcrud.exceptions.http_exceptions import NotFoundException
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.aviso.model import Aviso
from app.domains.grupo.model import Grupo
from app.domains.grupo.service import FUSO
from app.domains.moderacao.repository import ModeracaoRepository
from app.domains.moderacao.schema import MotivoCreate, SuspensaoCreate


async def _buscar_grupo(repo: ModeracaoRepository, grupo_id: int) -> Grupo:
    grupo = await repo.buscar_grupo(grupo_id)

    if grupo is None:
        raise NotFoundException("Grupo não encontrado")

    return grupo


# suspende o grupo por 14 ou 30 dias e manda o aviso pro dono. se o grupo já estava
# suspenso, o prazo novo substitui o antigo.
async def suspender_grupo(db: AsyncSession, grupo_id: int, data: SuspensaoCreate) -> Grupo:
    repo = ModeracaoRepository(db)
    grupo = await _buscar_grupo(repo, grupo_id)

    ate = datetime.now(UTC) + timedelta(days=data.dias)
    fim = ate.astimezone(FUSO)

    aviso = Aviso(
        id_usuario=grupo.id_dono,
        mensagem=f'Seu grupo "{grupo.nome}" foi suspenso por {data.dias} dias, até {fim:%d/%m/%Y}. Motivo: {data.motivo}',
    )
    return await repo.suspender(grupo, ate, aviso)


# exclui o grupo e manda o aviso pro dono. as trilhas, as participações e as denúncias
# do grupo são apagadas junto.
async def excluir_grupo(db: AsyncSession, grupo_id: int, data: MotivoCreate) -> None:
    repo = ModeracaoRepository(db)
    grupo = await _buscar_grupo(repo, grupo_id)

    aviso = Aviso(
        id_usuario=grupo.id_dono,
        mensagem=f'Seu grupo "{grupo.nome}" foi excluído pela administração. Motivo: {data.motivo}',
    )
    await repo.excluir_grupo(grupo, aviso)


# apaga um conteúdo do grupo e manda o aviso pro dono
async def excluir_conteudo(db: AsyncSession, grupo_id: int, conteudo_id: int, data: MotivoCreate) -> None:
    repo = ModeracaoRepository(db)
    grupo = await _buscar_grupo(repo, grupo_id)

    conteudo = await repo.buscar_conteudo_do_grupo(conteudo_id, grupo.id)

    if conteudo is None:
        raise NotFoundException("Conteúdo não encontrado nesse grupo")

    aviso = Aviso(
        id_usuario=grupo.id_dono,
        mensagem=f'O conteúdo "{conteudo.titulo}" do seu grupo "{grupo.nome}" foi removido pela administração. Motivo: {data.motivo}',
    )
    await repo.excluir_conteudo(conteudo, aviso)