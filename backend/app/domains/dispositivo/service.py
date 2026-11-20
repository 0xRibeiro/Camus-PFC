import secrets
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from fastcrud.exceptions.http_exceptions import NotFoundException
from influxdb_client import Point
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import dynsec
from app.core.mqtt import mqtt
from app.core.redis import redis_client
from app.domains.dispositivo.model import Dispositivo, EstadoDispositivo, ModuloIot
from app.domains.dispositivo.repository import DispositivoRepository, LeituraRepository
from app.domains.dispositivo.schema import (
    CadastroDispositivo,
    ComandoModulo,
    ComandoPayload,
    CredencialDispositivo,
    LeituraModulo,
    ListaModulos,
    IntervaloLigado,
    ModuloIotRead,
    PontoLeitura,
    RespostaContagem,
    RespostaDesvinculo,
    RespostaVinculo,
    SerieLeitura,
    StatusDispositivo,
    TrechoLeitura,
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

    # offline n manda versao nem rede, mantem a ultima
    if status.firmware is not None:
        dispositivo.firmware = status.firmware
    if status.rede is not None:
        dispositivo.rede = status.rede

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


# +1 do dono, esp fora de aquario n tem ninguem
async def contar_vinculados(db: AsyncSession, mac: str) -> RespostaContagem:
    repo = DispositivoRepository(db)
    dispositivo = await repo.buscar_por_mac(mac)

    if dispositivo is None or dispositivo.id_aquario is None:
        return RespostaContagem(vinculados=0)

    operadores = await repo.contar_operadores(dispositivo.id_aquario)
    return RespostaContagem(vinculados=operadores + 1)


# o q n veio na lista fica sem dispositivo
async def registrar_modulos(db: AsyncSession, mac: str, lista: ListaModulos) -> None:
    repo = DispositivoRepository(db)
    dispositivo = await repo.buscar_por_mac(mac)

    if dispositivo is None:
        return

    agora = datetime.now(UTC)
    alterados = []
    seriais = set()
    # mudancas do rele vao pro influx, pro grafico mostrar qnd o aquecedor ficou ligado
    mudancas_rele = []

    for item in lista.modulos:
        seriais.add(item.serial)
        modulo = await repo.buscar_modulo(item.serial)

        if modulo is None:
            modulo = ModuloIot(serial=item.serial)

        if item.ligado is not None and item.ligado != modulo.ligado:
            mudancas_rele.append(ponto_rele(mac, item.serial, item.tipo, item.ligado, agora))

        modulo.tipo = item.tipo
        modulo.ligado = item.ligado
        modulo.id_dispositivo = dispositivo.id
        modulo.ultimo_contato = agora
        alterados.append(modulo)

    for modulo in await repo.listar_modulos(dispositivo.id):
        if modulo.serial not in seriais:
            # tiraram o modulo com o rele ligado, o aquecedor desligou junto
            if modulo.ligado:
                mudancas_rele.append(ponto_rele(mac, modulo.serial, modulo.tipo, False, agora))
            modulo.id_dispositivo = None
            alterados.append(modulo)

    await repo.salvar_modulos(alterados)
    if mudancas_rele:
        await LeituraRepository().gravar(mudancas_rele)


def ponto_rele(mac: str, serial: str, tipo: int, ligado: bool, tempo: datetime) -> Point:
    return (
        Point("rele")
        .tag("dispositivo", mac)
        .tag("modulo", serial)
        .tag("tipo", str(int(tipo)))
        .field("ligado", ligado)
        .time(tempo)
    )


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


###### leituras validas

# faixa q cada sensor consegue medir, fora disso e erro de leitura
LIMITES_LEITURA = {
    "distancia": (2, 400),
    "temperatura": (-55, 125),
    "tds": (0, 1000),
    "turbidez": (0, 3000),
}

# ds18b20 manda 85 cravado qnd a leitura falha
TEMPERATURA_ERRO = 85.0

# buraco menor q isso e atraso normal do esp, n desligado
SEM_LEITURA_MINIMO = timedelta(seconds=30)


def leitura_valida(nome: str, valor: float) -> bool:
    if nome == "temperatura" and valor == TEMPERATURA_ERRO:
        return False
    if nome not in LIMITES_LEITURA:
        return True

    minimo, maximo = LIMITES_LEITURA[nome]
    return minimo <= valor <= maximo


# msm regra do leitura_valida, escrita em flux pra rodar dentro do influx
def condicao_valida_flux() -> str:
    invalido = f'(r.nome == "temperatura" and r._value == {TEMPERATURA_ERRO})'
    for nome, (minimo, maximo) in LIMITES_LEITURA.items():
        invalido += f' or (r.nome == "{nome}" and (r._value < {float(minimo)} or r._value > {float(maximo)}))'
    return f"not ({invalido})"


###### series

# dia do grafico comeca na meia-noite daqui. o influx do nix n tem os fusos instalados,
# entao vai so a diferenca pra utc, q no brasil e fixa desde q acabou o horario de verao
FUSO = ZoneInfo("America/Sao_Paulo")


# meia-noite daqui e 03:00 utc, entao empurra as janelas 3h
def deslocamento_fuso() -> int:
    diferenca = datetime.now(FUSO).utcoffset() or timedelta()
    return int(-diferenca.total_seconds())

# influx so guarda 30 dias, folga de 1 dia pro "ultimos 30 dias" do calendario
PERIODO_MAXIMO = timedelta(days=31)


# 1h vai cru de 5 em 5s, o resto em uns 360 pontos. hora e dia e a pessoa q escolhe
def calcular_janela(inicio: datetime, fim: datetime, agrupamento: str) -> int:
    if agrupamento == "hora":
        return 3600
    if agrupamento == "dia":
        return 86400

    segundos = int((fim - inicio).total_seconds())
    if segundos <= 3600:
        return 5
    return max(5, segundos // 360)


# series ficam por tipo de modulo, n por serial, a consulta ja junta os modulos do msm tipo
def serie_do_registro(series: dict[int, dict[str, SerieLeitura]], registro) -> SerieLeitura:
    tipo = int(registro.values["tipo"])
    nome = registro.values["nome"]

    if tipo not in series:
        series[tipo] = {}
    if nome not in series[tipo]:
        series[tipo][nome] = SerieLeitura(nome=nome, unidade=registro.values["unidade"], pontos=[])
    return series[tipo][nome]


# janela vazia vira trecho, emendando as vizinhas do msm tipo
def adicionar_trecho(serie: SerieLeitura, inicio: datetime, janela: timedelta, erro: bool) -> None:
    tipo = "erro" if erro else "sem_leitura"
    fim = inicio + janela

    if serie.trechos and serie.trechos[-1].tipo == tipo and serie.trechos[-1].fim == inicio:
        serie.trechos[-1].fim = fim
        return
    serie.trechos.append(TrechoLeitura(inicio=inicio, fim=fim, tipo=tipo))


# sem leitura curtinho e so o esp atrasando, erro aparece sempre.
# erros separados so por um buraco curto viram um trecho so
def limpar_trechos(serie: SerieLeitura) -> None:
    trechos = []
    for trecho in serie.trechos:
        if trecho.tipo == "sem_leitura" and trecho.fim - trecho.inicio <= SEM_LEITURA_MINIMO:
            continue

        anterior = trechos[-1] if trechos else None
        if anterior and anterior.tipo == trecho.tipo == "erro" and trecho.inicio - anterior.fim <= SEM_LEITURA_MINIMO:
            anterior.fim = trecho.fim
        else:
            trechos.append(trecho)
    serie.trechos = trechos


# liga abre um intervalo, desliga fecha. o q tava ligado antes do inicio comeca no inicio,
# o q ainda ta ligado vai ate o fim
def intervalos_ligado(registros, inicio: datetime, fim: datetime) -> dict[int, list[IntervaloLigado]]:
    intervalos: dict[int, list[IntervaloLigado]] = {}
    ligou_em: dict[int, datetime] = {}

    for registro in registros:
        tipo = int(registro.values["tipo"])
        tempo = registro.get_time()

        if registro.get_value() and tipo not in ligou_em:
            ligou_em[tipo] = tempo
        elif not registro.get_value() and tipo in ligou_em:
            adicionar_intervalo(intervalos, tipo, ligou_em.pop(tipo), tempo, inicio, fim)

    for tipo, tempo in ligou_em.items():
        adicionar_intervalo(intervalos, tipo, tempo, fim, inicio, fim)
    return intervalos


# corta no periodo pedido, o q ficou todo fora nem entra
def adicionar_intervalo(intervalos: dict[int, list[IntervaloLigado]], tipo: int, ligou: datetime, desligou: datetime,
    inicio: datetime, fim: datetime) -> None:
    if desligou <= inicio or ligou >= fim:
        return
    if tipo not in intervalos:
        intervalos[tipo] = []
    intervalos[tipo].append(IntervaloLigado(inicio=max(ligou, inicio), fim=min(desligou, fim)))


# tela principal manda so os minutos, o historico manda inicio e fim do calendario
def resolver_periodo(minutos: int, inicio: datetime | None, fim: datetime | None) -> tuple[datetime, datetime]:
    if inicio is None or fim is None:
        agora = datetime.now(UTC)
        return agora - timedelta(minutes=minutos), agora

    if fim <= inicio:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "O fim do período tem que ser depois do início")
    if fim - inicio > PERIODO_MAXIMO:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "As leituras ficam guardadas por 30 dias")
    return inicio, fim


