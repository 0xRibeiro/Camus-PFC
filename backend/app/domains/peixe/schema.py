from pydantic import BaseModel, ConfigDict, Field

from app.domains.peixe.model import Especie


class PeixeCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nome: str = Field(min_length=1, max_length=50)
    especie: Especie


class PeixeRead(PeixeCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str