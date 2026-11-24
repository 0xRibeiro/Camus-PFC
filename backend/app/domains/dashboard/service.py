from datetime import date, datetime, timedelta
from statistics import median
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.dashboard.repository import DashboardRepository
from app.domains.dashboard.schema import (
    Agrupamento,
    AlternativaEscolhaRead,
    AlunoDetalheRead,
    AlunoQuizRead,
    AlunoTrilhaRead,
    ConquistaResumoRead,
    ConteudoDoAlunoRead,
    ConteudoFunilRead,
    DashboardConteudoRead,
    DashboardRead,
    DashboardTrilhaRead,
    EngajamentoTrilhaRead,
    AlternativaDoAlunoRead,
    NotaQuizRead,
    PontoEvolucaoConteudoRead,
    PontoEvolucaoRead,
    PontoEvolucaoTrilhaRead,
    QuestaoAcertoRead,
    RespostaDoAlunoRead,
    ResumoConteudoRead,
    TotaisConteudoRead,
    TotaisPeriodoRead,
    TotaisTrilhaRead,
)
from app.domains.progresso.model import TentativaQuiz
from app.domains.trilha.model import Alternativa, Conteudo, ConteudoTipo, Questao

# msm fuso dos dias da dashboard no repository
FUSO = ZoneInfo("America/Sao_Paulo")

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
        "trilhas": await repo.contar_trilhas_por_dia(inicio, fim),
        "grupos": await repo.contar_grupos_por_dia(inicio, fim),
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


# comeco do todo o periodo no admin, banco vazio comeca hj
async def buscar_inicio_do_sistema(repo: DashboardRepository) -> date:
    primeiro = await repo.buscar_primeiro_dia()
    if primeiro is None:
        return await repo.buscar_data_atual()
    return primeiro


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
        inicio_total=await buscar_inicio_do_sistema(repo),
    )


# tempo de quem terminou no periodo, mediana pra um aluno q sumiu por meses n puxar tudo
def calcular_tempo_mediano(duracoes: list[tuple[date, float]], inicio: date, fim: date) -> float | None:
    no_periodo = []
    for dia, horas in duracoes:
        if inicio <= dia <= fim:
            no_periodo.append(horas)
    if not no_periodo:
        return None
    return median(no_periodo)


# dia q cada aluno comecou e terminou (None se n terminou)
def montar_marcos(progresso: list[tuple[int, int, datetime, datetime]],
    total_conteudos: int) -> dict[int, tuple[date, date | None]]:
    marcos = {}
    for usuario_id, quantidade, primeira, ultima in progresso:
        termino = None
        if quantidade == total_conteudos:
            termino = dia_no_fuso(ultima)
        marcos[usuario_id] = (dia_no_fuso(primeira), termino)
    return marcos


# fez algo no periodo e ainda n tinha terminado a trilha no fim dele, quem comecou agr tbm conta
async def contar_em_andamento(repo: DashboardRepository, conteudos: list[int], inicio: date,
    fim: date, marcos: dict[int, tuple[date, date | None]]) -> int:
    quantidade = 0
    for usuario_id in await repo.listar_alunos_ativos(conteudos, inicio, fim):
        _, termino = marcos.get(usuario_id, (None, None))
        if termino is not None and termino <= fim:
            continue
        quantidade += 1
    return quantidade


async def contar_totais_trilha(repo: DashboardRepository, conteudos: list[int], inicio: date,
    fim: date, contagens: dict[str, dict[date, int]], duracoes: list[tuple[date, float]],
    marcos: dict[int, tuple[date, date | None]]) -> TotaisTrilhaRead:
    return TotaisTrilhaRead(
        em_andamento=await contar_em_andamento(repo, conteudos, inicio, fim, marcos),
        tempo_mediano=calcular_tempo_mediano(duracoes, inicio, fim),
        **somar_totais(contagens),
    )


def dia_no_fuso(momento: datetime) -> date:
    return momento.astimezone(FUSO).date()


