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


async def test_xp_por_dia_usa_7_dias_por_padrao(client, db, usuario_logado, monkeypatch):
    mock = trocar(monkeypatch, "meu_xp_por_dia", [])
    resposta = await client.get("/pontuacao/xp/dias")
    assert resposta.status_code == 200
    assert mock.call_args.args[2] == 7


async def test_xp_por_dia_aceita_outro_periodo(client, db, usuario_logado, monkeypatch):
    mock = trocar(monkeypatch, "meu_xp_por_dia", [])
    resposta = await client.get("/pontuacao/xp/dias?dias=30")
    assert resposta.status_code == 200
    assert mock.call_args.args[2] == 30


async def test_xp_por_dia_zero_dias(client, db, usuario_logado):
    resposta = await client.get("/pontuacao/xp/dias?dias=0")
    assert resposta.status_code == 422


async def test_xp_por_dia_passou_do_limite(client, db, usuario_logado):
    resposta = await client.get("/pontuacao/xp/dias?dias=91")
    assert resposta.status_code == 422


async def test_ranking(client, db, usuario_logado, monkeypatch):
    trocar(monkeypatch, "ranking", [])
    resposta = await client.get("/pontuacao/ranking")
    assert resposta.status_code == 200
    assert resposta.json() == []


async def test_extrato(client, db, usuario_logado, monkeypatch):
    trocar(monkeypatch, "meu_extrato", [])
    resposta = await client.get("/pontuacao/extrato")
    assert resposta.status_code == 200
    assert resposta.json() == []
