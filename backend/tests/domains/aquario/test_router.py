from unittest.mock import AsyncMock

from fastcrud.exceptions.http_exceptions import ForbiddenException, NotFoundException
from polyfactory.factories.pydantic_factory import ModelFactory

from app.domains.aquario import service
from app.domains.aquario.schema import AquarioRead, ConviteAquarioRead


def fake(schema):
    return ModelFactory.create_factory(schema).build()


def trocar(monkeypatch, nome, valor=None, erro=None):
    mock = AsyncMock(return_value=valor, side_effect=erro)
    monkeypatch.setattr(service, nome, mock)
    return mock


async def test_listar_aquarios(client, db, usuario_logado, monkeypatch):
    trocar(monkeypatch, "listar_aquarios", [])
    resposta = await client.get("/aquarios")
    assert resposta.status_code == 200
    assert resposta.json() == []


async def test_listar_aquarios_usa_o_usuario_logado(client, db, usuario_logado, monkeypatch):
    mock = trocar(monkeypatch, "listar_aquarios", [])
    await client.get("/aquarios")
    assert mock.call_args.args[1] == usuario_logado.id


async def test_criar_aquario_sem_corpo(client, db, usuario_logado):
    resposta = await client.post("/aquarios", json={})
    assert resposta.status_code == 422


async def test_entrar_com_codigo_sem_corpo(client, db, usuario_logado):
    resposta = await client.post("/aquarios/entrar-com-codigo", json={})
    assert resposta.status_code == 422
