from fastcrud.exceptions.http_exceptions import NotFoundException
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.aquario.model import Aquario
from app.domains.aquario.repository import AquarioRepository
from app.domains.peixe.model import Peixe
from app.domains.peixe.schema import PeixeCreate


async def buscar_aquario_do_usuario(repo: AquarioRepository, aquario_id: int, usuario_id: int) -> Aquario:
    aquario = await repo.buscar_do_usuario(aquario_id, usuario_id)
    if aquario is None:
        raise NotFoundException("Aquário não encontrado")

    return aquario


async def listar_peixes(db: AsyncSession, aquario_id: int, usuario_id: int) -> list[Peixe]:
    repo = AquarioRepository(db)
    await buscar_aquario_do_usuario(repo, aquario_id, usuario_id)
    return await repo.listar_peixes(aquario_id)


async def cadastrar_peixe(db: AsyncSession, aquario_id: int, data: PeixeCreate, usuario_id: int) -> Peixe:
    repo = AquarioRepository(db)
    await buscar_aquario_do_usuario(repo, aquario_id, usuario_id)

    peixe = Peixe(aquario_id=aquario_id, nome=data.nome, especie=data.especie)
    return await repo.criar_peixe(peixe)