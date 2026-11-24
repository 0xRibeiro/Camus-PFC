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


async def test_entrar_com_convite_sem_corpo(client, db, usuario_logado):
    resposta = await client.post("/aquarios/entrar", json={})
    assert resposta.status_code == 422


async def test_conectar_dispositivo_sem_corpo(client, db, usuario_logado):
    resposta = await client.post("/aquarios/1/dispositivo", json={})
    assert resposta.status_code == 422


async def test_desconectar_dispositivo(client, db, usuario_logado, monkeypatch):
    trocar(monkeypatch, "desconectar_dispositivo")
    resposta = await client.delete("/aquarios/1/dispositivo")
    assert resposta.status_code == 204


async def test_desconectar_dispositivo_sem_ser_dono(client, db, usuario_logado, monkeypatch):
    trocar(monkeypatch, "desconectar_dispositivo", erro=ForbiddenException("só o dono"))
    resposta = await client.delete("/aquarios/1/dispositivo")
    assert resposta.status_code == 403


async def test_listar_modulos_usa_valores_padrao(client, db, usuario_logado, monkeypatch):
    mock = trocar(monkeypatch, "listar_modulos", [])
    resposta = await client.get("/aquarios/1/modulos")
    assert resposta.status_code == 200
    assert mock.call_args.args[3] == 60
    assert mock.call_args.args[6] == "auto"


async def test_listar_modulos_minutos_zero(client, db, usuario_logado):
    resposta = await client.get("/aquarios/1/modulos?minutos=0")
    assert resposta.status_code == 422


async def test_listar_modulos_minutos_acima_do_limite(client, db, usuario_logado):
    resposta = await client.get("/aquarios/1/modulos?minutos=43201")
    assert resposta.status_code == 422


async def test_listar_modulos_agrupamento_invalido(client, db, usuario_logado):
    resposta = await client.get("/aquarios/1/modulos?agrupamento=semana")
    assert resposta.status_code == 422


async def test_listar_modulos_aquario_inexistente(client, db, usuario_logado, monkeypatch):
    trocar(monkeypatch, "listar_modulos", erro=NotFoundException("sem aquário"))
    resposta = await client.get("/aquarios/99/modulos")
    assert resposta.status_code == 404


async def test_comandar_modulo_sem_corpo(client, db, usuario_logado):
    resposta = await client.post("/aquarios/1/modulos/abc123/comando", json={})
    assert resposta.status_code == 422


async def test_gerar_convite(client, db, usuario_logado, monkeypatch):
    trocar(monkeypatch, "gerar_convite", fake(ConviteAquarioRead))
    resposta = await client.post("/aquarios/1/convites")
    assert resposta.status_code == 201


async def test_gerar_convite_sem_ser_dono(client, db, usuario_logado, monkeypatch):
    trocar(monkeypatch, "gerar_convite", erro=ForbiddenException("só o dono"))
    resposta = await client.post("/aquarios/1/convites")
    assert resposta.status_code == 403


async def test_listar_membros(client, db, usuario_logado, monkeypatch):
    trocar(monkeypatch, "listar_membros", [])
    resposta = await client.get("/aquarios/1/membros")
    assert resposta.status_code == 200
