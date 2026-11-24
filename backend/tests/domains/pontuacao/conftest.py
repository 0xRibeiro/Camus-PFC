from unittest.mock import AsyncMock, Mock

import pytest

from app.domains.pontuacao import service


@pytest.fixture
def repo(monkeypatch):
    repo_fake = Mock()
    for nome in (
        "somar_xp",
        "contar_na_frente",
        "somar_por_dia",
        "listar_ranking",
        "listar_ranking_grupo",
        "listar_do_usuario",
        "listar_titulos_conteudos",
        "listar_titulos_minigames",
    ):
        setattr(repo_fake, nome, AsyncMock())
    monkeypatch.setattr(service, "PontuacaoRepository", Mock(return_value=repo_fake))
    return repo_fake
