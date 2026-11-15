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


class ResultadoRead(BaseModel):
    acertou: bool
    resposta_taxon_id: int
    resposta_nome: str
    resposta_nome_cientifico: str
    pontos: int
    acertos_com_xp_hoje: int
    limite_acertos_com_xp: int
