from unittest.mock import AsyncMock

from fastcrud.exceptions.http_exceptions import NotFoundException
from polyfactory.factories.pydantic_factory import ModelFactory

from app.domains.grupo.schema import GrupoRead
from app.domains.moderacao import service
from app.domains.usuario.model import RoleUsuario

MOTIVO = {"motivo": "violou as regras da plataforma"}


def grupo_read():
    return ModelFactory.create_factory(GrupoRead).build(suspenso_ate=None)


def trocar(monkeypatch, nome, valor=None, erro=None):
    mock = AsyncMock(return_value=valor, side_effect=erro)
    monkeypatch.setattr(service, nome, mock)
    return mock


async def test_suspender_grupo_aluno_e_barrado(client, db, usuario_logado):
    usuario_logado.role = RoleUsuario.aluno
    resposta = await client.post("/admin/grupos/1/suspensao", json={})
    assert resposta.status_code == 403


async def test_excluir_grupo_aluno_e_barrado(client, db, usuario_logado):
    usuario_logado.role = RoleUsuario.aluno
    resposta = await client.request("DELETE", "/admin/grupos/1", json=MOTIVO)
    assert resposta.status_code == 403


async def test_excluir_conteudo_aluno_e_barrado(client, db, usuario_logado):
    usuario_logado.role = RoleUsuario.aluno
    resposta = await client.request("DELETE", "/admin/grupos/1/conteudos/2", json=MOTIVO)
    assert resposta.status_code == 403


async def test_suspender_grupo_prazo_invalido(client, db, usuario_logado):
    usuario_logado.role = RoleUsuario.admin
    resposta = await client.post(
        "/admin/grupos/1/suspensao", json={"dias": 7, **MOTIVO}
    )
    assert resposta.status_code == 422


async def test_suspender_grupo_motivo_curto(client, db, usuario_logado):
    usuario_logado.role = RoleUsuario.admin
    resposta = await client.post(
        "/admin/grupos/1/suspensao", json={"dias": 14, "motivo": "abc"}
    )
    assert resposta.status_code == 422


async def test_suspender_grupo_sucesso(client, db, usuario_logado, monkeypatch):
    usuario_logado.role = RoleUsuario.admin
    trocar(monkeypatch, "suspender_grupo", grupo_read())
    resposta = await client.post(
        "/admin/grupos/1/suspensao", json={"dias": 30, **MOTIVO}
    )
    assert resposta.status_code == 200
