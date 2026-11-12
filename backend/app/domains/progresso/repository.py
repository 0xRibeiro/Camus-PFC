from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.progresso.model import ConclusaoConteudo, TentativaQuiz
from app.domains.trilha.model import Alternativa, Conteudo, Modulo, Questao, Trilha
from app.domains.usuario.model import Usuario


class ProgressoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.grupo_id = db.info.get("grupo_id")

    ###### trilha modulo e conteudo
    async def listar_trilhas_ativas(self) -> list[Trilha]:
        resultado = await self.db.execute(select(Trilha).where(Trilha.is_active.is_(True), Trilha.grupo_id == self.grupo_id).order_by(Trilha.id))
        return list(resultado.scalars().all())

    async def buscar_trilha(self, trilha_id: int) -> Trilha | None:
        return await self.db.scalar(select(Trilha).where(Trilha.id == trilha_id, Trilha.grupo_id == self.grupo_id))

    async def buscar_modulo(self, modulo_id: int) -> Modulo | None:
        return await self.db.get(Modulo, modulo_id)

    async def buscar_conteudo(self, conteudo_id: int) -> Conteudo | None:
        return await self.db.scalar(select(Conteudo).join(Modulo, Conteudo.modulo_id == Modulo.id).join(Trilha, Modulo.trilha_id == Trilha.id).where(Conteudo.id == conteudo_id, Trilha.grupo_id == self.grupo_id))

    async def listar_modulos(self, trilha_ids: list[int]) -> list[Modulo]:
        resultado = await self.db.execute(select(Modulo).where(Modulo.trilha_id.in_(trilha_ids)).order_by(Modulo.ordem, Modulo.id))
        return list(resultado.scalars().all())

    async def listar_conteudos(self, modulo_ids: list[int]) -> list[Conteudo]:
        resultado = await self.db.execute(select(Conteudo).where(Conteudo.modulo_id.in_(modulo_ids)).order_by(Conteudo.ordem, Conteudo.id))
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

    async def bloquear_progresso(self, usuario_id: int) -> None:
        await self.db.execute(
            select(Usuario.id).where(Usuario.id == usuario_id).with_for_update()
        )

    def salvar_conclusao(self, conclusao: ConclusaoConteudo) -> None:
        self.db.add(conclusao)

    def salvar_tentativa(self, tentativa: TentativaQuiz) -> None:
        self.db.add(tentativa)

    # unica função que commita agora, centralizando o commit
    async def confirmar(self) -> None:
        await self.db.commit()