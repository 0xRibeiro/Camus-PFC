from datetime import date, timedelta

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.dashboard.repository import DashboardRepository
from app.domains.dashboard.schema import (
    Agrupamento,
    ConquistaResumoRead,
    DashboardRead,
    PontoEvolucaoRead,
    TotaisPeriodoRead,
)

LINHAS = ["alunos", "dispositivos", "trilhas", "grupos"]


# comeco da semana (segunda) ou do mes
def inicio_do_grupo(dia: date, agrupamento: Agrupamento) -> date:
    if agrupamento == "semana":
        return dia - timedelta(days=dia.weekday())
    if agrupamento == "mes":
        return dia.replace(day=1)
    return dia


async def contar_linhas(repo: DashboardRepository, inicio: date, fim: date) -> dict[str, dict[date, int]]:
    return {
        "alunos": await repo.contar_alunos_por_dia(inicio, fim),
        "dispositivos": await repo.contar_dispositivos_por_dia(inicio, fim),
        "trilhas": await repo.contar_criados_por_dia("trilhas", inicio, fim),
        "grupos": await repo.contar_criados_por_dia("grupos", inicio, fim),
    }


def somar_totais(contagens: dict[str, dict[date, int]]) -> TotaisPeriodoRead:
    totais = {}
    for linha in LINHAS:
        totais[linha] = sum(contagens[linha].values())
    return TotaisPeriodoRead(**totais)


# junta os dias no ponto do grupo, dia sem nada entra com 0
def montar_evolucao(contagens: dict[str, dict[date, int]], inicio: date, fim: date,
    agrupamento: Agrupamento) -> list[PontoEvolucaoRead]:
    pontos: dict[date, dict[str, int]] = {}

    dia = inicio
    while dia <= fim:
        chave = inicio_do_grupo(dia, agrupamento)
        if chave not in pontos:
            pontos[chave] = {}
            for linha in LINHAS:
                pontos[chave][linha] = 0

        for linha in LINHAS:
            pontos[chave][linha] += contagens[linha].get(dia, 0)
        dia += timedelta(days=1)

    evolucao = []
    for chave, valores in pontos.items():
        evolucao.append(PontoEvolucaoRead(data=chave, **valores))
    return evolucao


async def obter_dashboard(db: AsyncSession, inicio: date | None, fim: date | None,
    agrupamento: Agrupamento) -> DashboardRead:
    repo = DashboardRepository(db)

    # sem datas pega os ultimos 30 dias
    if fim is None:
        fim = await repo.buscar_data_atual()
    if inicio is None:
        inicio = fim - timedelta(days=29)

    if inicio > fim:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A data inicial deve ser antes da final")

    # periodo anterior do msm tamanho
    tamanho = fim - inicio + timedelta(days=1)
    contagens = await contar_linhas(repo, inicio, fim)
    contagens_anteriores = await contar_linhas(repo, inicio - tamanho, inicio - timedelta(days=1))

    conquistas = []
    for conquista_id, titulo, imagem_dir, quantidade in await repo.contar_conquistas_por_quantidade():
        conquistas.append(ConquistaResumoRead(id=conquista_id, titulo=titulo, imagem_dir=imagem_dir, quantidade=quantidade))

    trilhas_globais, trilhas_de_grupo = await repo.contar_trilhas_por_escopo()
    return DashboardRead(
        evolucao=montar_evolucao(contagens, inicio, fim, agrupamento),
        totais=somar_totais(contagens),
        totais_anteriores=somar_totais(contagens_anteriores),
        conquistas_por_quantidade=conquistas,
        total_alunos=await repo.contar_alunos(),
        total_trilhas_globais=trilhas_globais,
        total_trilhas_de_grupo=trilhas_de_grupo,
    )
