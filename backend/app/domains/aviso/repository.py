from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.aviso.model import Aviso


class AvisoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # traz só os avisos que o usuário ainda não dispensou, começando pelo mais novo
    async def listar_nao_lidos(self, id_usuario: int) -> list[Aviso]:
        consulta = (
            select(Aviso)
            .where(Aviso.id_usuario == id_usuario, Aviso.lido.is_(False))
            .order_by(Aviso.criado_em.desc(), Aviso.id.desc())
        )
        resultado = await self.db.execute(consulta)
        return list(resultado.scalars().all())

    async def buscar(self, aviso_id: int) -> Aviso | None:
        return await self.db.get(Aviso, aviso_id)

    async def salvar(self, aviso: Aviso) -> Aviso:
        await self.db.commit()
        await self.db.refresh(aviso)
        return aviso