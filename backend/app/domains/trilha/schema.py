from pydantic import BaseModel, ConfigDict

from app.domains.trilha.model import ConteudoTipo


###### schemas de trilha
class TrilhaCreate(BaseModel):
    titulo: str
    descricao: str | None = None


class TrilhaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    titulo: str
    descricao: str | None = None
    is_active: bool


class TrilhaUpdate(BaseModel):
    titulo: str | None = None
    descricao: str | None = None
    is_active: bool | None = None


###### schemas de modulo de uma trilha
class ModuloCreate(BaseModel):
    trilha_id: int
    titulo: str
    ordem: int


class ModuloRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    trilha_id: int
    titulo: str
    ordem: int


class ModuloUpdate(BaseModel):
    titulo: str | None = None


###### schemas de conteudos de um modulo
class ConteudoCreate(BaseModel):
    modulo_id: int
    titulo: str
    tipo: ConteudoTipo
    ordem: int
    video_url: str | None = None
    artigo_texto: str | None = None


class ConteudoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    modulo_id: int
    titulo: str
    tipo: ConteudoTipo
    ordem: int
    video_url: str | None = None
    artigo_texto: str | None = None


class ConteudoUpdate(BaseModel):
    titulo: str | None = None
    video_url: str | None = None
    artigo_texto: str | None = None


###### schemas de questao de um conteudo quiz
class QuestaoCreate(BaseModel):
    conteudo_id: int
    ordem: int
    enunciado: str


class QuestaoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    conteudo_id: int
    ordem: int
    enunciado: str


class QuestaoUpdate(BaseModel):
    enunciado: str | None = None


###### schemas de alternativas de uma questao
class AlternativaCreate(BaseModel):
    questao_id: int
    texto: str
    correta: bool = False


class AlternativaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    questao_id: int
    texto: str
    correta: bool


class AlternativaUpdate(BaseModel):
    texto: str | None = None
    correta: bool | None = None