# novo conta no dia da 1a conclusao, terminou no dia da ultima.
# o tempo vai da 1a ate a ultima, n tem registro de quando abriu o 1o conteudo
def contar_novos_e_terminaram(progresso: list[tuple[int, int, datetime, datetime]],
    total_conteudos: int) -> tuple[dict[date, int], dict[date, int], list[tuple[date, float]]]:
    novos: dict[date, int] = {}
    terminaram: dict[date, int] = {}
    duracoes = []
    for _, quantidade, primeira, ultima in progresso:
        primeiro_dia = dia_no_fuso(primeira)
        novos[primeiro_dia] = novos.get(primeiro_dia, 0) + 1
        if quantidade == total_conteudos:
            ultimo_dia = dia_no_fuso(ultima)
            terminaram[ultimo_dia] = terminaram.get(ultimo_dia, 0) + 1
            duracoes.append((ultimo_dia, (ultima - primeira).total_seconds() / 3600))
    return novos, terminaram, duracoes


def filtrar_periodo(por_dia: dict[date, int], inicio: date, fim: date) -> dict[date, int]:
    filtrado = {}
    for dia, quantidade in por_dia.items():
        if inicio <= dia <= fim:
            filtrado[dia] = quantidade
    return filtrado


def contar_linhas_trilha(novos: dict[date, int], terminaram: dict[date, int], inicio: date,
    fim: date) -> dict[str, dict[date, int]]:
    return {
        "novos": filtrar_periodo(novos, inicio, fim),
        "terminaram": filtrar_periodo(terminaram, inicio, fim),
    }


# cada aluno ativo no ponto entra numa coluna so: terminou ganha de comecou, q ganha de em andamento
def montar_evolucao_trilha(atividade: set[tuple[int, date]], marcos: dict[int, tuple[date, date | None]],
    inicio: date, fim: date, agrupamento: Agrupamento) -> list[PontoEvolucaoTrilhaRead]:
    comeco = {}
    termino = {}
    # o 1o ponto pode comecar antes do periodo (semana/mes), oq aconteceu antes do inicio n conta
    for usuario_id, (dia_comeco, dia_termino) in marcos.items():
        if dia_comeco >= inicio:
            comeco[usuario_id] = inicio_do_grupo(dia_comeco, agrupamento)
        if dia_termino is not None and dia_termino >= inicio:
            termino[usuario_id] = inicio_do_grupo(dia_termino, agrupamento)

    # o msm aluno em varios dias da semana conta uma vez so
    ativos_por_ponto: dict[date, set[int]] = {}
    for usuario_id, dia in atividade:
        ativos_por_ponto.setdefault(inicio_do_grupo(dia, agrupamento), set()).add(usuario_id)

    evolucao = []
    # sem linhas ele so devolve as datas de cada ponto
    for ponto in montar_evolucao({}, inicio, fim, agrupamento):
        chave = ponto["data"]
        contagem = {"comecaram": 0, "andamento": 0, "terminaram": 0}
        for usuario_id in ativos_por_ponto.get(chave, set()):
            if termino.get(usuario_id) == chave:
                contagem["terminaram"] += 1
            elif comeco.get(usuario_id) == chave:
                contagem["comecaram"] += 1
            else:
                contagem["andamento"] += 1
        evolucao.append(PontoEvolucaoTrilhaRead(data=chave, **contagem))
    return evolucao


