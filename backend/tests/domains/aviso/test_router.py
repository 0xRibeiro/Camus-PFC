from unittest.mock import AsyncMock

from fastcrud.exceptions.http_exceptions import NotFoundException
from polyfactory.factories.pydantic_factory import ModelFactory

from app.domains.aviso import service
from app.domains.aviso.schema import AvisoRead


def fake(schema):
    return ModelFactory.create_factory(schema).build()


def trocar(monkeypatch, nome, valor=None, erro=None):
    mock = AsyncMock(return_value=valor, side_effect=erro)
    monkeypatch.setattr(service, nome, mock)
    return mock


async def test_listar_avisos_vazio(client, db, usuario_logado, monkeypatch):
    trocar(monkeypatch, "listar_avisos", [])
    resposta = await client.get("/avisos")
    assert resposta.status_code == 200
    assert resposta.json() == []
