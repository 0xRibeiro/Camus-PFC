from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.aquario.model import AquarioMembro, PapelAquario
from app.domains.dispositivo.model import Dispositivo


class DispositivoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def buscar(self, id_dispositivo: int) -> Dispositivo | None:
        return await self.db.get(Dispositivo, id_dispositivo)

    async def buscar_por_mac(self, mac: str) -> Dispositivo | None:
        resultado = await self.db.execute(select(Dispositivo).where(Dispositivo.mac == mac))
        return resultado.scalar_one_or_none()

    async def buscar_do_aquario(self, id_aquario: int) -> Dispositivo | None:
        resultado = await self.db.execute(select(Dispositivo).where(Dispositivo.id_aquario == id_aquario))
        return resultado.scalar_one_or_none()

    # serve pra criar e pra atualizar
    async def salvar(self, dispositivo: Dispositivo) -> Dispositivo:
        self.db.add(dispositivo)
        await self.db.commit()
        await self.db.refresh(dispositivo)
        return dispositivo

    # sem commit, vai junto no salvar
    async def remover_operadores(self, id_aquario: int) -> int:
        resultado = await self.db.execute(delete(AquarioMembro).where(AquarioMembro.id_aquario == id_aquario)
        .where(AquarioMembro.papel == PapelAquario.operador).returning(AquarioMembro.id_usuario))
        return len(resultado.all())
