from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from app.domains.progresso import service


@pytest.fixture
def repo(monkeypatch):
    repo_fake = Mock()
    repo_fake.grupo_id = None
    repo_fake.db = SimpleNamespace(info={})
    for nome in (
        "buscar_trilha",
        "buscar_modulo",
        "buscar_conteudo",
        "listar_modulos",
        "listar_conteudos",
        "listar_conclusoes",
        "listar_questoes",
        "listar_alternativas",
        "bloquear_progresso",
        "confirmar",
    ):
        setattr(repo_fake, nome, AsyncMock())
    repo_fake.listar_conclusoes.return_value = []
    monkeypatch.setattr(service, "ProgressoRepository", Mock(return_value=repo_fake))
    return repo_fake
