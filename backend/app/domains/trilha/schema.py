from pydantic import BaseModel, ConfigDict, Field

from app.domains.trilha.model import ConteudoTipo


###### schemas de trilha
class TrilhaCreate(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=100)
    descricao: str | None = None
    foto: str | None = Field(default=None, max_length=500)


class TrilhaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    titulo: str
    descricao: str | None = None
    foto: str | None = None
    is_active: bool


class TrilhaUpdate(BaseModel):
    titulo: str | None = Field(default=None, min_length=1, max_length=100)
    descricao: str | None = None
    foto: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None


###### schemas de modulo de uma trilha
class ModuloCreate(BaseModel):
    trilha_id: int
    titulo: str = Field(..., min_length=1, max_length=50)
    ordem: int = Field(..., ge=0)


class ModuloRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    trilha_id: int
    titulo: str
    ordem: int


class ModuloUpdate(BaseModel):
    titulo: str | None = Field(default=None, min_length=1, max_length=50)
    ordem: int | None = Field(default=None, ge=0)


###### schemas de conteudos de um modulo
class ConteudoCreate(BaseModel):
    modulo_id: int
    titulo: str = Field(..., min_length=1, max_length=100)
    tipo: ConteudoTipo
    ordem: int = Field(..., ge=0)
    video_url: str | None = Field(default=None, max_length=500)
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
    titulo: str | None = Field(default=None, min_length=1, max_length=100)
    ordem: int | None = Field(default=None, ge=0)
    video_url: str | None = Field(default=None, max_length=500)
    artigo_texto: str | None = None


###### schemas de questao de um conteudo quiz
class QuestaoCreate(BaseModel):
    conteudo_id: int
    ordem: int = Field(..., ge=0)
    enunciado: str = Field(..., min_length=1)


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
