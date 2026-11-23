from unittest.mock import AsyncMock

from fastcrud.exceptions.http_exceptions import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
)
from polyfactory.factories.pydantic_factory import ModelFactory

from app.domains.progresso import service
from app.domains.progresso.schema import (
    ConclusaoRead,
    ConteudoAlunoRead,
    ResultadoQuizRead,
    TrilhaAlunoRead,
)


def fake(schema):
    return ModelFactory.create_factory(schema).build()


def trocar(monkeypatch, nome, valor=None, erro=None):
    mock = AsyncMock(return_value=valor, side_effect=erro)
    monkeypatch.setattr(service, nome, mock)
    return mock


async def test_listar_trilhas(client, db, usuario_logado, monkeypatch):
    trocar(monkeypatch, "listar_trilhas", [])
    resposta = await client.get("/progresso/trilhas")
    assert resposta.status_code == 200
    assert resposta.json() == []


async def test_buscar_trilha(client, db, usuario_logado, monkeypatch):
    trocar(monkeypatch, "buscar_trilha", fake(TrilhaAlunoRead))
    resposta = await client.get("/progresso/trilhas/1")
    assert resposta.status_code == 200
