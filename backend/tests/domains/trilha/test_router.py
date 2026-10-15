from app.domains.usuario.model import RoleUsuario
from tests.domains.trilha.factories import TrilhaCreateFactory


# sem o usuario_logado
async def test_criar_trilha_sem_login(client):
    # manda sem token e com payload valido
    resposta = await client.post(
        "/trilhas",
        json=TrilhaCreateFactory.build().model_dump(mode="json"),
    )

    # o HTTPBearer barra sem token
    assert resposta.status_code == 401


async def test_criar_trilha_aluno(client, usuario_logado):
    # escolhe a role da geracao na factory
    usuario_logado.role = RoleUsuario.aluno

    resposta = await client.post(
        "/trilhas",
        json=TrilhaCreateFactory.build().model_dump(mode="json"),
    )

    # ta logado mas n tem permissao
    assert resposta.status_code == 403
    assert resposta.json()["detail"] == "acesso negado"


# teste com user author
async def test_criar_trilha_author(client, usuario_logado, db):
    usuario_logado.role = RoleUsuario.author

    # por usar fatscrud precisa escrever o refresh fake para metodos q criam
    # e tem dados preenchidos pelo BD apos o commit no BD se n vem null
    async def refresh_fake(trilha):
        trilha.id = 1
        trilha.is_active = False

    # troca o refresh da sessao falsa pela nossa funcao
    db.refresh = refresh_fake

    resposta = await client.post(
        "/trilhas",
        json=TrilhaCreateFactory.build().model_dump(mode="json"),
    )

    assert resposta.status_code == 200
    # confere q foi msm pro banco
    db.commit.assert_called_once()
