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
