from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.aviso.model import Aviso
from app.domains.grupo.model import Grupo
from app.domains.trilha.model import Conteudo, Modulo, Trilha


class ModeracaoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def buscar_grupo(self, grupo_id: int) -> Grupo | None:
        return await self.db.get(Grupo, grupo_id)

    # só devolve o conteúdo se ele for de uma trilha do grupo (conteúdo -> módulo -> trilha -> grupo)
    async def buscar_conteudo_do_grupo(self, conteudo_id: int, grupo_id: int) -> Conteudo | None:
        consulta = (
            select(Conteudo)
            .join(Modulo, Modulo.id == Conteudo.modulo_id)
            .join(Trilha, Trilha.id == Modulo.trilha_id)
            .where(Conteudo.id == conteudo_id, Trilha.grupo_id == grupo_id)
        )
        resultado = await self.db.execute(consulta)
        return resultado.scalars().first()

    # a ação e o aviso vão pro banco juntos, se um der erro o outro também não grava
    async def suspender(self, grupo: Grupo, ate: datetime, aviso: Aviso) -> Grupo:
        grupo.suspenso_ate = ate
        self.db.add(aviso)
        await self.db.commit()
        await self.db.refresh(grupo)
        return grupo

    async def excluir_grupo(self, grupo: Grupo, aviso: Aviso) -> None:
        await self.db.delete(grupo)
        self.db.add(aviso)
        await self.db.commit()

    async def excluir_conteudo(self, conteudo: Conteudo, aviso: Aviso) -> None:
        await self.db.delete(conteudo)
        self.db.add(aviso)
        await self.db.commit()