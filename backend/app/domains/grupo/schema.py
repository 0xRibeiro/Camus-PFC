from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator


class GrupoCreate(BaseModel):
    # remove espaços nas pontas antes de validar o nome
    model_config = ConfigDict(str_strip_whitespace=True)

    # nome no maximo 50 ja pra evitar um sql injection por ai  :)
    nome: str = Field(..., min_length=1, max_length=50)


class GrupoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    id_dono: int
    inabilitado: bool = False
    suspenso_ate: datetime | None = None

    # um grupo que acabou de ser criado na memória ainda não recebeu o valor padrão
    @field_validator("inabilitado", mode="before")
    @classmethod
    def inabilitado_vazio_vira_false(cls, valor: bool | None) -> bool:
        return bool(valor)

    # o front lê esse campo pra decidir se mostra o aviso de grupo bloqueado.
    # a conta fica no back pra não depender da hora do navegador.
    @computed_field
    @property
    def suspenso(self) -> bool:
        if self.inabilitado:
            return True

        return self.suspenso_ate is not None and self.suspenso_ate > datetime.now(UTC)

class GrupoEntrar(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    # limitei assim o min e max pra garantir sempre ser 12
    convite: str = Field(..., min_length=12, max_length=12)


class ConviteRead(BaseModel):
    convite: str
    # to em duvida do tempo aqui, acho que uns 900 segundos é ok
    expira_em_segundos: int


class MembroGrupoRead(BaseModel):
    id: int
    username: str
    # esses papeis por enquanto só servem para distinguir quem é o dono do grupo, mas com a adição de
    # novos como moderadores, daria para ampliar o uso desses papeis.
    papel: Literal["dono", "membro"]