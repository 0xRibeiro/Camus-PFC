from pydantic import BaseModel, ConfigDict, Field


class GrupoCreate(BaseModel):
    # remove espaços nas pontas antes de validar o nome
    model_config = ConfigDict(str_strip_whitespace=True)

    # nome no maximo 50 ja pra evitar um sql injection por ai  :)
    nome: str = Field(..., min_length=1, max_length=50)


class GrupoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    id_dono: int


class GrupoEntrar(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    # limitei assim o min e max pra garantir sempre ser 12
    convite: str = Field(..., min_length=12, max_length=12)


class ConviteRead(BaseModel):
    convite: str
    # to em duvida do tempo aqui, acho que uns 900 segundos é ok
    expira_em_segundos: int