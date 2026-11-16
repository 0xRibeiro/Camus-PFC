from datetime import date
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


class PontoEvolucaoTrilhaRead(BaseModel):
    data: date
    conclusoes: int
    novos: int
    terminaram: int


class TotaisTrilhaRead(BaseModel):
    alunos_ativos: int
    conclusoes: int
    novos: int
    terminaram: int


# base e membros no grupo ou alunos na global
class EngajamentoTrilhaRead(BaseModel):
    base: int
    iniciaram: int
    concluiram: int


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
