from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.pontuacao.model import LancamentoPontos, OrigemLancamento
from app.domains.trilha.model import Conteudo


class PontuacaoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def salvar(self, lancamento: LancamentoPontos) -> LancamentoPontos:
        self.db.add(lancamento)
        await self.db.commit()
        await self.db.refresh(lancamento)
        return lancamento

    async def desfazer(self) -> None:
        await self.db.rollback()

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

    # so xp global sem o de grupo
    async def somar_global(self, usuario_id: int) -> int:
        total = await self.db.scalar(
            select(func.sum(LancamentoPontos.pontos)).where(
                LancamentoPontos.usuario_id == usuario_id,
                LancamentoPontos.grupo_id.is_(None),
            )
        )
        if total is None:
            return 0
        return total

    async def listar_do_usuario(self, usuario_id: int) -> list[LancamentoPontos]:
        resultado = await self.db.execute(
            select(LancamentoPontos)
            .where(LancamentoPontos.usuario_id == usuario_id)
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
