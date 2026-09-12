from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.conquistas.model import Conquista


class ConquistaRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def buscar(self, conquista_id: int) -> Conquista | None:
        return await self.db.get(Conquista, conquista_id)

    async def listar(self) -> list[Conquista]:
        resultado = await self.db.execute(select(Conquista).order_by(Conquista.id))
        return list(resultado.scalars().all())
    