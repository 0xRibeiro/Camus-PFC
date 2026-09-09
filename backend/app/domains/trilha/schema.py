from pydantic import BaseModel, ConfigDict

from app.domains.trilha.model import ConteudoTipo


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


class ModuloCreate(BaseModel):
    titulo: str


class ModuloRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    trilha_id: int
    titulo: str
    ordem: int


class ModuloUpdate(BaseModel):
    titulo: str | None = None


class ConteudoCreate(BaseModel):
    titulo: str
    tipo: ConteudoTipo
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


class QuestaoCreate(BaseModel):
    enunciado: str


class QuestaoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    conteudo_id: int
    ordem: int
    enunciado: str


class QuestaoUpdate(BaseModel):
    enunciado: str | None = None


class AlternativaCreate(BaseModel):
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
