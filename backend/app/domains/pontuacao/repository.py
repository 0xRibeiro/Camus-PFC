from datetime import date

from sqlalchemy import Date, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.minigame.model import TITULOS_JOGOS, RodadaMinigame
from app.domains.pontuacao.model import LancamentoPontos, OrigemLancamento
from app.domains.trilha.model import Conteudo
from app.domains.usuario.model import Usuario

# dia do lancamento no fuso de sp
DIA_DO_LANCAMENTO = cast(func.timezone("America/Sao_Paulo", LancamentoPontos.criado_em), Date)


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

    # so xp global, sem conta excluida ou desativada. empate desempata pelo username
    async def listar_ranking(self, limite: int) -> list[tuple[Usuario, int]]:
        total = func.sum(LancamentoPontos.pontos).label("total")
        resultado = await self.db.execute(
            select(Usuario, total)
            .join(LancamentoPontos, LancamentoPontos.usuario_id == Usuario.id)
            .where(
                LancamentoPontos.grupo_id.is_(None),
                Usuario.deletado_em.is_(None),
                Usuario.is_active.is_(True),
            )
            .group_by(Usuario.id)
            .order_by(total.desc(), Usuario.username)
            .limit(limite)
        )
        ranking = []
        for usuario, xp in resultado.all():
            ranking.append((usuario, xp))
        return ranking

    # quem ta na frente no ranking global, msm desempate do listar_ranking
    async def contar_na_frente(self, usuario: Usuario, xp: int) -> int:
        total = func.sum(LancamentoPontos.pontos).label("total")
        totais = (
            select(Usuario.username, total)
            .join(LancamentoPontos, LancamentoPontos.usuario_id == Usuario.id)
            .where(
                LancamentoPontos.grupo_id.is_(None),
                Usuario.deletado_em.is_(None),
                Usuario.is_active.is_(True),
            )
            .group_by(Usuario.id)
            .subquery()
        )
        quantidade = await self.db.scalar(
            select(func.count()).select_from(totais).where(
                (totais.c.total > xp) | ((totais.c.total == xp) & (totais.c.username < usuario.username))
            )
        )
        if quantidade is None:
            return 0
        return quantidade

    # so os dias q teve xp, os vazios o service completa
    async def somar_por_dia(self, usuario_id: int, grupo_id: int | None, inicio: date) -> dict[date, int]:
        resultado = await self.db.execute(
            select(DIA_DO_LANCAMENTO, func.sum(LancamentoPontos.pontos))
            .where(
                LancamentoPontos.usuario_id == usuario_id,
                LancamentoPontos.grupo_id == grupo_id,
                DIA_DO_LANCAMENTO >= inicio,
            )
            .group_by(DIA_DO_LANCAMENTO)
        )
        pontos = {}
        for dia, soma in resultado.all():
            pontos[dia] = soma
        return pontos

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

    # nome do jogo de cada rodada, com (combo) qnd for xp de combo
    async def listar_titulos_minigames(self, rodada_ids: list[int]) -> dict[int, str]:
        resultado = await self.db.execute(
            select(RodadaMinigame.id, RodadaMinigame.jogo, RodadaMinigame.combo).where(RodadaMinigame.id.in_(rodada_ids))
        )
        titulos = {}
        for rodada_id, jogo, combo in resultado.all():
            titulo = TITULOS_JOGOS.get(jogo, "Minigame")
            if combo:
                titulo += " (combo)"
            titulos[rodada_id] = titulo
        return titulos