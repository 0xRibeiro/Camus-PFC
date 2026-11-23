from types import SimpleNamespace
from unittest.mock import AsyncMock

from fastcrud.exceptions.http_exceptions import ForbiddenException, NotFoundException
from polyfactory.factories.pydantic_factory import ModelFactory

from app.domains.denuncia import service
from app.domains.denuncia.schema import DenunciaRead
from app.domains.grupo import service as grupo_service
from app.domains.usuario.model import RoleUsuario
from app.main import app

DENUNCIA = {"motivo": "informacao_incorreta", "descricao": "o conteudo esta com erro"}


def fake(schema):
    return ModelFactory.create_factory(schema).build()


def trocar(monkeypatch, modulo, nome, valor=None, erro=None):
    mock = AsyncMock(return_value=valor, side_effect=erro)
    monkeypatch.setattr(modulo, nome, mock)
    return mock


def entrar_no_grupo():
    app.dependency_overrides[grupo_service.grupo_membro] = lambda: SimpleNamespace(id=1)


async def test_listar_denuncias_aluno_e_barrado(client, db, usuario_logado):
    usuario_logado.role = RoleUsuario.aluno
    resposta = await client.get("/admin/denuncias")
    assert resposta.status_code == 403


async def test_listar_denuncias_admin(client, db, usuario_logado, monkeypatch):
    usuario_logado.role = RoleUsuario.admin
    trocar(monkeypatch, service, "listar_denuncias", [])
    resposta = await client.get("/admin/denuncias")
    assert resposta.status_code == 200
    assert resposta.json() == []


async def test_listar_denuncias_filtra_por_status(client, db, usuario_logado, monkeypatch):
    usuario_logado.role = RoleUsuario.admin
    mock = trocar(monkeypatch, service, "listar_denuncias", [])
    resposta = await client.get("/admin/denuncias?status=pendente")
    assert resposta.status_code == 200
    assert mock.call_args.args[1] == "pendente"


async def test_listar_denuncias_status_invalido(client, db, usuario_logado):
    usuario_logado.role = RoleUsuario.admin
    resposta = await client.get("/admin/denuncias?status=qualquer")
    assert resposta.status_code == 422