# a rota ja garantiu q a trilha ta no escopo
async def obter_dashboard_trilha(db: AsyncSession, trilha_id: int, inicio: date | None,
    fim: date | None, agrupamento: Agrupamento) -> DashboardTrilhaRead:
    repo = DashboardRepository(db)
    trilha = await repo.buscar_trilha(trilha_id)
    if trilha is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trilha não encontrada")
    inicio, fim, inicio_anterior, fim_anterior = await resolver_periodo(repo, inicio, fim)
    lista_conteudos = await repo.listar_conteudos_da_trilha(trilha_id)

    conteudos = []
    for conteudo, _ in lista_conteudos:
        conteudos.append(conteudo.id)

    # progresso de sempre, o periodo filtra dps
    progresso = await repo.listar_progresso_por_aluno(conteudos)
    novos, terminaram, duracoes = contar_novos_e_terminaram(progresso, len(conteudos))

    contagens = contar_linhas_trilha(novos, terminaram, inicio, fim)
    contagens_anteriores = contar_linhas_trilha(novos, terminaram, inicio_anterior, fim_anterior)

    marcos = montar_marcos(progresso, len(conteudos))
    atividade = await repo.listar_dias_de_atividade(conteudos, inicio, fim)

    return DashboardTrilhaRead(
        evolucao=montar_evolucao_trilha(atividade, marcos, inicio, fim, agrupamento),
        totais=await contar_totais_trilha(repo, conteudos, inicio, fim, contagens, duracoes, marcos),
        totais_anteriores=await contar_totais_trilha(repo, conteudos, inicio_anterior, fim_anterior,
            contagens_anteriores, duracoes, marcos),
        engajamento=await montar_engajamento(repo, trilha_id, progresso, sum(terminaram.values())),
        funil=await montar_funil(repo, lista_conteudos),
        inicio_total=dia_no_fuso(trilha.criado_em),
    )


# numeros de cada quiz pra tela de gerenciar a trilha, tudo de sempre
async def resumir_conteudos(db: AsyncSession, trilha_id: int) -> list[ResumoConteudoRead]:
    repo = DashboardRepository(db)

    versoes = {}
    for conteudo, _ in await repo.listar_conteudos_da_trilha(trilha_id):
        if conteudo.tipo == ConteudoTipo.quiz:
            versoes[conteudo.id] = conteudo.versao

    # so a versao atual, subiu a versao zera ate alguem refazer
    da_versao = {}
    for quiz_id in versoes:
        da_versao[quiz_id] = []
    for tentativa in await repo.listar_tentativas_dos_quizzes(list(versoes)):
        if tentativa.versao_conteudo == versoes[tentativa.conteudo_id]:
            da_versao[tentativa.conteudo_id].append(tentativa)

    resumo = []
    for quiz_id, tentativas in da_versao.items():
        acertos = 0
        total = 0
        for tentativa in tentativas:
            acertos += tentativa.acertos
            total += tentativa.total

        acerto = None
        if total > 0:
            acerto = acertos / total

        # cada aluno tem 1 tentativa por versao, quem fez a atual é quem concluiu ela
        resumo.append(ResumoConteudoRead(id=quiz_id, concluiram=len(tentativas), acerto=acerto))
    return resumo


# terminou e quem concluiu todos os conteudos atuais
async def montar_engajamento(repo: DashboardRepository, trilha_id: int,
    progresso: list[tuple[int, int, datetime, datetime]], concluiram: int) -> EngajamentoTrilhaRead:
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


def dia_da_tentativa(tentativa: TentativaQuiz) -> date:
    return tentativa.criado_em.astimezone(FUSO).date()


# msm corte do selo de cada questao no front: abaixo de 50% mal, abaixo de 75% medio
def faixa_da_nota(tentativa: TentativaQuiz) -> str:
    acerto = tentativa.acertos / tentativa.total
    if acerto < 0.5:
        return "mal"
    if acerto < 0.75:
        return "medio"
    return "bem"


# quantos alunos de cada faixa por dia, a tentativa ja é 1 por aluno
def contar_faixas_por_dia(tentativas: list[TentativaQuiz], inicio: date,
    fim: date) -> dict[str, dict[date, int]]:
    contagens = {"mal": {}, "medio": {}, "bem": {}}
    for tentativa in tentativas:
        dia = dia_da_tentativa(tentativa)
        if inicio <= dia <= fim:
            por_dia = contagens[faixa_da_nota(tentativa)]
            por_dia[dia] = por_dia.get(dia, 0) + 1
    return contagens


def contar_totais_conteudo(tentativas: list[TentativaQuiz], inicio: date, fim: date) -> TotaisConteudoRead:
    alunos = 0
    acertos = 0
    questoes = 0
    gabaritaram = 0
    for tentativa in tentativas:
        if inicio <= dia_da_tentativa(tentativa) <= fim:
            alunos += 1
            acertos += tentativa.acertos
            questoes += tentativa.total
            if tentativa.acertos == tentativa.total:
                gabaritaram += 1

    return TotaisConteudoRead(alunos=alunos, acertos=acertos, questoes=questoes, gabaritaram=gabaritaram)


