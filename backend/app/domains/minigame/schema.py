from typing import Literal

from pydantic import BaseModel


class OpcaoRead(BaseModel):
    taxon_id: int
    nome: str


# vai pro front sem a resposta certa
class RodadaRead(BaseModel):
    id: int
    foto_url: str
    foto_atribuicao: str
    opcoes: list[OpcaoRead]
    acertos_com_xp_hoje: int
    limite_acertos_com_xp: int


class RespostaInput(BaseModel):
    taxon_id: int


class EspecieComparadaRead(BaseModel):
    taxon_id: int
    nome: str
    foto_url: str
    foto_atribuicao: str
    # o do desafiante so vem dps de responder
    registros: int | None = None


class RodadaMaisOuMenosRead(BaseModel):
    id: int
    base: EspecieComparadaRead
    desafiante: EspecieComparadaRead
    sequencia: int
    recorde: int
    sequencia_para_combo: int
    acertos_com_xp_hoje: int
    limite_acertos_com_xp: int


class PalpiteInput(BaseModel):
    palpite: Literal["mais", "menos"]


class ResultadoMaisOuMenosRead(BaseModel):
    acertou: bool
    registros_desafiante: int
    nome_cientifico_desafiante: str
    pontos: int
    combo: bool
    sequencia: int
    recorde: int
    acertos_com_xp_hoje: int
    limite_acertos_com_xp: int


class ResultadoRead(BaseModel):
    acertou: bool
    resposta_taxon_id: int
    resposta_nome: str
    resposta_nome_cientifico: str
    pontos: int
    acertos_com_xp_hoje: int
    limite_acertos_com_xp: int
