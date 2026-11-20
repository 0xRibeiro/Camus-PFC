from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.domains.dispositivo.model import EstadoDispositivo, TipoModulo


# payload do topico camus/dispositivos/<mac>/status
class StatusDispositivo(BaseModel):
    estado: EstadoDispositivo

    # o offline do testamento n manda versao nem rede
    firmware: str | None = None
    rede: str | None = None


# camus/dispositivos/<mac>/vinculo/pedido
class PedidoVinculo(BaseModel):
    acao: Literal["gerar_codigo", "desvincular_todos", "contar_vinculados"]


# camus/dispositivos/<mac>/vinculo/resposta
class RespostaVinculo(BaseModel):
    acao: Literal["gerar_codigo"] = "gerar_codigo"
    codigo: str
    expira_em: int


class RespostaDesvinculo(BaseModel):
    acao: Literal["desvincular_todos"] = "desvincular_todos"
    removidos: int


# dono + operadores, quem perde acesso se desvincular
class RespostaContagem(BaseModel):
    acao: Literal["contar_vinculados"] = "contar_vinculados"
    vinculados: int


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


# sem_leitura = iot desligado, erro = sensor mandou valor fora da faixa
class TrechoLeitura(BaseModel):
    inicio: datetime
    fim: datetime
    tipo: Literal["sem_leitura", "erro"]


class SerieLeitura(BaseModel):
    nome: str
    unidade: str
    # media das leituras validas por janela
    pontos: list[PontoLeitura]
    trechos: list[TrechoLeitura] = []

    # das leituras validas de vdd, n das medias
    minimo: float | None = None
    media: float | None = None
    maximo: float | None = None

    # ultima leitura de vdd
    atual: PontoLeitura | None = None
    atual_erro: bool = False


class ModuloIotRead(BaseModel):
    # None qnd e um tipo q so tem leitura antiga, nenhum modulo dele ta conectado agora
    serial: str | None
    tipo: TipoModulo
    series: list[SerieLeitura]

    # None = n tem rele
    ligado: bool | None = None

    # so aparece no historico, leituras de um modulo q ja tiraram da central
    removido: bool = False


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
    # so o dono recebe, pros outros vai None
    rede: str | None = None
    ultimo_contato: datetime
