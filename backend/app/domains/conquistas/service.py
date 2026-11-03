from fastcrud.exceptions.http_exceptions import ForbiddenException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis import redis_client
from app.domains.conquistas.model import Conquista
from app.domains.conquistas.repository import ConquistaRepository
from app.domains.grupo.repository import GrupoRepository


async def conceder_conquista(db: AsyncSession, user_id: int, conquista_id: int) -> Conquista | None:
    repo = ConquistaRepository(db)

    # as conquistas da interface continuam com a mesma logica de antes
    if conquista_id not in (8, 9, 10):
        return await repo.conceder(user_id, conquista_id)

    grupos = await GrupoRepository(db).listar_do_usuario(user_id)

    # conquista 8: precisa ser dono de pelo menos um grupo
    if conquista_id == 8 and not any(grupo.id_dono == user_id for grupo in grupos):
        raise ForbiddenException("Crie um grupo para obter esta conquista")

    # conquista 9: ser dono do próprio grupo não conta como entrar por convite
    if conquista_id == 9 and not any(grupo.id_dono != user_id for grupo in grupos):
        raise ForbiddenException("Entre no grupo de outro usuário para obter esta conquista")

    # conquista 10: procura um convite válido pertencente a um grupo do usuário
    if conquista_id == 10:
        grupos_criados = {str(grupo.id) for grupo in grupos if grupo.id_dono == user_id}

        if grupos_criados:
            async for chave in redis_client.scan_iter(match="grupo:convite:*"):
                grupo_id = await redis_client.get(chave)

                if grupo_id in grupos_criados:
                    return await repo.conceder(user_id, conquista_id)

        raise ForbiddenException("Gere um convite para o seu grupo para obter esta conquista")

    return await repo.conceder(user_id, conquista_id)