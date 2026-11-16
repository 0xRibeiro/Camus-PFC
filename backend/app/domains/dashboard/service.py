from datetime import date, timedelta

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.dashboard.repository import DashboardRepository
from app.domains.dashboard.schema import (
    Agrupamento,
    ConquistaResumoRead,
    ConteudoFunilRead,
    DashboardRead,
    DashboardTrilhaRead,
    EngajamentoTrilhaRead,
    PontoEvolucaoRead,
    PontoEvolucaoTrilhaRead,
    TotaisPeriodoRead,
    TotaisTrilhaRead,
)
from app.domains.trilha.model import Conteudo

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


def somar_totais(contagens: dict[str, dict[date, int]]) -> dict[str, int]:
    totais = {}
    for linha, por_dia in contagens.items():
        totais[linha] = sum(por_dia.values())
    return totais


# junta os dias no ponto do grupo, dia sem nada entra com 0
def montar_evolucao(contagens: dict[str, dict[date, int]], inicio: date, fim: date,
    agrupamento: Agrupamento) -> list[dict]:
    pontos: dict[date, dict] = {}

    dia = inicio
    while dia <= fim:
        chave = inicio_do_grupo(dia, agrupamento)
        if chave not in pontos:
            pontos[chave] = {"data": chave}
            for linha in contagens:
                pontos[chave][linha] = 0

        for linha, por_dia in contagens.items():
            pontos[chave][linha] += por_dia.get(dia, 0)
        dia += timedelta(days=1)

    return list(pontos.values())


# sem datas pega os ultimos 30 dias, devolve tbm o periodo anterior do msm tamanho
async def resolver_periodo(repo: DashboardRepository, inicio: date | None,
    fim: date | None) -> tuple[date, date, date, date]:
    if fim is None:
        fim = await repo.buscar_data_atual()
    if inicio is None:
        inicio = fim - timedelta(days=29)

    if inicio > fim:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A data inicial deve ser antes da final")

    tamanho = fim - inicio + timedelta(days=1)
    return inicio, fim, inicio - tamanho, inicio - timedelta(days=1)


async def obter_dashboard(db: AsyncSession, inicio: date | None, fim: date | None,
    agrupamento: Agrupamento) -> DashboardRead:
    repo = DashboardRepository(db)
    inicio, fim, inicio_anterior, fim_anterior = await resolver_periodo(repo, inicio, fim)

    contagens = await contar_linhas(repo, inicio, fim)
    contagens_anteriores = await contar_linhas(repo, inicio_anterior, fim_anterior)

    evolucao = []
    for ponto in montar_evolucao(contagens, inicio, fim, agrupamento):
        evolucao.append(PontoEvolucaoRead(**ponto))

    conquistas = []
    for conquista_id, titulo, imagem_dir, quantidade in await repo.contar_conquistas_por_quantidade():
        conquistas.append(ConquistaResumoRead(id=conquista_id, titulo=titulo, imagem_dir=imagem_dir, quantidade=quantidade))

    trilhas_globais, trilhas_de_grupo = await repo.contar_trilhas_por_escopo()
    return DashboardRead(
        evolucao=evolucao,
        totais=TotaisPeriodoRead(**somar_totais(contagens)),
        totais_anteriores=TotaisPeriodoRead(**somar_totais(contagens_anteriores)),
        conquistas_por_quantidade=conquistas,
        total_alunos=await repo.contar_alunos(),
        total_trilhas_globais=trilhas_globais,
        total_trilhas_de_grupo=trilhas_de_grupo,
    )


async def contar_totais_trilha(repo: DashboardRepository, conteudos: list[int], inicio: date,
    fim: date, contagens: dict[str, dict[date, int]]) -> TotaisTrilhaRead:
    return TotaisTrilhaRead(
        alunos_ativos=len(await repo.listar_alunos_ativos(conteudos, inicio, fim)),
        **somar_totais(contagens),
    )


