from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.aquario.model import Aquario, AquarioMembro, PapelAquario
from app.domains.peixe.model import Peixe
from app.domains.usuario.model import Usuario


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

    async def buscar(self, aquario_id: int) -> Aquario | None:
        return await self.db.get(Aquario, aquario_id)

    async def buscar_membro(self, aquario_id: int, usuario_id: int) -> AquarioMembro | None:
        return await self.db.get(AquarioMembro, (aquario_id, usuario_id))

    # serve pra adicionar e pra trocar o papel
    async def salvar_membro(self, aquario_id: int, usuario_id: int, papel: PapelAquario) -> AquarioMembro:
        membro = await self.buscar_membro(aquario_id, usuario_id)
        if membro is None:
            membro = AquarioMembro(id_aquario=aquario_id, id_usuario=usuario_id)

        membro.papel = papel
        self.db.add(membro)
        await self.db.commit()
        await self.db.refresh(membro)
        return membro

    async def remover_membro(self, membro: AquarioMembro) -> None:
        await self.db.delete(membro)
        await self.db.commit()

    # os q ele criou + os q ele e membro
    async def listar_do_usuario(self, usuario_id: int) -> list[Aquario]:
        membro_de = select(AquarioMembro.id_aquario).where(AquarioMembro.id_usuario == usuario_id)
        consulta = select(Aquario).where(or_(Aquario.id_dono == usuario_id, Aquario.id.in_(membro_de))).order_by(Aquario.id)
        return list((await self.db.scalars(consulta)).all())

    async def listar_membros(self, aquario_id: int) -> list[tuple[str, PapelAquario]]:
        consulta = (select(Usuario.username, AquarioMembro.papel).join(AquarioMembro, AquarioMembro.id_usuario == Usuario.id)
        .where(AquarioMembro.id_aquario == aquario_id).order_by(Usuario.username))
        resultado = await self.db.execute(consulta)

        membros = []
        for username, papel in resultado.all():
            membros.append((username, papel))
        return membros

    async def buscar_username(self, usuario_id: int) -> str | None:
        return await self.db.scalar(select(Usuario.username).where(Usuario.id == usuario_id))