from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.grupo.model import Grupo, Participacao


class GrupoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def buscar(self, grupo_id: int) -> Grupo | None:
        return await self.db.get(Grupo, grupo_id)

    async def listar_do_usuario(self, usuario_id: int) -> list[Grupo]:
        resultado = await self.db.execute(select(Grupo).join(Participacao, Participacao.id_grupo == Grupo.id,)
        .where(Participacao.id_usuario == usuario_id).order_by(Grupo.id))

        return list(resultado.scalars().all())

    async def criar(self, grupo: Grupo) -> Grupo:
        self.db.add(grupo)

        # obtém o id sem confirmar a criação ainda pra conseguir incluir o id do dono depois
        await self.db.flush()

        participacao = Participacao(id_grupo=grupo.id, id_usuario=grupo.id_dono)
        self.db.add(participacao)

        # salva o grupo e a participação juntos
        await self.db.commit()
        await self.db.refresh(grupo)
        return grupo

    async def buscar_participacao(self, grupo_id: int, usuario_id: int) -> Participacao | None:
        return await self.db.get(Participacao, (grupo_id, usuario_id))

    async def adicionar_participante(self, grupo_id: int, usuario_id: int) -> Participacao:
        participacao = Participacao(id_grupo=grupo_id, id_usuario=usuario_id)
        self.db.add(participacao)
        await self.db.commit()
        await self.db.refresh(participacao)
        return participacao