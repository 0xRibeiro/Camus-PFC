import asyncio
import uuid
from typing import Any

from pydantic import BaseModel

from app.core.mqtt import mqtt

# dynamic security do mosquitto, o backend entra como admin
TOPICO = "$CONTROL/dynamic-security/v1"

PAPEL_DISPOSITIVO = "dispositivo"
PAPEL_BACKEND = "backend"

# correlationData -> resposta esperando
pendentes: dict[str, asyncio.Future] = {}


class ComandosControle(BaseModel):
    commands: list[dict[str, Any]]


class RespostaControle(BaseModel):
    responses: list[dict[str, Any]]


class ErroDynsec(Exception):
    pass


def enviar(comandos: list[dict[str, Any]]) -> None:
    mqtt.publish(TOPICO, ComandosControle(commands=comandos))


# manda e espera a resposta do broker
async def executar(comandos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    correlacao = uuid.uuid4().hex
    for comando in comandos:
        comando["correlationData"] = correlacao

    futuro = asyncio.get_running_loop().create_future()
    pendentes[correlacao] = futuro
    enviar(comandos)

    try:
        return await asyncio.wait_for(futuro, timeout=5)
    finally:
        pendentes.pop(correlacao, None)


@mqtt.subscribe(f"{TOPICO}/response")
async def ao_resposta(resposta: RespostaControle, topic: str):
    if not resposta.responses:
        return

    correlacao = resposta.responses[0].get("correlationData", "")
    futuro = pendentes.get(correlacao)

    if futuro is not None and not futuro.done():
        futuro.set_result(resposta.responses)


# roda a cada conexao, "ja existe" e esperado
@mqtt.on_connect()
def preparar_papeis(client, flags, rc, properties):
    enviar([
        {
            "command": "createRole",
            "rolename": PAPEL_DISPOSITIVO,
            "acls": [
                {"acltype": "publishClientSend", "topic": "camus/dispositivos/%u/#", "allow": True},
                {"acltype": "subscribePattern", "topic": "camus/dispositivos/%u/#", "allow": True},
            ],
        },
        {
            "command": "createRole",
            "rolename": PAPEL_BACKEND,
            "acls": [
                {"acltype": "publishClientSend", "topic": "camus/dispositivos/#", "allow": True},
                {"acltype": "subscribePattern", "topic": "camus/dispositivos/#", "allow": True},
            ],
        },
        {"command": "addClientRole", "username": "admin", "rolename": PAPEL_BACKEND},
        {"command": "deleteClient", "username": "democlient"},
    ])


# cria ou troca a senha, apagar antes deixa um comando so pros dois casos
async def cadastrar_dispositivo(mac: str, senha: str) -> None:
    respostas = await executar([
        {"command": "deleteClient", "username": mac},
        {
            "command": "createClient",
            "username": mac,
            "password": senha,
            "roles": [{"rolename": PAPEL_DISPOSITIVO}],
        },
    ])

    criacao = respostas[-1]
    if "error" in criacao:
        raise ErroDynsec(criacao["error"])


async def remover_dispositivo(mac: str) -> None:
    await executar([{"command": "deleteClient", "username": mac}])
