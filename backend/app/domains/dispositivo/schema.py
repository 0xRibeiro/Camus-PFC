from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.domains.dispositivo.model import EstadoDispositivo


# payload do topico camus/dispositivos/<mac>/status
class StatusDispositivo(BaseModel):
    estado: EstadoDispositivo

    # o offline do testamento n manda versao
    firmware: str | None = None


# camus/dispositivos/<mac>/vinculo/pedido
class PedidoVinculo(BaseModel):
    acao: Literal["gerar_codigo", "desvincular_todos"]


# camus/dispositivos/<mac>/vinculo/resposta
class RespostaVinculo(BaseModel):
    acao: Literal["gerar_codigo"] = "gerar_codigo"
    codigo: str
    expira_em: int


class RespostaDesvinculo(BaseModel):
    acao: Literal["desvincular_todos"] = "desvincular_todos"
    removidos: int


class VincularDispositivo(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    codigo: str = Field(..., min_length=6, max_length=6)


class DispositivoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    mac: str
    estado: EstadoDispositivo
    firmware: str | None
    ultimo_contato: datetime
