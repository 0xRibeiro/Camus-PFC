from app.domains.usuario.model import RoleUsuario


async def test_criar_conquista_aluno_e_barrado(client, db, usuario_logado):
    usuario_logado.role = RoleUsuario.aluno
    resposta = await client.post("/conquistas", json={})
    assert resposta.status_code == 403


async def test_editar_conquista_aluno_e_barrado(client, db, usuario_logado):
    usuario_logado.role = RoleUsuario.aluno
    resposta = await client.patch("/conquistas/1", json={})
    assert resposta.status_code == 403


async def test_apagar_conquista_aluno_e_barrado(client, db, usuario_logado):
    usuario_logado.role = RoleUsuario.aluno
    resposta = await client.delete("/conquistas/1")
    assert resposta.status_code == 403


async def test_criar_conquista_admin_sem_corpo(client, db, usuario_logado):
    usuario_logado.role = RoleUsuario.admin
    resposta = await client.post("/conquistas", json={})
    assert resposta.status_code == 422
