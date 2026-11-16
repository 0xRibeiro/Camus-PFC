from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.domains.documento_legal.model import TipoDocumentoLegal


class RascunhoCreate(BaseModel):
    tipo: TipoDocumentoLegal
    conteudo: dict


class RascunhoUpdate(BaseModel):
    conteudo: dict


# sem conteudo
class DocumentoLegalResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo: TipoDocumentoLegal
    versao: int
    publicado_em: datetime | None
    criado_por: int
    autor: str
    criado_em: datetime


### publico

class DocumentoLegalPublico(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tipo: TipoDocumentoLegal
    versao: int
    conteudo: dict
    publicado_em: datetime


class DocumentoLegalHistorico(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    versao: int
    publicado_em: datetime


### aceite

class DocumentoPendente(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo: TipoDocumentoLegal
    versao: int
    publicado_em: datetime


class AceiteStatus(BaseModel):
    aceitou: bool
    pendentes: list[DocumentoPendente]


# ids q o usuario viu
class AceiteCreate(BaseModel):
    documento_ids: list[int]


class DocumentoLegalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo: TipoDocumentoLegal
    versao: int
    conteudo: dict
    publicado_em: datetime | None
    criado_por: int
    criado_em: datetime