# nota de 0 ate o total, nota sem ninguem entra com 0
def montar_notas(tentativas: list[TentativaQuiz], total_questoes: int) -> list[NotaQuizRead]:
    quantidade_por_nota: dict[int, int] = {}
    for tentativa in tentativas:
        quantidade_por_nota[tentativa.acertos] = quantidade_por_nota.get(tentativa.acertos, 0) + 1

    notas = []
    for acertos in range(total_questoes + 1):
        notas.append(NotaQuizRead(acertos=acertos, quantidade=quantidade_por_nota.get(acertos, 0)))
    return notas


# conta quantas vezes cada alternativa foi marcada
async def montar_questoes(repo: DashboardRepository, conteudo_id: int,
    tentativas: list[TentativaQuiz]) -> list[QuestaoAcertoRead]:
    questoes = await repo.listar_questoes([conteudo_id])
    ids_questoes = []
    for questao in questoes:
        ids_questoes.append(questao.id)

    escolhas: dict[int, int] = {}
    for tentativa in tentativas:
        for alternativa_id in tentativa.respostas.values():
            escolhas[alternativa_id] = escolhas.get(alternativa_id, 0) + 1

    alternativas_por_questao: dict[int, list[AlternativaEscolhaRead]] = {}
    for alternativa in await repo.listar_alternativas(ids_questoes):
        alternativas_por_questao.setdefault(alternativa.questao_id, []).append(AlternativaEscolhaRead(
            id=alternativa.id,
            texto=alternativa.texto,
            correta=alternativa.correta,
            escolhas=escolhas.get(alternativa.id, 0),
        ))

    resultado = []
    for questao in questoes:
        alternativas = alternativas_por_questao.get(questao.id, [])
        respostas = 0
        acertos = 0
        for alternativa in alternativas:
            respostas += alternativa.escolhas
            if alternativa.correta:
                acertos += alternativa.escolhas

        resultado.append(QuestaoAcertoRead(
            id=questao.id,
            enunciado=questao.enunciado,
            respostas=respostas,
            acertos=acertos,
            alternativas=alternativas,
        ))
    return resultado


# a rota ja garantiu q o conteudo ta no escopo
async def obter_dashboard_conteudo(db: AsyncSession, conteudo_id: int, inicio: date | None,
    fim: date | None, agrupamento: Agrupamento) -> DashboardConteudoRead:
    repo = DashboardRepository(db)
    encontrado = await repo.buscar_conteudo(conteudo_id)
    if encontrado is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conteúdo não encontrado")
    conteudo, trilha_id = encontrado

    # artigo e video so tem concluiu ou n, isso fica pra dashboard da trilha
    if conteudo.tipo != ConteudoTipo.quiz:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Só quiz tem dashboard")

    inicio, fim, inicio_anterior, fim_anterior = await resolver_periodo(repo, inicio, fim)
    tentativas = await repo.listar_tentativas_da_versao(conteudo_id, conteudo.versao)

    evolucao = []
    for ponto in montar_evolucao(contar_faixas_por_dia(tentativas, inicio, fim), inicio, fim, agrupamento):
        evolucao.append(PontoEvolucaoConteudoRead(**ponto))

    # notas e questoes tbm so do periodo, igual o resto da tela
    no_periodo = []
    for tentativa in tentativas:
        if inicio <= dia_da_tentativa(tentativa) <= fim:
            no_periodo.append(tentativa)

    questoes = await montar_questoes(repo, conteudo_id, no_periodo)

    return DashboardConteudoRead(
        inicio_total=dia_no_fuso(conteudo.criado_em),
        versao=conteudo.versao,
        versao_desde=dia_no_fuso(conteudo.versao_desde),
        titulo=conteudo.titulo,
        trilha_id=trilha_id,
        evolucao=evolucao,
        totais=contar_totais_conteudo(tentativas, inicio, fim),
        totais_anteriores=contar_totais_conteudo(tentativas, inicio_anterior, fim_anterior),
        notas=montar_notas(no_periodo, len(questoes)),
        questoes=questoes,
    )


