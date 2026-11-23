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


async def test_buscar_trilha_inexistente(client, db, usuario_logado, monkeypatch):
    trocar(monkeypatch, "buscar_trilha", erro=NotFoundException("sem trilha"))
    resposta = await client.get("/progresso/trilhas/99")
    assert resposta.status_code == 404


async def test_buscar_trilha_id_invalido(client, db, usuario_logado):
    resposta = await client.get("/progresso/trilhas/abc")
    assert resposta.status_code == 422


async def test_buscar_conteudo(client, db, usuario_logado, monkeypatch):
    trocar(monkeypatch, "buscar_conteudo", fake(ConteudoAlunoRead))
    resposta = await client.get("/progresso/conteudos/1")
    assert resposta.status_code == 200


async def test_buscar_conteudo_bloqueado(client, db, usuario_logado, monkeypatch):
    trocar(monkeypatch, "buscar_conteudo", erro=ForbiddenException("bloqueado"))
    resposta = await client.get("/progresso/conteudos/2")
    assert resposta.status_code == 403


async def test_concluir_conteudo(client, db, usuario_logado, monkeypatch):
    trocar(monkeypatch, "concluir_conteudo", fake(ConclusaoRead))
    resposta = await client.post("/progresso/conteudos/1/concluir")
    assert resposta.status_code == 200


async def test_concluir_conteudo_de_quiz(client, db, usuario_logado, monkeypatch):
    trocar(monkeypatch, "concluir_conteudo", erro=BadRequestException("é quiz"))
    resposta = await client.post("/progresso/conteudos/1/concluir")
    assert resposta.status_code == 400


async def test_responder_quiz(client, db, usuario_logado, monkeypatch):
    trocar(monkeypatch, "responder_quiz", fake(ResultadoQuizRead))
    resposta = await client.post(
        "/progresso/conteudos/1/responder", json={"respostas": {"1": 2}}
    )
    assert resposta.status_code == 200
