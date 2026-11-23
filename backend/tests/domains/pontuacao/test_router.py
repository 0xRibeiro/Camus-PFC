from unittest.mock import AsyncMock

from polyfactory.factories.pydantic_factory import ModelFactory

from app.domains.pontuacao import service
from app.domains.pontuacao.schema import XpRead


def fake(schema):
    return ModelFactory.create_factory(schema).build()


def trocar(monkeypatch, nome, valor=None):
    mock = AsyncMock(return_value=valor)
    monkeypatch.setattr(service, nome, mock)
    return mock


async def test_meu_xp(client, db, usuario_logado, monkeypatch):
    trocar(monkeypatch, "meu_xp", fake(XpRead))
    resposta = await client.get("/pontuacao/xp")
    assert resposta.status_code == 200
