from pydantic import BaseModel, ConfigDict


class ConquistaCreate(BaseModel):
	titulo: str
	descricao: str | None = None


class ConquistaRead(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: int
	titulo: str
	descricao: str | None = None


class ConquistaUpdate(BaseModel):
	titulo: str | None = None
	descricao: str | None = None


# abaixo são os schemas da tabela associativa. não tenho certeza se é necessário
# ou recomendado ter todos esses metodos pra ela, mas manterei por enquanto e deleterei
# caso seja necessario.

class associacao_conquista_usuarioCreate(BaseModel):
	usuario_id: int
	conquista_id: int

class associacao_conquista_usuarioRead(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	usuario_id: int
	conquista_id: int

class associacao_conquista_usuarioUpdate(BaseModel):
	usuario_id: int | None = None
	conquista_id: int | None = None