########## alunos da trilha de grupo

# so trilha de grupo mostra o aluno, na global o autor n tem relacao com quem faz
async def buscar_grupo_da_trilha(repo: DashboardRepository, trilha_id: int) -> int:
    trilha = await repo.buscar_trilha(trilha_id)
    if trilha is None or trilha.grupo_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Só trilha de grupo mostra os alunos")
    return trilha.grupo_id


async def listar_alunos_da_trilha(db: AsyncSession, trilha_id: int) -> list[AlunoTrilhaRead]:
    repo = DashboardRepository(db)
    grupo_id = await buscar_grupo_da_trilha(repo, trilha_id)

    conteudos = []
    for conteudo, _ in await repo.listar_conteudos_da_trilha(trilha_id):
        conteudos.append(conteudo.id)

    # {aluno: (quantos concluiu, ultima conclusao)}
    progresso = {}
    for usuario_id, quantidade, _, ultima in await repo.listar_progresso_por_aluno(conteudos):
        progresso[usuario_id] = (quantidade, ultima)

    alunos = []
    for membro in await repo.listar_membros(grupo_id):
        quantidade, ultima = progresso.get(membro.id, (0, None))
        alunos.append(AlunoTrilhaRead(
            id=membro.id,
            username=membro.username,
            avatar=membro.avatar,
            cor_fundo=membro.cor_fundo,
            concluidos=quantidade,
            total=len(conteudos),
            ultima_atividade=ultima,
        ))
    return alunos


# o q o aluno marcou em cada questao, so da pra montar na versao atual (as antigas foram editadas)
def montar_respostas(questoes: list[Questao], respostas: dict,
    alternativas_por_questao: dict[int, list[Alternativa]]) -> list[RespostaDoAlunoRead]:
    lista = []
    for questao in questoes:
        # chave do json vem como texto, sem resposta fica None
        escolhida_id = respostas.get(str(questao.id))
        acertou = False
        alternativas = []
        for alternativa in alternativas_por_questao.get(questao.id, []):
            escolhida = alternativa.id == escolhida_id
            if escolhida and alternativa.correta:
                acertou = True
            alternativas.append(AlternativaDoAlunoRead(
                id=alternativa.id,
                texto=alternativa.texto,
                correta=alternativa.correta,
                escolhida=escolhida,
            ))

        lista.append(RespostaDoAlunoRead(
            id=questao.id,
            enunciado=questao.enunciado,
            acertou=acertou,
            alternativas=alternativas,
        ))
    return lista


# tentativa da versao atual, se ele so fez uma antiga pega a mais nova q tiver
def escolher_tentativa(tentativas: list[TentativaQuiz], versao_atual: int) -> TentativaQuiz | None:
    escolhida = None
    for tentativa in tentativas:
        if tentativa.versao_conteudo == versao_atual:
            return tentativa
        if escolhida is None or tentativa.versao_conteudo > escolhida.versao_conteudo:
            escolhida = tentativa
    return escolhida


