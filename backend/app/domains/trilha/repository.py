from sqlalchemy import select

from app.core.repository import BaseRepository
from app.domains.trilha.model import Alternativa, Conteudo, Modulo, Questao, Trilha


class TrilhaRepository(BaseRepository[Trilha]):
    model = Trilha


class ModuloRepository(BaseRepository[Modulo]):
    model = Modulo

    async def listar_por_trilha(self, trilha_id: int) -> list[Modulo]:
        result = await self.db.execute(
            select(Modulo).where(Modulo.trilha_id == trilha_id).order_by(Modulo.ordem)
        )
        return list(result.scalars().all())


class ConteudoRepository(BaseRepository[Conteudo]):
    model = Conteudo

    async def listar_por_modulo(self, modulo_id: int) -> list[Conteudo]:
        result = await self.db.execute(
            select(Conteudo)
            .where(Conteudo.modulo_id == modulo_id)
            .order_by(Conteudo.ordem)
        )
        return list(result.scalars().all())


class QuestaoRepository(BaseRepository[Questao]):
    model = Questao

    async def listar_por_conteudo(self, conteudo_id: int) -> list[Questao]:
        result = await self.db.execute(
            select(Questao)
            .where(Questao.conteudo_id == conteudo_id)
            .order_by(Questao.ordem)
        )
        return list(result.scalars().all())


class AlternativaRepository(BaseRepository[Alternativa]):
    model = Alternativa

    async def listar_por_questao(self, questao_id: int) -> list[Alternativa]:
        result = await self.db.execute(
            select(Alternativa)
            .where(Alternativa.questao_id == questao_id)
            .order_by(Alternativa.id)
        )
        return list(result.scalars().all())
