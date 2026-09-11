from pydantic import BaseModel, ConfigDict


class ConquistaCreate(BaseModel):
	titulo: str
	descricao: str | None = None


class ConquistaRead(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: int
	titulo: str
	descricao: str | None = None
	desbloquada: bool


class ConquistaUpdate(BaseModel):
	titulo: str | None = None
	descricao: str | None = None
	desbloquada: bool | None = None