async def obter_aluno_da_trilha(db: AsyncSession, trilha_id: int, usuario_id: int) -> AlunoDetalheRead:
    repo = DashboardRepository(db)
    grupo_id = await buscar_grupo_da_trilha(repo, trilha_id)
    membro = await repo.buscar_membro(grupo_id, usuario_id)
    if membro is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado nesse grupo")

    lista_conteudos = await repo.listar_conteudos_da_trilha(trilha_id)
    conteudos = []
    quizzes = []
    for conteudo, _ in lista_conteudos:
        conteudos.append(conteudo.id)
        if conteudo.tipo == ConteudoTipo.quiz:
            quizzes.append(conteudo.id)

    conclusoes = {}
    for conclusao in await repo.listar_conclusoes_do_aluno(usuario_id, conteudos):
        conclusoes[conclusao.conteudo_id] = conclusao

    tentativas_por_quiz: dict[int, list[TentativaQuiz]] = {}
    for tentativa in await repo.listar_tentativas_do_aluno(usuario_id, quizzes):
        tentativas_por_quiz.setdefault(tentativa.conteudo_id, []).append(tentativa)

    questoes_por_quiz: dict[int, list[Questao]] = {}
    ids_questoes = []
    for questao in await repo.listar_questoes(quizzes):
        questoes_por_quiz.setdefault(questao.conteudo_id, []).append(questao)
        ids_questoes.append(questao.id)

    alternativas_por_questao: dict[int, list[Alternativa]] = {}
    for alternativa in await repo.listar_alternativas(ids_questoes):
        alternativas_por_questao.setdefault(alternativa.questao_id, []).append(alternativa)

    itens = []
    ultima = None
    for conteudo, modulo in lista_conteudos:
        conclusao = conclusoes.get(conteudo.id)
        item = ConteudoDoAlunoRead(id=conteudo.id, titulo=conteudo.titulo, tipo=conteudo.tipo.value, modulo=modulo)
        if conclusao is not None:
            item.concluido_em = conclusao.concluido_em
            if ultima is None or conclusao.concluido_em > ultima:
                ultima = conclusao.concluido_em

        tentativa = escolher_tentativa(tentativas_por_quiz.get(conteudo.id, []), conteudo.versao)
        if tentativa is not None:
            item.acertos = tentativa.acertos
            item.questoes = tentativa.total
            if tentativa.versao_conteudo != conteudo.versao:
                item.versao_antiga = True
            else:
                item.respostas = montar_respostas(questoes_por_quiz.get(conteudo.id, []), tentativa.respostas,
                    alternativas_por_questao)
        itens.append(item)

    return AlunoDetalheRead(
        id=membro.id,
        username=membro.username,
        avatar=membro.avatar,
        cor_fundo=membro.cor_fundo,
        concluidos=len(conclusoes),
        total=len(conteudos),
        ultima_atividade=ultima,
        conteudos=itens,
    )


# membros q fizeram, com a nota e as respostas desse quiz. de sempre e n do periodo
async def listar_alunos_do_quiz(db: AsyncSession, conteudo_id: int) -> list[AlunoQuizRead]:
    repo = DashboardRepository(db)
    encontrado = await repo.buscar_conteudo(conteudo_id)
    if encontrado is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conteúdo não encontrado")
    conteudo, trilha_id = encontrado
    if conteudo.tipo != ConteudoTipo.quiz:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Só quiz tem dashboard")
    grupo_id = await buscar_grupo_da_trilha(repo, trilha_id)

    tentativas_por_aluno: dict[int, list[TentativaQuiz]] = {}
    for tentativa in await repo.listar_tentativas_dos_quizzes([conteudo_id]):
        tentativas_por_aluno.setdefault(tentativa.usuario_id, []).append(tentativa)

    questoes = await repo.listar_questoes([conteudo_id])
    ids_questoes = []
    for questao in questoes:
        ids_questoes.append(questao.id)

    alternativas_por_questao: dict[int, list[Alternativa]] = {}
    for alternativa in await repo.listar_alternativas(ids_questoes):
        alternativas_por_questao.setdefault(alternativa.questao_id, []).append(alternativa)

    alunos = []
    for membro in await repo.listar_membros(grupo_id):
        tentativa = escolher_tentativa(tentativas_por_aluno.get(membro.id, []), conteudo.versao)
        if tentativa is None:
            continue

        aluno = AlunoQuizRead(
            id=membro.id,
            username=membro.username,
            avatar=membro.avatar,
            cor_fundo=membro.cor_fundo,
            concluido_em=tentativa.criado_em,
            acertos=tentativa.acertos,
            questoes=tentativa.total,
        )
        if tentativa.versao_conteudo != conteudo.versao:
            aluno.versao_antiga = True
        else:
            aluno.respostas = montar_respostas(questoes, tentativa.respostas, alternativas_por_questao)
        alunos.append(aluno)
    return alunos
