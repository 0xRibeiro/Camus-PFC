import secrets
from datetime import UTC, datetime

from fastapi import HTTPException, status
from fastcrud.exceptions.http_exceptions import NotFoundException
from influxdb_client import Point
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import dynsec
from app.core.redis import redis_client
from app.domains.dispositivo.model import Dispositivo, ModuloIot
from app.domains.dispositivo.repository import DispositivoRepository, LeituraRepository
from app.domains.dispositivo.schema import (
    CadastroDispositivo,
    CredencialDispositivo,
    LeituraModulo,
    ListaModulos,
    ModuloIotRead,
    PontoLeitura,
    RespostaDesvinculo,
    RespostaVinculo,
    SerieLeitura,
    StatusDispositivo,
)

CODIGO_VALIDADE_SEGUNDOS = 300


# dispositivo nasce no cadastro do script, aqui so atualiza
async def registrar_status(db: AsyncSession, mac: str, status: StatusDispositivo) -> Dispositivo | None:
    repo = DispositivoRepository(db)
    dispositivo = await repo.buscar_por_mac(mac)

    if dispositivo is None:
        return None

    dispositivo.estado = status.estado
    dispositivo.ultimo_contato = datetime.now(UTC)

    # offline n manda versao, mantem a ultima
    if status.firmware is not None:
        dispositivo.firmware = status.firmware

    return await repo.salvar(dispositivo)


# cria a conta no broker (ou troca a senha) e a linha no banco
async def cadastrar(db: AsyncSession, data: CadastroDispositivo) -> CredencialDispositivo:
    senha = secrets.token_urlsafe(24)

    try:
        await dynsec.cadastrar_dispositivo(data.mac, senha)
    except (dynsec.ErroDynsec, TimeoutError) as erro:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, f"Broker não cadastrou o dispositivo: {erro}")

    repo = DispositivoRepository(db)
    if await repo.buscar_por_mac(data.mac) is None:
        await repo.salvar(Dispositivo(mac=data.mac))

    return CredencialDispositivo(mac=data.mac, senha=senha)


async def gerar_codigo(mac: str) -> RespostaVinculo:
    while True:
        codigo = f"{secrets.randbelow(1_000_000):06d}"

        # nx: so grava se o codigo n estiver em uso
        gravou = await redis_client.set(f"dispositivo:codigo:{codigo}", mac, ex=CODIGO_VALIDADE_SEGUNDOS, nx=True)
        if gravou:
            return RespostaVinculo(codigo=codigo, expira_em=CODIGO_VALIDADE_SEGUNDOS)


# usado pelo aquario pra conectar e pra entrar com codigo
async def buscar_por_codigo(db: AsyncSession, codigo: str) -> Dispositivo:
    mac = await redis_client.get(f"dispositivo:codigo:{codigo}")

    if mac is None:
        raise NotFoundException("Código inválido ou expirou")

    dispositivo = await DispositivoRepository(db).buscar_por_mac(mac)

    if dispositivo is None:
        raise NotFoundException("Dispositivo não encontrado")

    return dispositivo


async def apagar_codigo(codigo: str) -> None:
    await redis_client.delete(f"dispositivo:codigo:{codigo}")


# tira o esp do aquario e os operadores saem junto
async def tirar_do_aquario(db: AsyncSession, dispositivo: Dispositivo) -> int:
    if dispositivo.id_aquario is None:
        return 0

    repo = DispositivoRepository(db)
    removidos = await repo.remover_operadores(dispositivo.id_aquario)
    dispositivo.id_aquario = None
    await repo.salvar(dispositivo)
    return removidos


async def desvincular_todos(db: AsyncSession, mac: str) -> RespostaDesvinculo:
    dispositivo = await DispositivoRepository(db).buscar_por_mac(mac)

    if dispositivo is None:
        return RespostaDesvinculo(removidos=0)

    removidos = await tirar_do_aquario(db, dispositivo)
    return RespostaDesvinculo(removidos=removidos)


# o q n veio na lista fica sem dispositivo
async def registrar_modulos(db: AsyncSession, mac: str, lista: ListaModulos) -> None:
    repo = DispositivoRepository(db)
    dispositivo = await repo.buscar_por_mac(mac)

    if dispositivo is None:
        return

    agora = datetime.now(UTC)
    alterados = []
    seriais = set()

    for item in lista.modulos:
        seriais.add(item.serial)
        modulo = await repo.buscar_modulo(item.serial)

        if modulo is None:
            modulo = ModuloIot(serial=item.serial)

        modulo.tipo = item.tipo
        modulo.id_dispositivo = dispositivo.id
        modulo.ultimo_contato = agora
        alterados.append(modulo)

    for modulo in await repo.listar_modulos(dispositivo.id):
        if modulo.serial not in seriais:
            modulo.id_dispositivo = None
            alterados.append(modulo)

    await repo.salvar_modulos(alterados)


async def gravar_leitura(mac: str, leitura: LeituraModulo) -> None:
    pontos = []
    for item in leitura.leituras:
        ponto = (
            Point("leitura")
            .tag("dispositivo", mac)
            .tag("modulo", leitura.serial)
            .tag("tipo", str(leitura.tipo.value))
            .tag("nome", item.nome)
            .tag("unidade", item.unidade)
            .field("valor", item.valor)
        )
        pontos.append(ponto)

    await LeituraRepository().gravar(pontos)


# junta os pontos do influx por modulo e por nome da leitura
async def listar_modulos(db: AsyncSession, dispositivo: Dispositivo, minutos: int) -> list[ModuloIotRead]:
    series: dict[str, dict[str, SerieLeitura]] = {}

    for registro in await LeituraRepository().listar_do_dispositivo(dispositivo.mac, minutos):
        serial = registro.values["modulo"]
        nome = registro.values["nome"]

        if serial not in series:
            series[serial] = {}

        if nome not in series[serial]:
            series[serial][nome] = SerieLeitura(nome=nome, unidade=registro.values["unidade"], pontos=[])

        series[serial][nome].pontos.append(PontoLeitura(tempo=registro.get_time(), valor=registro.get_value()))

    modulos = []
    for modulo in await DispositivoRepository(db).listar_modulos(dispositivo.id):
        series_do_modulo = []
        for serie in series.get(modulo.serial, {}).values():
            series_do_modulo.append(serie)

        modulos.append(ModuloIotRead(serial=modulo.serial, tipo=modulo.tipo, series=series_do_modulo))
    return modulos
