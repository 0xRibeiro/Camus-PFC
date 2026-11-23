from unittest.mock import AsyncMock

from fastcrud.exceptions.http_exceptions import ForbiddenException, NotFoundException
from polyfactory.factories.pydantic_factory import ModelFactory

from app.domains.grupo import service
from app.domains.grupo.schema import ConviteRead, GrupoRead


def fake(schema):
    return ModelFactory.create_factory(schema).build()


def grupo_read():
    return ModelFactory.create_factory(GrupoRead).build(suspenso_ate=None)


def trocar(monkeypatch, nome, valor=None, erro=None):
    mock = AsyncMock(return_value=valor, side_effect=erro)
    monkeypatch.setattr(service, nome, mock)
    return mock


async def test_criar_grupo(client, db, usuario_logado, monkeypatch):
    trocar(monkeypatch, "criar_grupo", grupo_read())
    resposta = await client.post("/grupos", json={"nome": "Turma A"})
    assert resposta.status_code == 201


async def test_criar_grupo_sem_nome(client, db, usuario_logado):
    resposta = await client.post("/grupos", json={})
    assert resposta.status_code == 422


async def test_criar_grupo_sem_permissao(client, db, usuario_logado, monkeypatch):
    trocar(monkeypatch, "criar_grupo", erro=ForbiddenException("só aluno"))
    resposta = await client.post("/grupos", json={"nome": "Turma A"})
    assert resposta.status_code == 403


async def test_listar_grupos(client, db, usuario_logado, monkeypatch):
    trocar(monkeypatch, "listar_grupos", [])
    resposta = await client.get("/grupos")
    assert resposta.status_code == 200
    assert resposta.json() == []


async def test_entrar_no_grupo(client, db, usuario_logado, monkeypatch):
    trocar(monkeypatch, "entrar_grupo", grupo_read())
    resposta = await client.post("/grupos/entrar", json={"convite": "123456"})
    assert resposta.status_code == 200
