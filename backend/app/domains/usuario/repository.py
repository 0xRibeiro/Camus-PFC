from sqlalchemy import select

from app.core.repository import BaseRepository
from app.domains.usuario.model import Usuario


class UsuarioRepository(BaseRepository[Usuario]):
    model = Usuario

    async def buscar_por_username(self, username: str) -> Usuario | None:
        result = await self.db.execute(select(Usuario).where(Usuario.username == username))
        return result.scalar_one_or_none()
