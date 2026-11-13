from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.domains.dispositivo.model import EstadoDispositivo, TipoModulo


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


class CadastroDispositivo(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    # mac minusculo sem ":", igual no topico
    mac: str = Field(..., pattern=r"^[0-9a-f]{12}$")


# a senha so aparece aqui, depois so o hash no broker
class CredencialDispositivo(BaseModel):
    mac: str
    senha: str


class CodigoDispositivo(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    codigo: str = Field(..., min_length=6, max_length=6)


# camus/dispositivos/<mac>/modulos
class ModuloPayload(BaseModel):
    serial: str
    tipo: TipoModulo
    endereco: int

    # so vem nos atuadores
    ligado: bool | None = None


class ListaModulos(BaseModel):
    modulos: list[ModuloPayload]


# camus/dispositivos/<mac>/leituras
class LeituraPayload(BaseModel):
    nome: str
    valor: float
    unidade: str


class LeituraModulo(BaseModel):
    serial: str
    tipo: TipoModulo
    leituras: list[LeituraPayload]


class PontoLeitura(BaseModel):
    tempo: datetime
    valor: float


class SerieLeitura(BaseModel):
    nome: str
    unidade: str
    pontos: list[PontoLeitura]


class ModuloIotRead(BaseModel):
    serial: str
    tipo: TipoModulo
    series: list[SerieLeitura]

    # None = n tem rele
    ligado: bool | None = None


# body da rota de comando
class ComandoModulo(BaseModel):
    acao: Literal["ativar", "desativar"]


# camus/dispositivos/<mac>/comandos
class ComandoPayload(BaseModel):
    serial: str
    acao: Literal["ativar", "desativar"]


class DispositivoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    mac: str
    estado: EstadoDispositivo
    firmware: str | None
    ultimo_contato: datetime