# novo conta no 1o dia, terminou conta no dia da ultima conclusao
def contar_novos_e_terminaram(progresso: list[tuple[int, int, date, date]],
    total_conteudos: int) -> tuple[dict[date, int], dict[date, int]]:
    novos: dict[date, int] = {}
    terminaram: dict[date, int] = {}
    for _, quantidade, primeiro_dia, ultimo_dia in progresso:
        novos[primeiro_dia] = novos.get(primeiro_dia, 0) + 1
        if quantidade == total_conteudos:
            terminaram[ultimo_dia] = terminaram.get(ultimo_dia, 0) + 1
    return novos, terminaram


def filtrar_periodo(por_dia: dict[date, int], inicio: date, fim: date) -> dict[date, int]:
    filtrado = {}
    for dia, quantidade in por_dia.items():
        if inicio <= dia <= fim:
            filtrado[dia] = quantidade
    return filtrado


async def contar_linhas_trilha(repo: DashboardRepository, conteudos: list[int], novos: dict[date, int],
    terminaram: dict[date, int], inicio: date, fim: date) -> dict[str, dict[date, int]]:
    return {
        "conclusoes": await repo.contar_conclusoes_por_dia(conteudos, inicio, fim),
        "novos": filtrar_periodo(novos, inicio, fim),
        "terminaram": filtrar_periodo(terminaram, inicio, fim),
    }


# a rota ja garantiu q a trilha ta no escopo
async def obter_dashboard_trilha(db: AsyncSession, trilha_id: int, inicio: date | None,
    fim: date | None, agrupamento: Agrupamento) -> DashboardTrilhaRead:
    repo = DashboardRepository(db)
    inicio, fim, inicio_anterior, fim_anterior = await resolver_periodo(repo, inicio, fim)
    lista_conteudos = await repo.listar_conteudos_da_trilha(trilha_id)

    conteudos = []
    for conteudo, _ in lista_conteudos:
        conteudos.append(conteudo.id)

    # progresso de sempre, o periodo filtra dps
    progresso = await repo.listar_progresso_por_aluno(conteudos)
    novos, terminaram = contar_novos_e_terminaram(progresso, len(conteudos))

    contagens = await contar_linhas_trilha(repo, conteudos, novos, terminaram, inicio, fim)
    contagens_anteriores = await contar_linhas_trilha(repo, conteudos, novos, terminaram, inicio_anterior, fim_anterior)

    evolucao = []
    for ponto in montar_evolucao(contagens, inicio, fim, agrupamento):
        evolucao.append(PontoEvolucaoTrilhaRead(**ponto))

    return DashboardTrilhaRead(
        evolucao=evolucao,
        totais=await contar_totais_trilha(repo, conteudos, inicio, fim, contagens),
        totais_anteriores=await contar_totais_trilha(repo, conteudos, inicio_anterior, fim_anterior, contagens_anteriores),
        engajamento=await montar_engajamento(repo, trilha_id, progresso, sum(terminaram.values())),
        funil=await montar_funil(repo, lista_conteudos),
    )


# terminou e quem concluiu todos os conteudos atuais
async def montar_engajamento(repo: DashboardRepository, trilha_id: int,
    progresso: list[tuple[int, int, date, date]], concluiram: int) -> EngajamentoTrilhaRead:
    trilha = await repo.buscar_trilha(trilha_id)
    if trilha is not None and trilha.grupo_id is not None:
        base = await repo.contar_membros(trilha.grupo_id)
    else:
        base = await repo.contar_alunos()

    return EngajamentoTrilhaRead(base=base, iniciaram=len(progresso), concluiram=concluiram)


async def montar_funil(repo: DashboardRepository, lista_conteudos: list[tuple[Conteudo, str]]) -> list[ConteudoFunilRead]:
    ids = []
    for conteudo, _ in lista_conteudos:
        ids.append(conteudo.id)
    conclusoes = await repo.contar_conclusoes_por_conteudo(ids)

    funil = []
    for conteudo, modulo in lista_conteudos:
        funil.append(ConteudoFunilRead(
            id=conteudo.id,
            titulo=conteudo.titulo,
            tipo=conteudo.tipo.value,
            modulo=modulo,
            concluiram=conclusoes.get(conteudo.id, 0),
        ))
    return funil
