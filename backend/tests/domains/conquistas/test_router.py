from app.domains.usuario.model import RoleUsuario


async def test_criar_conquista_aluno_e_barrado(client, db, usuario_logado):
    usuario_logado.role = RoleUsuario.aluno
    resposta = await client.post("/conquistas", json={})
    assert resposta.status_code == 403
