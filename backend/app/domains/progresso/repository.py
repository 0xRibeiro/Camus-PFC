from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.progresso.model import ConclusaoConteudo, TentativaQuiz
from app.domains.trilha.model import Alternativa, Conteudo, Modulo, Questao, Trilha


class ProgressoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    ###### trilha modulo e conteudo
    async def listar_trilhas_ativas(self) -> list[Trilha]:
        resultado = await self.db.execute(
            select(Trilha).where(Trilha.is_active.is_(True)).order_by(Trilha.id)
        )
        return list(resultado.scalars().all())

    async def buscar_trilha(self, trilha_id: int) -> Trilha | None:
        return await self.db.get(Trilha, trilha_id)

    async def buscar_modulo(self, modulo_id: int) -> Modulo | None:
        return await self.db.get(Modulo, modulo_id)

    async def buscar_conteudo(self, conteudo_id: int) -> Conteudo | None:
        return await self.db.get(Conteudo, conteudo_id)

    async def listar_modulos(self, trilha_ids: list[int]) -> list[Modulo]:
        resultado = await self.db.execute(
            select(Modulo).where(Modulo.trilha_id.in_(trilha_ids)).order_by(Modulo.ordem)
        )
        return list(resultado.scalars().all())

    async def listar_conteudos(self, modulo_ids: list[int]) -> list[Conteudo]:
        resultado = await self.db.execute(
            select(Conteudo).where(Conteudo.modulo_id.in_(modulo_ids)).order_by(Conteudo.ordem)
        )
        return list(resultado.scalars().all())

    ###### quiz
    async def listar_questoes(self, conteudo_id: int) -> list[Questao]:
        resultado = await self.db.execute(
            select(Questao).where(Questao.conteudo_id == conteudo_id).order_by(Questao.ordem)
        )
        return list(resultado.scalars().all())

    async def listar_alternativas(self, questao_ids: list[int]) -> list[Alternativa]:
        resultado = await self.db.execute(
            select(Alternativa).where(Alternativa.questao_id.in_(questao_ids))
        )
        return list(resultado.scalars().all())

    ###### conclusao e tentativa do usuario
    async def listar_conclusoes(
        self, usuario_id: int, conteudo_ids: list[int]
    ) -> list[ConclusaoConteudo]:
        resultado = await self.db.execute(
            select(ConclusaoConteudo).where(
                ConclusaoConteudo.usuario_id == usuario_id,
                ConclusaoConteudo.conteudo_id.in_(conteudo_ids),
            )
        )
        return list(resultado.scalars().all())

    async def buscar_conclusao(
        self, usuario_id: int, conteudo_id: int
    ) -> ConclusaoConteudo | None:
        return await self.db.scalar(
            select(ConclusaoConteudo).where(
                ConclusaoConteudo.usuario_id == usuario_id,
                ConclusaoConteudo.conteudo_id == conteudo_id,
            )
        )

    async def salvar_conclusao(self, conclusao: ConclusaoConteudo) -> ConclusaoConteudo:
        self.db.add(conclusao)
        await self.db.commit()
        await self.db.refresh(conclusao)
        return conclusao

    async def salvar_tentativa(self, tentativa: TentativaQuiz) -> TentativaQuiz:
        self.db.add(tentativa)
        await self.db.commit()
        await self.db.refresh(tentativa)
        return tentativa
