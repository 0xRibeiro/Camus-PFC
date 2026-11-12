from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints


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