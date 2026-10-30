from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.conquistas.model import associacao_conquista_usuario
from app.domains.grupo.model import Grupo
from app.domains.trilha.model import Trilha
from app.domains.usuario.model import Usuario


# todos podem retornar 0 caso não tenha dados pra não quebrar a dash
class DashboardRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def contar_usuarios(self) -> int:
        return await self.db.scalar(select(func.count()).select_from(Usuario)) or 0

    async def contar_grupos(self) -> int:
        return await self.db.scalar(select(func.count()).select_from(Grupo)) or 0

    async def contar_conquistas_concedidas(self) -> int:
        return await self.db.scalar(select(func.count()).select_from(associacao_conquista_usuario)) or 0

    async def contar_trilhas(self) -> int:
        return await self.db.scalar(select(func.count()).select_from(Trilha)) or 0