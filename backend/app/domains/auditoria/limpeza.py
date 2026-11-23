import asyncio
import logging

from app.core.database import async_session_maker
from app.domains.auditoria.repository import AuditoriaRepository

logger = logging.getLogger(__name__)

DIAS_GUARDADOS = 60
INTERVALO_SEGUNDOS = 24 * 60 * 60


# roda junto com a api e limpa uma vez por dia os logs com mais de 60 dias
async def limpar_logs_antigos() -> None:
    while True:
        try:
            async with async_session_maker() as db:
                repo = AuditoriaRepository(db)
                await repo.apagar_antigos(DIAS_GUARDADOS)
        except Exception:
            logger.exception("falha na limpeza da auditoria")

        await asyncio.sleep(INTERVALO_SEGUNDOS)
