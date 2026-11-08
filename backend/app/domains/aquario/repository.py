from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.aquario.model import Aquario
from app.domains.peixe.model import Peixe


# os 3 metodos atuais fazem as ações basicas de CRUD.
class AquarioRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def buscar_do_usuario(self, aquario_id: int, usuario_id: int) -> Aquario | None:
        consulta = select(Aquario).where(Aquario.id == aquario_id, Aquario.id_dono == usuario_id)
        return await self.db.scalar(consulta)

    async def listar_peixes(self, aquario_id: int) -> list[Peixe]:
        consulta = select(Peixe).where(Peixe.aquario_id == aquario_id).order_by(Peixe.id)
        return list((await self.db.scalars(consulta)).all())

    async def criar_peixe(self, peixe: Peixe) -> Peixe:
        self.db.add(peixe)
        await self.db.commit()
        await self.db.refresh(peixe)
        return peixe