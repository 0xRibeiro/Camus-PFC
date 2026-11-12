from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.pontuacao.model import LancamentoPontos, OrigemLancamento
from app.domains.trilha.model import Conteudo


class PontuacaoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # adiciona apenas na sessão sem fazr o commit ainda pra evitar erros de ganhar o xp sem cumprir o conteudo
    def adicionar(self, lancamento: LancamentoPontos) -> None:
        self.db.add(lancamento)

    async def somar_por_origem(
        self,
        usuario_id: int,
        origem_tipo: OrigemLancamento,
        origem_id: int,
    ) -> int:
        total = await self.db.scalar(
            select(func.sum(LancamentoPontos.pontos)).where(
                LancamentoPontos.usuario_id == usuario_id,
                LancamentoPontos.origem_tipo == origem_tipo,
                LancamentoPontos.origem_id == origem_id,
            )
        )
        # sum sem nenhuma linha volta None
        if total is None:
            return 0
        return total

    # Escopo nulo soma só o XP global. Com grupo_id, soma só o XP do grupo.
    async def somar_xp(self, usuario_id: int, grupo_id: int | None) -> int:
        total = await self.db.scalar(
            select(func.sum(LancamentoPontos.pontos)).where(
                LancamentoPontos.usuario_id == usuario_id,
                LancamentoPontos.grupo_id == grupo_id,
            )
        )
        if total is None:
            return 0
        return total

    async def listar_do_usuario(
        self, usuario_id: int, grupo_id: int | None
    ) -> list[LancamentoPontos]:
        resultado = await self.db.execute(
            select(LancamentoPontos)
            .where(
                LancamentoPontos.usuario_id == usuario_id,
                LancamentoPontos.grupo_id == grupo_id,
            )
            .order_by(LancamentoPontos.criado_em.desc())
        )
        return list(resultado.scalars().all())

    async def listar_titulos_conteudos(self, conteudo_ids: list[int]) -> dict[int, str]:
        resultado = await self.db.execute(
            select(Conteudo.id, Conteudo.titulo).where(Conteudo.id.in_(conteudo_ids))
        )
        titulos = {}
        for conteudo_id, titulo in resultado.all():
            titulos[conteudo_id] = titulo
        return titulos