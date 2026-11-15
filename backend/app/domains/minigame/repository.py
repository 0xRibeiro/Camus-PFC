from sqlalchemy import Date, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.minigame.model import RodadaMinigame


class MinigameRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def adicionar(self, rodada: RodadaMinigame) -> None:
        self.db.add(rodada)

    # filtra pelo usuario e jogo tbm, ninguem responde rodada dos outros nem de outro jogo
    async def buscar_rodada(self, rodada_id: int, usuario_id: int, jogo: str) -> RodadaMinigame | None:
        return await self.db.scalar(
            select(RodadaMinigame).where(
                RodadaMinigame.id == rodada_id,
                RodadaMinigame.usuario_id == usuario_id,
                RodadaMinigame.jogo == jogo,
            )
        )

    # rodada sem resposta, recarregar a pagina devolve a msm pergunta
    async def buscar_pendente(self, usuario_id: int, jogo: str) -> RodadaMinigame | None:
        return await self.db.scalar(
            select(RodadaMinigame)
            .where(
                RodadaMinigame.usuario_id == usuario_id,
                RodadaMinigame.jogo == jogo,
                RodadaMinigame.acertou.is_(None),
            )
            .order_by(RodadaMinigame.id.desc())
            .limit(1)
        )

    async def buscar_ultima_respondida(self, usuario_id: int, jogo: str) -> RodadaMinigame | None:
        return await self.db.scalar(
            select(RodadaMinigame)
            .where(
                RodadaMinigame.usuario_id == usuario_id,
                RodadaMinigame.jogo == jogo,
                RodadaMinigame.acertou.is_not(None),
            )
            .order_by(RodadaMinigame.respondida_em.desc())
            .limit(1)
        )

    # do mais novo pro mais velho, pra contar sequencia e recorde
    async def listar_acertos(self, usuario_id: int, jogo: str) -> list[bool]:
        resultado = await self.db.execute(
            select(RodadaMinigame.acertou)
            .where(
                RodadaMinigame.usuario_id == usuario_id,
                RodadaMinigame.jogo == jogo,
                RodadaMinigame.acertou.is_not(None),
            )
            .order_by(RodadaMinigame.respondida_em.desc())
        )
        return list(resultado.scalars().all())

    # dia no fuso de sp igual a dashboard, se n vira o dia as 21h
    # limite é por jogo e acerto em combo fica de fora
    async def contar_acertos_com_xp_hoje(self, usuario_id: int, jogo: str) -> int:
        hoje = cast(func.timezone("America/Sao_Paulo", func.now()), Date)
        dia_resposta = cast(func.timezone("America/Sao_Paulo", RodadaMinigame.respondida_em), Date)
        resultado = await self.db.execute(
            select(func.count()).select_from(RodadaMinigame).where(
                RodadaMinigame.usuario_id == usuario_id,
                RodadaMinigame.jogo == jogo,
                RodadaMinigame.pontos > 0,
                RodadaMinigame.combo.is_(False),
                dia_resposta == hoje,
            )
        )
        return resultado.scalar_one()

    # unico commit do minigame, junto vai o lancamento de xp se tiver
    async def salvar(self, rodada: RodadaMinigame) -> None:
        await self.db.commit()
        await self.db.refresh(rodada)
