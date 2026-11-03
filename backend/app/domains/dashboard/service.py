from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.dashboard.repository import DashboardRepository
from app.domains.dashboard.schema import (
    CadastroDiaRead,
    ConquistaResumoRead,
    DashboardRead,
)


# deixei como 30 dias pra facilitar.
async def obter_dashboard(db: AsyncSession, dias: int = 30) -> DashboardRead:
    repo = DashboardRepository(db)

    # usando timedelta pra buscar sempre os ultimos 30 dias.
    fim = await repo.buscar_data_atual()
    inicio = fim - timedelta(days=dias - 1)

    cadastros = await repo.contar_cadastros_por_dia(inicio, fim)
    conquistas = await repo.contar_conquistas_por_quantidade()

    # monta todos os dias do período, incluindo aqueles sem registros
    cadastros_por_dia: list[CadastroDiaRead] = []

    for indice in range(dias):
        dia = inicio + timedelta(days=indice)
        cadastros_por_dia.append(CadastroDiaRead(data=dia, quantidade=cadastros.get(dia, 0)))

    return DashboardRead(
        total_usuarios=await repo.contar_usuarios(),
        total_grupos=await repo.contar_grupos(),
        total_conquistas_concedidas=await repo.contar_conquistas_concedidas(),
        total_trilhas=await repo.contar_trilhas(),
        cadastros_por_dia=cadastros_por_dia,
        conquistas_por_quantidade=[
            ConquistaResumoRead(id=conquista_id, titulo=titulo, quantidade=quantidade)
            for conquista_id, titulo, quantidade in conquistas
        ],
    )