# junta os pontos do influx por tipo de modulo e por nome da leitura.
# no historico tipo sem modulo conectado aparece msm assim, como removido
async def listar_modulos(db: AsyncSession, dispositivo: Dispositivo, inicio: datetime, fim: datetime,
    agrupamento: str, historico: bool) -> list[ModuloIotRead]:
    series: dict[int, dict[str, SerieLeitura]] = {}
    leituras = LeituraRepository()
    janela = calcular_janela(inicio, fim, agrupamento)
    registros = await leituras.listar_do_dispositivo(dispositivo.mac, inicio, fim, janela, condicao_valida_flux(), deslocamento_fuso())

    # a ultima janela ainda ta acontecendo, vazia nela n e desligado
    janela_atual = datetime.now(UTC) - timedelta(seconds=janela)

    # (tipo, nome, comeco da janela) q teve leitura fora da faixa
    janelas_com_erro = set()
    for registro in registros:
        if registro.values["result"] == "erros":
            janelas_com_erro.add((registro.values["tipo"], registro.values["nome"], registro.get_time()))

    for registro in registros:
        resultado = registro.values["result"]
        if resultado == "erros":
            continue

        serie = serie_do_registro(series, registro)
        valor = registro.get_value()

        if resultado == "pontos" and valor is None and registro.get_time() > janela_atual:
            continue
        if resultado == "pontos" and valor is None:
            erro = (registro.values["tipo"], serie.nome, registro.get_time()) in janelas_com_erro
            adicionar_trecho(serie, registro.get_time(), timedelta(seconds=janela), erro)
        elif resultado == "pontos":
            serie.pontos.append(PontoLeitura(tempo=registro.get_time(), valor=valor))
        elif resultado == "minimo":
            serie.minimo = valor
        elif resultado == "media":
            serie.media = valor
        elif resultado == "maximo":
            serie.maximo = valor

    for registro in await leituras.ultimas_do_dispositivo(dispositivo.mac, inicio, fim):
        serie = serie_do_registro(series, registro)
        serie.atual = PontoLeitura(tempo=registro.get_time(), valor=registro.get_value())
        serie.atual_erro = not leitura_valida(serie.nome, serie.atual.valor)

    for series_do_tipo in series.values():
        for serie in series_do_tipo.values():
            limpar_trechos(serie)

    ligados = intervalos_ligado(await leituras.listar_rele(dispositivo.mac, inicio, fim), inicio, fim)

    # conectados agora, com o rele de cada um
    modulos = []
    tipos_conectados = set()
    for modulo in await DispositivoRepository(db).listar_modulos(dispositivo.id):
        tipos_conectados.add(modulo.tipo)
        series_do_modulo = list(series.get(modulo.tipo, {}).values())
        modulos.append(ModuloIotRead(serial=modulo.serial, tipo=modulo.tipo, series=series_do_modulo, ligado=modulo.ligado,
            periodos_ligado=ligados.get(modulo.tipo, [])))

    # tela ao vivo so mostra o q ta conectado, o resto e coisa do historico
    if not historico:
        return modulos

    for tipo, series_do_tipo in series.items():
        if tipo not in tipos_conectados:
            modulos.append(ModuloIotRead(serial=None, tipo=tipo, series=list(series_do_tipo.values()), removido=True,
                periodos_ligado=ligados.get(tipo, [])))

    # msm ordem da tela ao vivo, q vem do banco por tipo
    modulos.sort(key=lambda modulo: modulo.tipo)
    return modulos


# o esp manda pro modulo e o estado novo volta pelo topico modulos
async def enviar_comando(db: AsyncSession, dispositivo: Dispositivo, serial: str, comando: ComandoModulo) -> None:
    modulo = await DispositivoRepository(db).buscar_modulo(serial)

    if modulo is None or modulo.id_dispositivo != dispositivo.id:
        raise NotFoundException("Módulo não encontrado")

    if modulo.ligado is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Módulo não aceita comando")

    # qos 0 e sem fila, offline o comando se perderia
    if dispositivo.estado != EstadoDispositivo.online:
        raise HTTPException(status.HTTP_409_CONFLICT, "Dispositivo offline")

    mqtt.publish(f"camus/dispositivos/{dispositivo.mac}/comandos", ComandoPayload(serial=serial, acao=comando.acao))
