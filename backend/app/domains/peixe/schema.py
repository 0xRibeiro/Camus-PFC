from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.domains.peixe.model import Especie


class PeixeCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nome: str = Field(min_length=1, max_length=50)
    especie: Literal[
        Especie.DOURADO,
        Especie.BETTA,
        Especie.PALHACO,
        Especie.ANJO,
        Especie.NEON,
    ]


class PeixeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    especie: Especie