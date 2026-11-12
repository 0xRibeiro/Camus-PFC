from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.dispositivo.model import Dispositivo


class DispositivoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def buscar_por_mac(self, mac: str) -> Dispositivo | None:
        resultado = await self.db.execute(select(Dispositivo).where(Dispositivo.mac == mac))
        return resultado.scalar_one_or_none()

    # serve pra criar e pra atualizar
    async def salvar(self, dispositivo: Dispositivo) -> Dispositivo:
        self.db.add(dispositivo)
        await self.db.commit()
        await self.db.refresh(dispositivo)
        return dispositivo
