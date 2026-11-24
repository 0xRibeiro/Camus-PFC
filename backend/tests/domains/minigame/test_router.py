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
