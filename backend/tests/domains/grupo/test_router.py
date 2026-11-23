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


async def test_entrar_no_grupo_sem_convite(client, db, usuario_logado):
    resposta = await client.post("/grupos/entrar", json={})
    assert resposta.status_code == 422


async def test_entrar_no_grupo_convite_expirado(client, db, usuario_logado, monkeypatch):
    trocar(monkeypatch, "entrar_grupo", erro=NotFoundException("expirou"))
    resposta = await client.post("/grupos/entrar", json={"convite": "000000"})
    assert resposta.status_code == 404


async def test_buscar_grupo(client, db, usuario_logado, monkeypatch):
    trocar(monkeypatch, "buscar_grupo", grupo_read())
    resposta = await client.get("/grupos/1")
    assert resposta.status_code == 200


async def test_buscar_grupo_inexistente(client, db, usuario_logado, monkeypatch):
    trocar(monkeypatch, "buscar_grupo", erro=NotFoundException("sem grupo"))
    resposta = await client.get("/grupos/99")
    assert resposta.status_code == 404


async def test_buscar_grupo_de_outro(client, db, usuario_logado, monkeypatch):
    trocar(monkeypatch, "buscar_grupo", erro=ForbiddenException("não participa"))
    resposta = await client.get("/grupos/1")
    assert resposta.status_code == 403


async def test_gerar_convite(client, db, usuario_logado, monkeypatch):
    trocar(monkeypatch, "gerar_convite", fake(ConviteRead))
    resposta = await client.post("/grupos/1/convites")
    assert resposta.status_code == 201


async def test_gerar_convite_sem_ser_dono(client, db, usuario_logado, monkeypatch):
    trocar(monkeypatch, "gerar_convite", erro=ForbiddenException("só o dono"))
    resposta = await client.post("/grupos/1/convites")
    assert resposta.status_code == 403


async def test_listar_membros(client, db, usuario_logado, monkeypatch):
    trocar(monkeypatch, "listar_membros", [])
    resposta = await client.get("/grupos/1/membros")
    assert resposta.status_code == 200


async def test_sair_do_grupo(client, db, usuario_logado, monkeypatch):
    trocar(monkeypatch, "sair_grupo")
    resposta = await client.delete("/grupos/1/membros/me")
    assert resposta.status_code == 204


async def test_dono_nao_pode_sair_do_grupo(client, db, usuario_logado, monkeypatch):
    trocar(monkeypatch, "sair_grupo", erro=ForbiddenException("dono exclui"))
    resposta = await client.delete("/grupos/1/membros/me")
    assert resposta.status_code == 403


async def test_remover_membro(client, db, usuario_logado, monkeypatch):
    trocar(monkeypatch, "remover_membro")
    resposta = await client.delete("/grupos/1/membros/5")
    assert resposta.status_code == 204


async def test_remover_membro_que_nao_participa(client, db, usuario_logado, monkeypatch):
    trocar(monkeypatch, "remover_membro", erro=NotFoundException("não participa"))
    resposta = await client.delete("/grupos/1/membros/5")
    assert resposta.status_code == 404
