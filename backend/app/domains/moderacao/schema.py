from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SuspensaoCreate(BaseModel):
    # tira os espaços das pontas antes de validar o motivo
    model_config = ConfigDict(str_strip_whitespace=True)

    # o admin escolhe entre dois prazos, contados em dias
    dias: Literal[14, 30]

    # o dono do grupo lê esse motivo no aviso que recebe
    motivo: str = Field(..., min_length=5, max_length=500)


class MotivoCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    # serve pra excluir um grupo ou um conteúdo
    motivo: str = Field(..., min_length=5, max_length=500)