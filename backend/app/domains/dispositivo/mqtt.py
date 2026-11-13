from app.core.database import async_session_maker
from app.core.mqtt import mqtt
from app.domains.dispositivo.schema import (
    LeituraModulo,
    ListaModulos,
    PedidoVinculo,
    StatusDispositivo,
)
from app.domains.dispositivo.service import (
    desvincular_todos,
    gerar_codigo,
    gravar_leitura,
    registrar_modulos,
    registrar_status,
)


# + pega o status de qualquer esp
@mqtt.subscribe("camus/dispositivos/+/status")
async def ao_status(status: StatusDispositivo, topic: str):
    # camus/dispositivos/<mac>/status
    mac = topic.split("/")[2]

    async with async_session_maker() as db:
        await registrar_status(db, mac, status)


@mqtt.subscribe("camus/dispositivos/+/vinculo/pedido")
async def ao_pedido_vinculo(pedido: PedidoVinculo, topic: str):
    mac = topic.split("/")[2]

    if pedido.acao == "gerar_codigo":
        resposta = await gerar_codigo(mac)
        mqtt.publish(f"camus/dispositivos/{mac}/vinculo/resposta", resposta)
    elif pedido.acao == "desvincular_todos":
        async with async_session_maker() as db:
            resposta = await desvincular_todos(db, mac)
        mqtt.publish(f"camus/dispositivos/{mac}/vinculo/resposta", resposta)


@mqtt.subscribe("camus/dispositivos/+/modulos")
async def ao_modulos(lista: ListaModulos, topic: str):
    mac = topic.split("/")[2]

    async with async_session_maker() as db:
        await registrar_modulos(db, mac, lista)


@mqtt.subscribe("camus/dispositivos/+/leituras")
async def ao_leitura(leitura: LeituraModulo, topic: str):
    mac = topic.split("/")[2]
    await gravar_leitura(mac, leitura)
