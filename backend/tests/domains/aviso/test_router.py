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


async def test_listar_avisos_com_itens(client, db, usuario_logado, monkeypatch):
    trocar(monkeypatch, "listar_avisos", [fake(AvisoRead), fake(AvisoRead)])
    resposta = await client.get("/avisos")
    assert resposta.status_code == 200
    assert len(resposta.json()) == 2


async def test_marcar_como_lido(client, db, usuario_logado, monkeypatch):
    trocar(monkeypatch, "marcar_como_lido", fake(AvisoRead))
    resposta = await client.patch("/avisos/1/lido")
    assert resposta.status_code == 200


async def test_marcar_como_lido_inexistente(client, db, usuario_logado, monkeypatch):
    trocar(monkeypatch, "marcar_como_lido", erro=NotFoundException("sem aviso"))
    resposta = await client.patch("/avisos/99/lido")
    assert resposta.status_code == 404
