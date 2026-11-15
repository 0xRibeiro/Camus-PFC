from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# motivos e status que a api aceita. pra ter um motivo novo, inclui aqui e no front tbm.
Motivo = Literal["conteudo_improprio", "assedio", "spam", "outro"]
StatusDenuncia = Literal["pendente", "resolvida", "rejeitada"]


class DenunciaCreate(BaseModel):
    # tira os espaços do começo e do fim antes de validar
    model_config = ConfigDict(str_strip_whitespace=True)

    motivo: Motivo
    descricao: str | None = Field(default=None, max_length=500)
    # se não vier id_conteudo, a denúncia é contra o grupo (quer dizer, o dono)
    id_conteudo: int | None = None


class DenunciaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    id_grupo: int
    id_conteudo: int | None
    motivo: str
    descricao: str | None
    status: StatusDenuncia
    criado_em: datetime
    resolvido_em: datetime | None


# o que o admin recebe: nomes no lugar de só os ids
class DenunciaAdminRead(DenunciaRead):
    denunciante: str
    grupo: str
    dono: str
    conteudo: str | None
    # o front usa isso pra esconder o suspender quando o grupo já está suspenso
    grupo_suspenso: bool = False


class DenunciaUpdate(BaseModel):
    # admin só fecha a denúncia (resolvida ou rejeitada), pendente é como ela já nasce
    status: Literal["resolvida", "rejeitada"]