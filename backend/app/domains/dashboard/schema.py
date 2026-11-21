from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel

Agrupamento = Literal["dia", "semana", "mes"]


# um ponto do grafico, data e o comeco do dia/semana/mes
class PontoEvolucaoRead(BaseModel):
    data: date
    alunos: int
    dispositivos: int
    trilhas: int
    grupos: int


class TotaisPeriodoRead(BaseModel):
    alunos: int
    dispositivos: int
    trilhas: int
    grupos: int


# cada aluno ativo no ponto entra numa coluna so, a altura é o total de ativos
class PontoEvolucaoTrilhaRead(BaseModel):
    data: date
    comecaram: int
    andamento: int
    terminaram: int


# novo = concluiu o 1o conteudo, terminou = concluiu todos
class TotaisTrilhaRead(BaseModel):
    # ativo no periodo q ainda n tinha terminado a trilha no fim dele
    em_andamento: int
    novos: int
    terminaram: int
    # mediana em horas de quem terminou no periodo, None se ngm terminou
    tempo_mediano: float | None = None


# base e membros no grupo ou alunos na global
class EngajamentoTrilhaRead(BaseModel):
    base: int
    iniciaram: int
    concluiram: int


# so trilha de grupo, cada membro com quanto ja fez
class AlunoTrilhaRead(BaseModel):
    id: int
    username: str
    avatar: str
    cor_fundo: str
    concluidos: int
    total: int
    # None se n comecou
    ultima_atividade: datetime | None = None


class AlternativaDoAlunoRead(BaseModel):
    id: int
    texto: str
    correta: bool
    escolhida: bool


# cada questao do quiz com o q o aluno marcou
class RespostaDoAlunoRead(BaseModel):
    id: int
    enunciado: str
    acertou: bool
    alternativas: list[AlternativaDoAlunoRead]


class ConteudoDoAlunoRead(BaseModel):
    id: int
    titulo: str
    tipo: str
    modulo: str
    concluido_em: datetime | None = None
    # so no quiz q ele fez
    acertos: int | None = None
    questoes: int | None = None
    # fez uma versao antiga, a nota vale mas as questoes mudaram
    versao_antiga: bool = False
    # vazio na versao antiga
    respostas: list[RespostaDoAlunoRead] = []


class AlunoDetalheRead(AlunoTrilhaRead):
    conteudos: list[ConteudoDoAlunoRead]


# numeros q aparecem do lado de cada quiz na tela da trilha, de sempre e n do periodo
class ResumoConteudoRead(BaseModel):
    id: int
    concluiram: int
    # de 0 a 1 na versao atual. None se ngm fez ainda
    acerto: float | None = None


class ConteudoFunilRead(BaseModel):
    id: int
    titulo: str
    tipo: str
    modulo: str
    concluiram: int


class DashboardTrilhaRead(BaseModel):
    evolucao: list[PontoEvolucaoTrilhaRead]
    totais: TotaisTrilhaRead
    totais_anteriores: TotaisTrilhaRead

    # esses dois sao de sempre, n do periodo
    engajamento: EngajamentoTrilhaRead
    funil: list[ConteudoFunilRead]

    # dia q a trilha foi criada, comeco do todo o periodo
    inicio_total: date


# quantos alunos fizeram o quiz no dia, separados pela faixa da nota
class PontoEvolucaoConteudoRead(BaseModel):
    data: date
    mal: int
    medio: int
    bem: int


# 1 tentativa por aluno na versao atual
class TotaisConteudoRead(BaseModel):
    alunos: int
    acertos: int
    questoes: int
    gabaritaram: int


# quantos alunos tiraram essa nota
class NotaQuizRead(BaseModel):
    acertos: int
    quantidade: int


class AlternativaEscolhaRead(BaseModel):
    id: int
    texto: str
    correta: bool
    escolhas: int


class QuestaoAcertoRead(BaseModel):
    id: int
    enunciado: str
    respostas: int
    acertos: int
    alternativas: list[AlternativaEscolhaRead]


# so quiz tem, tudo da versao atual e do periodo
class DashboardConteudoRead(BaseModel):
    titulo: str
    trilha_id: int

    # dia q o quiz foi criado, comeco do todo o periodo
    inicio_total: date
    versao: int
    versao_desde: date

    evolucao: list[PontoEvolucaoConteudoRead]
    totais: TotaisConteudoRead
    totais_anteriores: TotaisConteudoRead

    notas: list[NotaQuizRead]
    questoes: list[QuestaoAcertoRead]


# para saber quanto cada conquista foi concedida
class ConquistaResumoRead(BaseModel):
    id: int
    titulo: str
    imagem_dir: str
    quantidade: int


class DashboardRead(BaseModel):
    evolucao: list[PontoEvolucaoRead]
    totais: TotaisPeriodoRead
    # msm tamanho de periodo logo antes, pro %
    totais_anteriores: TotaisPeriodoRead

    conquistas_por_quantidade: list[ConquistaResumoRead]
    # base da % das conquistas
    total_alunos: int

    # mais dados pra dash, diferenciando entre os tipos de trilhas
    total_trilhas_globais: int
    total_trilhas_de_grupo: int

    # 1o registro do sistema, comeco do todo o periodo
    inicio_total: date
