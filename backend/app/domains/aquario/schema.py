from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from app.domains.aquario.model import PapelAquario
from app.domains.dispositivo.schema import DispositivoRead


class AquarioCreate(BaseModel):
    # usa annoted para ajudar a validar o campo, tirando espaços e limitando o tamanho
    nome: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]
    litros: int | None = Field(default=None, gt=0)


# aqui não retorna o id do dono porque não precisa disso no front
class AquarioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    litros: int | None

    # padrao bate com o aquario recem criado
    papel: PapelAquario = PapelAquario.dono
    dispositivo: DispositivoRead | None = None


class MembroAquarioRead(BaseModel):
    username: str
    papel: PapelAquario


class ConviteAquarioRead(BaseModel):
    convite: str
    expira_em_segundos: int


class AquarioEntrar(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    convite: str = Field(..., min_length=12, max_length=12)