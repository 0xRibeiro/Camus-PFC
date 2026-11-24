from unittest.mock import AsyncMock

from fastcrud.exceptions.http_exceptions import NotFoundException
from polyfactory.factories.pydantic_factory import ModelFactory

from app.domains.minigame import service
from app.domains.minigame.schema import (
    PalpiteInput,
    RespostaInput,
    ResultadoMaisOuMenosRead,
    ResultadoRead,
    RodadaMaisOuMenosRead,
    RodadaRead,
)


def fake(schema):
    return ModelFactory.create_factory(schema).build()


def trocar(monkeypatch, nome, valor=None, erro=None):
    mock = AsyncMock(return_value=valor, side_effect=erro)
    monkeypatch.setattr(service, nome, mock)
    return mock


async def test_meus_recordes(client, db, usuario_logado, monkeypatch):
    trocar(monkeypatch, "meus_recordes", [])
    resposta = await client.get("/minigames/recordes")
    assert resposta.status_code == 200
    assert resposta.json() == []


async def test_nova_rodada(client, db, usuario_logado, monkeypatch):
    trocar(monkeypatch, "nova_rodada", fake(RodadaRead))
    resposta = await client.post("/minigames/quem-e-esse-peixe/rodadas")
    assert resposta.status_code == 201


async def test_nova_rodada_sem_peixes_cadastrados(client, db, usuario_logado, monkeypatch):
    trocar(monkeypatch, "nova_rodada", erro=NotFoundException("sem peixes"))
    resposta = await client.post("/minigames/quem-e-esse-peixe/rodadas")
    assert resposta.status_code == 404


async def test_responder_sem_corpo(client, db, usuario_logado):
    resposta = await client.post("/minigames/quem-e-esse-peixe/rodadas/1/resposta", json={})
    assert resposta.status_code == 422


async def test_responder_sucesso(client, db, usuario_logado, monkeypatch):
    trocar(monkeypatch, "responder", fake(ResultadoRead))
    corpo = fake(RespostaInput).model_dump(mode="json")
    resposta = await client.post("/minigames/quem-e-esse-peixe/rodadas/1/resposta", json=corpo)
    assert resposta.status_code == 200
