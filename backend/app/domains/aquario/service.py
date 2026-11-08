from fastcrud.exceptions.http_exceptions import NotFoundException
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.aquario.repository import AquarioRepository
from app.domains.peixe.model import Peixe
from app.domains.peixe.schema import PeixeCreate


async def verificar_dono_do_aquario(repo: AquarioRepository, aquario_id: int, usuario_id: int,) -> None:
    if await repo.buscar_do_usuario(aquario_id, usuario_id) is None:
        raise NotFoundException("Aquário não encontrado")


async def listar_peixes(db: AsyncSession, aquario_id: int, usuario_id: int,) -> list[Peixe]:
    repo = AquarioRepository(db)
    await verificar_dono_do_aquario(repo, aquario_id, usuario_id)
    return await repo.listar_peixes(aquario_id)


async def cadastrar_peixe(db: AsyncSession, aquario_id: int, data: PeixeCreate, usuario_id: int) -> Peixe:
    repo = AquarioRepository(db)
    await verificar_dono_do_aquario(repo, aquario_id, usuario_id)
    
    peixe = Peixe(aquario_id=aquario_id, nome=data.nome, especie=data.especie)
    return await repo.criar_peixe(peixe)