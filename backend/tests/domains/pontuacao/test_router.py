from unittest.mock import AsyncMock

from polyfactory.factories.pydantic_factory import ModelFactory

from app.domains.pontuacao import service
from app.domains.pontuacao.schema import XpRead
from datetime import datetime
from app.domains.usuario.model import RoleUsuario
from tests.domains.usuario.factories import UsuarioFactory


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


async def test_xp_do_aluno_mostra_a_posicao(client, db, repo, usuario_logado):
    usuario_logado.role = RoleUsuario.aluno
    repo.somar_xp.return_value = 120
    repo.contar_na_frente.return_value = 2
    resposta = await client.get("/pontuacao/xp")
    assert resposta.status_code == 200
    assert resposta.json()["xp_total"] == 120
    assert resposta.json()["posicao"] == 3


async def test_xp_zerado_fica_sem_posicao(client, db, repo, usuario_logado):
    usuario_logado.role = RoleUsuario.aluno
    repo.somar_xp.return_value = 0
    resposta = await client.get("/pontuacao/xp")
    assert resposta.json()["posicao"] is None
    repo.contar_na_frente.assert_not_awaited()


async def test_xp_de_admin_nao_tem_posicao(client, db, repo, usuario_logado):
    usuario_logado.role = RoleUsuario.admin
    repo.somar_xp.return_value = 50
    resposta = await client.get("/pontuacao/xp")
    assert resposta.json()["xp_total"] == 50
    assert resposta.json()["posicao"] is None


async def test_xp_no_grupo_usa_o_escopo_do_grupo(client, db, repo, usuario_logado):
    usuario_logado.role = RoleUsuario.aluno
    db.info["grupo_id"] = 4
    repo.somar_xp.return_value = 30
    resposta = await client.get("/pontuacao/xp")
    assert resposta.json()["posicao"] is None
    assert repo.somar_xp.call_args.args[1] == 4


async def test_xp_por_dia_preenche_os_dias_vazios_com_zero(client, db, repo, usuario_logado):
    repo.somar_por_dia.return_value = {}
    resposta = await client.get("/pontuacao/xp/dias?dias=3")
    assert resposta.status_code == 200
    assert [item["pontos"] for item in resposta.json()] == [0, 0, 0]
