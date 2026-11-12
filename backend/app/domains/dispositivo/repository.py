from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.dispositivo.model import Dispositivo, DispositivoUsuario
from app.domains.usuario.model import Usuario


class DispositivoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def buscar(self, id_dispositivo: int) -> Dispositivo | None:
        return await self.db.get(Dispositivo, id_dispositivo)

    async def buscar_por_mac(self, mac: str) -> Dispositivo | None:
        resultado = await self.db.execute(select(Dispositivo).where(Dispositivo.mac == mac))
        return resultado.scalar_one_or_none()

    async def listar_do_usuario(self, id_usuario: int) -> list[Dispositivo]:
        resultado = await self.db.execute(select(Dispositivo).join(DispositivoUsuario, DispositivoUsuario.id_dispositivo == Dispositivo.id)
        .where(DispositivoUsuario.id_usuario == id_usuario).order_by(Dispositivo.id))
        return list(resultado.scalars().all())

    async def listar_usuarios(self, id_dispositivo: int) -> list[tuple[str, datetime]]:
        resultado = await self.db.execute(select(Usuario.username, DispositivoUsuario.vinculado_em)
        .join(DispositivoUsuario, DispositivoUsuario.id_usuario == Usuario.id)
        .where(DispositivoUsuario.id_dispositivo == id_dispositivo).order_by(DispositivoUsuario.vinculado_em))

        linhas = []
        for username, vinculado_em in resultado.all():
            linhas.append((username, vinculado_em))
        return linhas

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

    async def remover_vinculo(self, vinculo: DispositivoUsuario) -> None:
        await self.db.delete(vinculo)
        await self.db.commit()

    async def remover_vinculos(self, id_dispositivo: int) -> int:
        resultado = await self.db.execute(delete(DispositivoUsuario).where(DispositivoUsuario.id_dispositivo == id_dispositivo)
        .returning(DispositivoUsuario.id_usuario))
        removidos = len(resultado.all())
        await self.db.commit()
        return removidos
