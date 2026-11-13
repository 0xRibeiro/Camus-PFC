from fastcrud.exceptions.http_exceptions import NotFoundException
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.aviso.model import Aviso
from app.domains.aviso.repository import AvisoRepository
from app.domains.usuario.model import Usuario


async def listar_avisos(db: AsyncSession, usuario: Usuario) -> list[Aviso]:
    return await AvisoRepository(db).listar_nao_lidos(usuario.id)


# marca o aviso como lido. se for de outra pessoa, dá 404 como se não existisse.
async def marcar_como_lido(db: AsyncSession, aviso_id: int, usuario: Usuario) -> Aviso:
    repo = AvisoRepository(db)
    aviso = await repo.buscar(aviso_id)

    if aviso is None or aviso.id_usuario != usuario.id:
        raise NotFoundException("Aviso não encontrado")

    aviso.lido = True
    return await repo.salvar(aviso)