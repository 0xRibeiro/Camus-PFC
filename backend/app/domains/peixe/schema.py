from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

Apelido = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]


class PeixeCreate(BaseModel):
    taxon_id: int = Field(gt=0)
    quantidade: int = Field(default=1, ge=1, le=999)
    apelido: Apelido | None = None

    @model_validator(mode="after")
    def apelido_so_com_um(self) -> Self:
        if self.apelido is not None and self.quantidade > 1:
            raise ValueError("Só dá pra dar nome quando é 1 peixe")
        return self


# nome so vale qnd o resultado e 1 peixe (regra fica no service)
class PeixeUpdate(BaseModel):
    quantidade: int | None = Field(default=None, ge=1, le=999)
    apelido: Apelido | None = None


class PeixeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    taxon_id: int
    nome_popular: str
    nome_cientifico: str
    foto_url: str | None
    foto_credito: str | None
    quantidade: int
    apelido: str | None
