from datetime import datetime, timezone

import pytest

from app.domains.usuario.avatares import AVATARES
from app.domains.usuario.model import RoleUsuario
from tests.domains.usuario.factories import (
    UsuarioCreateFactory,
    UsuarioFactory,
    UsuarioLoginFactory,
)


async def test_login_email_inexistente(client, repo):
    repo.buscar_por_email.return_value = None

    resposta = await client.post(
        "/auth/login",
        json=UsuarioLoginFactory.build().model_dump(mode="json"),
    )

    assert resposta.status_code == 401
    assert resposta.json()["detail"] == "credenciais inválidas"


async def test_login_senha_errada(client, repo):
    repo.buscar_por_email.return_value = UsuarioFactory.build()

    resposta = await client.post(
        "/auth/login",
        json=UsuarioLoginFactory.build(password="senhaerrada").model_dump(mode="json"),
    )

    assert resposta.status_code == 401
    assert resposta.json()["detail"] == "credenciais inválidas"


async def test_login_sucesso(client, repo, redis):
    repo.buscar_por_email.return_value = UsuarioFactory.build()

    resposta = await client.post(
        "/auth/login",
        json=UsuarioLoginFactory.build().model_dump(mode="json"),
    )

    assert resposta.status_code == 200
    assert "access_token" in resposta.json()
    assert "refresh_token" in resposta.json()
    redis.set.assert_called_once()


async def test_register_username_existente(client, repo):
    repo.buscar_por_username.return_value = UsuarioFactory.build()

    resposta = await client.post(
        "/auth/register",
        json=UsuarioCreateFactory.build().model_dump(mode="json"),
    )

    assert resposta.status_code == 422
    assert resposta.json()["detail"] == "username já existe"
    repo.salvar.assert_not_called()


async def test_register_email_existente(client, repo):
    repo.buscar_por_username.return_value = None
    repo.buscar_por_email.return_value = UsuarioFactory.build()

    resposta = await client.post(
        "/auth/register",
        json=UsuarioCreateFactory.build().model_dump(mode="json"),
    )

    assert resposta.status_code == 422
    assert resposta.json()["detail"] == "email já existe"
    repo.salvar.assert_not_called()


async def test_register_sem_aceitar_termos(client, repo):
    resposta = await client.post(
        "/auth/register",
        json=UsuarioCreateFactory.build(
            factory_use_construct=True,
            aceitou_termos=False,
        ).model_dump(mode="json"),
    )

    assert resposta.status_code == 422
    repo.salvar.assert_not_called()


async def test_register_sucesso(client, repo):
    repo.buscar_por_username.return_value = None
    repo.buscar_por_email.return_value = None
    repo.salvar.return_value = UsuarioFactory.build()

    resposta = await client.post(
        "/auth/register",
        json=UsuarioCreateFactory.build().model_dump(mode="json"),
    )

    assert resposta.status_code == 201
    assert "password" not in resposta.json()
    assert "hashed_password" not in resposta.json()


###### soft delete (LGPD: exclusão de conta sem apagar a linha do banco)


async def test_deletar_me_faz_soft_delete(client, repo, usuario_logado):
    usuario_logado.role = RoleUsuario.aluno
    resposta = await client.delete("/usuarios/me")

    assert resposta.status_code == 204
    assert usuario_logado.deletado_em is not None
    assert usuario_logado.is_active is False
    assert usuario_logado.username == f"usuario-excluido-{usuario_logado.id}"
    assert (
        usuario_logado.email == f"usuario-excluido-{usuario_logado.id}@removido.camus"
    )
    repo.salvar.assert_awaited_once_with(usuario_logado)


async def test_deletar_me_e_idempotente(client, repo, usuario_logado):
    usuario_logado.role = RoleUsuario.aluno
    usuario_logado.deletado_em = datetime.now(timezone.utc)

    resposta = await client.delete("/usuarios/me")

    assert resposta.status_code == 204, (resposta.text, usuario_logado.role)


async def test_admin_deletar_usuario_faz_soft_delete(client, repo, usuario_logado):
    usuario_logado.role = RoleUsuario.admin
    alvo = UsuarioFactory.build()
    alvo.role = RoleUsuario.aluno
    repo.buscar.return_value = alvo

    resposta = await client.delete(f"/admin/usuarios/{alvo.id}")

    assert resposta.status_code == 204
    assert alvo.deletado_em is not None
    assert alvo.is_active is False
    repo.salvar.assert_awaited_once_with(alvo)


###### perfil (avatar e cor de fundo)


async def test_listar_avatares(client):
    resposta = await client.get("/avatares")

    assert resposta.status_code == 200
    assert resposta.json() == list(AVATARES)


async def test_atualizar_avatar_e_cor(client, repo, usuario_logado):
    repo.salvar.return_value = usuario_logado
    avatar = AVATARES[1]

    resposta = await client.patch(
        "/usuarios/me",
        json={"avatar": avatar, "cor_fundo": "#ff8800"},
    )

    assert resposta.status_code == 200
    assert usuario_logado.avatar == avatar
    assert usuario_logado.cor_fundo == "#FF8800"  # o schema normaliza pra maiuscula
    assert resposta.json()["avatar"] == avatar
    repo.salvar.assert_awaited_once_with(usuario_logado)


async def test_atualizar_avatar_invalido(client, repo, usuario_logado):
    resposta = await client.patch("/usuarios/me", json={"avatar": "qualquer-coisa"})

    assert resposta.status_code == 422
    repo.salvar.assert_not_called()


@pytest.mark.parametrize("cor", ["vermelho", "#fff", "#GGGGGG", "ff8800"])
async def test_atualizar_cor_invalida(client, repo, usuario_logado, cor):
    resposta = await client.patch("/usuarios/me", json={"cor_fundo": cor})

    assert resposta.status_code == 422
    repo.salvar.assert_not_called()


async def test_atualizar_username(client, repo, usuario_logado):
    repo.buscar_por_username.return_value = None
    repo.salvar.return_value = usuario_logado

    resposta = await client.patch("/usuarios/me", json={"username": "novo-nome"})

    assert resposta.status_code == 200
    assert usuario_logado.username == "novo-nome"


async def test_atualizar_username_existente(client, repo, usuario_logado):
    repo.buscar_por_username.return_value = UsuarioFactory.build()

    resposta = await client.patch("/usuarios/me", json={"username": "ja-existe"})

    assert resposta.status_code == 422
    assert resposta.json()["detail"] == "username já existe"
    repo.salvar.assert_not_called()



async def test_deletar_me_admin_e_barrado(client, repo, usuario_logado):
    usuario_logado.role = RoleUsuario.admin

    resposta = await client.delete("/usuarios/me")

    assert resposta.status_code == 403
    assert usuario_logado.deletado_em is None
    repo.salvar.assert_not_called()