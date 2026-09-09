from pydantic import BaseModel, ConfigDict


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
