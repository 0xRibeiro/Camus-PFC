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

    async def salvar(self, conquista: Conquista) -> Conquista:
        self.db.add(conquista)
        await self.db.commit()
        await self.db.refresh(conquista) 
        return conquista

    async def deletar(self, conquista: Conquista) -> None:
        await self.db.delete(conquista)
        await self.db.commit()