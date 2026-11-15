from sqlalchemy import Date, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.minigame.model import RodadaMinigame


class MinigameRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def adicionar(self, rodada: RodadaMinigame) -> None:
        self.db.add(rodada)

    # filtra pelo usuario tbm, ninguem responde rodada dos outros
    async def buscar_rodada(self, rodada_id: int, usuario_id: int) -> RodadaMinigame | None:
        return await self.db.scalar(
            select(RodadaMinigame).where(
                RodadaMinigame.id == rodada_id,
                RodadaMinigame.usuario_id == usuario_id,
            )
        )

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
