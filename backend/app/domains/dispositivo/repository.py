from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.dispositivo.model import Dispositivo, DispositivoUsuario


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

    async def buscar_vinculo(self, id_dispositivo: int, id_usuario: int) -> DispositivoUsuario | None:
        return await self.db.get(DispositivoUsuario, (id_dispositivo, id_usuario))

    async def adicionar_vinculo(self, id_dispositivo: int, id_usuario: int) -> DispositivoUsuario:
        vinculo = DispositivoUsuario(id_dispositivo=id_dispositivo, id_usuario=id_usuario)
        self.db.add(vinculo)
        await self.db.commit()
        await self.db.refresh(vinculo)
        return vinculo

    async def remover_vinculos(self, id_dispositivo: int) -> int:
        resultado = await self.db.execute(delete(DispositivoUsuario).where(DispositivoUsuario.id_dispositivo == id_dispositivo)
        .returning(DispositivoUsuario.id_usuario))
        removidos = len(resultado.all())
        await self.db.commit()
        return removidos
