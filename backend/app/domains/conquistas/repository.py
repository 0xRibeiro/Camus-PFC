from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.conquistas.model import Conquista, associacao_conquista_usuario


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


    ## Traz o metodo de conceder para esse repository seguindo melhor
    ## o padrão de router --> service --> repository
    async def conceder(self, user_id: int, conquista_id: int) -> Conquista | None:
        conquista = await self.buscar(conquista_id)
        if conquista is None:
            return None

        existente = await self.db.scalar(
            select(associacao_conquista_usuario.c.conquista_id).where(
                associacao_conquista_usuario.c.usuario_id == user_id,
                associacao_conquista_usuario.c.conquista_id == conquista.id,
            )
        )
        if existente is not None:
            return None

        await self.db.execute(
            associacao_conquista_usuario.insert().values(
                usuario_id=user_id,
                conquista_id=conquista.id,
            )
        )
        await self.db.commit()
        return conquista